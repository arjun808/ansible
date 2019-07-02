#!/usr/bin/python
import subprocess
import os
import signal
import shutil
from ansible.module_utils.basic import *
import time
from artifactory import ArtifactoryPath
dt = time.strftime("%Y%m%d%H%M%S")


def is_running(name):
  process = subprocess.Popen("ps -ef | grep -i " + name + " | grep -v grep", shell=True, stdout=subprocess.PIPE)
  exists = process.communicate()[0]

  if exists:
    return True
  else:
    return False

def demolish():
  proc_id = subprocess.Popen(['pidof java'], shell=True, stdout=subprocess.PIPE).communicate()[0]
  clean_pid = proc_id.rstrip('\n')
  int_pid = int(clean_pid)
  os.kill(int_pid, signal.SIGTERM)
  return int_pid

def filepath_exists(directory):
  if os.path.exists(directory):
   return True
  else:
   return False

def path_create(directory):
   os.makedirs(directory)
   reply = " Path {0} has been created".format(directory)
   return reply

def move(src, dest):
  shutil.move(src, dest)
  return True

def timestamp(file):
  new_name = "{0}-".format(file)+dt
  os.rename(file, new_name)
  return True

def copy(src, dest):
  if filepath_exists(src):
     shutil.copy2(src, dest)
     result = "file has been copied"
  else:
     result = "file does not exist"
  return result
  
def delete(file):
   os.remove(file)
   return True

def main():
# creating AnsibleModule object with acceptable attributes
  module = AnsibleModule(
    argument_spec=dict(
    name=dict(required=True, type='str'),
    jar_version=dict(required=True, type='str'),
    environment=dict(required=True, type='str'),
    ),
    supports_check_mode=True
  )

# condition for check mode/dry run
  if module.check_mode:
    module.exit_json(changed=False)

# initialising the passed attributes as variables
  name = module.params['name']
  jar_version = module.params['jar_version']
  environment = module.params['environment']

# killing the microservice if it is running on the server
  
  if is_running(name):
    pid = demolish()
    time.sleep(2)
    if is_running(name):
      msg = "Program could not be stopped. Please check the host."
      module.fail_json(msg=msg)
    else:
      program_status = "Program '{0}' having PID '{1}' has been killed on this host.".format(name, pid)
  else:
      program_status = "Program '{0}' is not running on this host.".format(name)

# copying the properties file and timestamping the previous property file. Creating the property file path if it does not exist.

  property_dir = "/home/ngaurav/{0}/resources/".format(name)
  property_file = "/home/ngaurav/{0}/resources/application-{1}.properties".format(name, environment)
  property_src = "/root/test/application-{0}.properties".format(environment)

  if filepath_exists(property_file):
    timestamp(property_file)
    copy_reply = copy(property_src, property_file)
    property_file_status = "Property file has been timestamped. New property {0}.".format(copy_reply)
  elif filepath_exists(property_dir):
    file_copy_status = copy(property_src, property_file)
    property_file_status = "There exists no previous property file. {0} ".format(file_copy_status)
  else:
    path_create(property_dir)
    property_file_status = "File path has been created."

# deleting previous backup jar and creating the backup directory if it does not exist.
  
  backup_jar= "/dev/shm/eSource/Backup_Deployment/Artifacts/{0}-{1}.jar".format(name, jar_version)
  backup_dir = "/dev/shm/eSource/Backup_Deployment/Artifacts/"
  current_jar = "/dev/shm/eSource/Current_Deployment/Artifacts/{0}-{1}.jar".format(name, jar_version)
  current_dir = "/dev/shm/eSource/Current_Deployment/Artifacts/"
  
  if filepath_exists(backup_jar):
    delete(backup_jar)
    backup_jar_status = "Backup jar has been deleted."
  elif filepath_exists(backup_dir):
    backup_jar_status = "Backup directory exists but there is no backup jar yet."
  else:
    path_create(backup_dir)
    backup_jar_status = "Backup directory did not exist previously. It has been created."
	
# backing up the current jar to backup directory. Creating the current deployment directory if it does not exist.
  
  if filepath_exists(current_dir):
    copyjar_reply = copy(current_jar, backup_dir)
    current_jar_status = "The current jar {0} for backup".format(copyjar_reply)
  else:
    path_create(current_dir)
    current_jar_status = "The directory for current deployments did not exist. It has been created."
	
  if filepath_exists(current_jar):
    delete(current_jar)

#downloading the latest jar and moving it to the current deployment path
  path = ArtifactoryPath(
    "http://ec2-34-210-28-18.us-west-2.compute.amazonaws.com:8081/artifactory/libs-release-local/com/wlt/cel/{0}/{1}/{0}-{1}.jar".format(name, jar_version),
    auth=('admin', 'password'))
  with path.open() as fd:
    with open("{0}-{1}.jar".format(name, jar_version), "wb") as out:
        out.write(fd.read())
  here = "/root/module/{0}-{1}.jar".format(name, jar_version)
  move(here, current_dir)
  jar_download_status = " Downloaded latest jar."

#starting up jar and checking if it is running with backup steps in case new jar does not start
  delete_current_jar = '{0}{1}-{2}.jar'.format(current_dir, name, jar_version)
  p = subprocess.Popen('java -jar -Dspring.profiles.active={0} -Dspring.config.location={1} {2}{3}-{4}.jar'.format(environment, property_dir, current_dir, name, jar_version), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  
  if is_running(name):  
   running_jar_status = 'New jar has been started.'
  else:
    delete(delete_current_jar)
    move(backup_jar, current_dir)
    p = subprocess.Popen('java -jar -Dspring.profiles.active={0} -Dspring.config.location={1} {2}{3}-{4}.jar'.format(environment, property_dir, current_dir, name, jar_version), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if is_running(name):
      running_jar_status = "Failed jar has been removed. The backup jar has been started."
    else:
      running_jar_status = "Failed jar has been removed. The backup jar could not be started. Please check the host manually." 


  module.exit_json(program_status=program_status, property_file_status=property_file_status, backup_jar_status=backup_jar_status, current_jar_status=current_jar_status, jar_download_status=jar_download_status, running_jar_status=running_jar_status)

if __name__ == '__main__':
  main()
