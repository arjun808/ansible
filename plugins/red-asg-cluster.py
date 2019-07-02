#!/usr/bin/python
import subprocess
import boto3
import json
import datetime
import time
import telnetlib
import os
import pwd
import grp

def retry_command(x):
 for attempt in range(10):
    try:
      output = execute_command(x)
      return output
    except ValueError as error:
      dateprint("Attempt {} : Retrying execution in 3 seconds after receiving {}".format(attempt, error))
      time.sleep(3)
    else:
      dateprint("Execution of {} failed".format(x))
      quit()

def retry_sdk(x):
 for attempt in range(10):
    try:
      output = x
      return output
    except ValueError as error:
      dateprint("Attempt {} : Retrying execution in 3 seconds after receiving {}".format(attempt, error))
      time.sleep(3)
    else:
      dateprint("Execution of {} failed".format(x))
      quit()

def execute_command(command):
   process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   output, error = process.communicate()
   if (command.find('credstash') != -1) and (error.find('couldn\'t be found') != -1):
       output = False
       return output
   if process.returncode != 0 and process.returncode != 6:
    dateprint("FATAL ERROR: Command execution failed. Command: ' {0} ' returned {1} value with error message {2}".format(command, process.returncode, error))
    raise ValueError("FAIL")
   else:
    return output

def dateprint(statement):
    date = datetime.datetime.now()
    print date, statement

dateprint("Starting redis clustering")
dateprint("setting env variables")
ENV = '/etc/profile.d/rmq-redis.sh'
REDIS_SERVICE_NAME = 'ct-redis'

redis_env = "export REDIS_SERVICE_NAME={0}".format(REDIS_SERVICE_NAME)
with open(ENV, 'a') as file:
     file.write(redis_env)
     file.write('\n')

def select_leader():
    dateprint("retrieving variables for instance and region")
    instance_id = retry_command("curl -s 169.254.169.254/latest/meta-data/instance-id")
    region = json.loads(retry_command("curl -s 169.254.169.254/latest/dynamic/instance-identity/document"))['region']
    region_env = "export REGION={0}".format(region)
    with open(ENV, 'a') as file:
         file.write(region_env)
         file.write('\n')
    redis_pass = retry_command("credstash -r {0} get cloudops.{0}.redis_pass".format(region))
    dateprint("retrieving autoscaling instance details")
    client = boto3.client('autoscaling')
    asg_name = retry_sdk(client.describe_auto_scaling_instances(InstanceIds=[instance_id,],))['AutoScalingInstances'][0]['AutoScalingGroupName']
    id_list_json = retry_sdk(client.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name,],))['AutoScalingGroups'][0]['Instances']
    asg_id_list = []
    for item in id_list_json:
        asg_id_list.append(item['InstanceId'])

    dateprint("generating IP list for instances in autoscaling")
    asg_ip_list = []
    client = boto3.client('ec2')
    for item in asg_id_list:
     asg_ip_list.append(retry_sdk(client.describe_instances(InstanceIds=[item,],)['Reservations'][0]['Instances'][0]['PrivateIpAddress']))
    asg_ip_list.sort()

    dateprint("Checking credstash for redis leader")
    credstash_check = retry_command("credstash -r {0} get cloudops.{0}.redis_leader".format(region))
    credstash_check = "1.0.1.0"
    if not credstash_check:
        dateprint("No Redis leader found in credstash")
        redis_leader = asg_ip_list[0]
        dateprint("Setting {} as the Redis leader in credstash and as environment variable".format(redis_leader))
        #credstash_set = retry_command("credstash -r {0} put test.{0}.redis_leader {1}".format(region, redis_leader))
        redis_leader_set = "export REDIS_LEADER={0}".format(redis_leader)
        with open(ENV, 'a') as file:
          file.write(redis_leader_set)
          file.write('\n')

    else:
        redis_leader = credstash_check
        dateprint("{} found as Redis leader; checking if Redis leader is up".format(redis_leader))
        try:
            session = telnetlib.Telnet(redis_leader, 22, 10)
            x = session.read_until("SSH")
            dateprint("Redis leader "+redis_leader+" is up")
        except Exception as err:
            dateprint("Redis leader "+ redis_leader +" is not available. Received error: {}".format(err))
            dateprint("Waiting 10 seconds for sentinel re-election")
            #time.sleep(10)
            dateprint("Checking instances to find redis leader")
            connection_retry = True
            connection_retry_count = 0
            no_master_count = 0
            while connection_retry:
                for item in asg_ip_list:
                    pong = retry_command("redis-cli -p 6379 -h {0} -a {1} PING".format(item, redis_pass))
                    if (pong.find("PONG") == -1):
                        dateprint("Unable to reach redis on {}. Skipping....".format(item))
                        connection_retry_count += 1
                    else:
                        role = retry_command("redis-cli -p 6379 -h {0} -a {1} info".format(item, redis_pass))
                        if (role.find('role:master') == -1):
                             dateprint("{} is not the sentinel master".format(item))
                             no_master_count +=1
                        else:
                             dateprint("{} is the sentinel master".format(item))
                             dateprint("Setting {} as the Redis leader in credstash and as environment variable".format(item))
                             redis_leader = item
                             redis_leader_set = "export REDIS_LEADER={0}".format(redis_leader)
                             with open(ENV, 'a') as file:
                               file.write(redis_leader_set)
                               file.write('\n')
                             connection_retry = False
                             break
                    if connection_retry_count >15:
                        dateprint("Unable to connect to any redis servers. Please check configuration.")
                        quit()
                    if no_master_count > len(asg_ip_list):
                        dateprint("Unable to find a master")



    local_ip = retry_command("curl -s 169.254.169.254/latest/meta-data/local-ipv4")
    if local_ip == redis_leader:
        dateprint("Setting up role as master")
        redis_role = "MASTER"
    else:
        dateprint("Setting up role as slave")
        redis_role = "SLAVE"

    redis_role_set = "export REDIS_ROLE={0}".format(redis_role)
    with open(ENV, 'a') as file:
      file.write(redis_role_set)
      file.write('\n')


def configure_redis():
  dateprint("exporting configuration files")
  template_dir = '/etc/consul.d/templates'
  consul_template = retry_command("/usr/local/bin/consul-template -once \
     -template {0}/redis.sh.ctmpl:/etc/consul.d/scripts/redis.sh \
     -template {0}/redis.conf.ctmpl:/etc/redis.conf \
     -template {0}/redis-sentinel.conf.ctmpl:/etc/redis-sentinel.conf \
     -template {0}/checks-redis.json.ctmpl:/etc/sensu/conf.d/checks-redis.json".format(template_dir))
  restart_sensu_client = retry_command("systemctl restart sensu-client")
  uid = pwd.getpwnam("redis").pw_uid
  gid = grp.getgrnam("redis").gr_gid
  for file in os.listdir("/etc"):
    if file.startswith("redis"):
        redis_ownership = os.chown("/etc/"+file,uid,gid)
        redis_chmod = os.chmod("/etc/"+file, 0600)
  if os.getenv("REDIS_ROLE") == "SLAVE":
       dateprint("Detected as slave, waiting for few seconds to let master available")
       time.sleep(10)

select_leader()
configure_redis()
