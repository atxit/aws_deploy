#AWS deployment CLI python code
I created this python code to demonstrate cloud automation using CLI. The code begins by asking if the user wants to use the demo defaults or enter their own configuration setting. If the user selects to enter their own settings, they will be steps through a set of questions. If using demo mode, these are prepopulated (defaults expanded later). Once instructed to proceed, the python code begins the process of building a new VPC, subnet, default gateway, adding a default route, SSH keys and finally, the EC2 (Linux Redhat) instance. Once the EC2 instance is online, python is instructed to SSH to the EC2 instance.  
Note: A valid AWS account is required to successful run this python code. The user MUST be logged into the CLI interface before running the python code. The python code will not prompt the user to enter their user credentials.  

#Supported versions:
Python 2.7.15 (tested)

#Libraries and Modules
netmiko, getpass, os, netaddr, ipaddress, time, termcolor, sys

#How to use
All three System Arguments must be supplied otherwise the python code will generate an error. 

Python 2.7 aws_deploy_ec2_with_vpc.py
1)	User is prompted to selected demo mode (prepopulated configuration) or to enter manually. 
2)	If demo mode is selected, all configuration is displayed as a summary 
3)	If the user manually entered the configuration, all configuration is displayed as a summary
    Note: Demo mode always deploys an EC2 instance. This is a choice when a user manually enters configuration. 
4)	The user will be prompted to start the build process. If not accepted, python will stop. 
5)	Once the build process starts, results of each step will be displayed. 
6)	The EC2 instance will take around 2 minutes to build and start. 
7)	Once the EC2 instance is online, python will SSH to the Linux server. 
