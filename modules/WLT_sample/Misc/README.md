- SA_deployment_PDE:
    service:
	version:
	env:
	
----
	

#stop currently running service

#check if the property file directory exists
#if not, create it.

check if the property file exists
if it exists, it should append timestamp to it and copy new file from jenkins job
if not, copy the file from the jenkins job

check if backup directory exists
if not create

check if backup artifact exists
if present, remove

check if current deployment directory exists
if not create

copying the artifact to backup and delete from current

download latest artifact

start service

check if service is running
if success, mail
if not, rollback

---------

for rollback:

delete current artifact

copy backup artifact to current and delete from backup

start

check if service is running
email notification







-------------------------------------

jenkins: 
url: 2.253.249.170:8180/jenkins
username: admin
password: admin123

-------------------------------------

artifactory:
url: 2.253.226.156:8081/artifactory/libs-release-local/
username: admin
password: password

-----------------------------------------



