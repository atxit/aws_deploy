#!/usr/bin/env python
from netmiko import ConnectHandler
from getpass import getpass
import os
import commands
import re
from netaddr import IPNetwork, IPAddress
import ipaddress
import time
from termcolor import colored
import sys

ip_address = "(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])"

def defaults():
	user_vpc_region = 'eu-west-2'
	user_cidr = '10.11.0.0/16'
	user_ip = '10.11.1.0/24'
	user_key = 'demo_key'
	user_vpc_name = 'demo_vpc'
	user_ec2 = True
	return user_cidr,user_ip,user_vpc_name,user_vpc_region,(user_ec2),user_key

def check_region(user_vpc_region):
	send_cli = 'aws ec2 describe-regions'
	results_json = commands.getoutput(send_cli)
	confirm = bool(re.search(user_vpc_region,results_json))
	if confirm == True:
		print('{} region has been found using the AWS catalogue'.format(user_vpc_region))
	if confirm == False:
		print('{} not found, stopping'.format(user_vpc_region))
	return confirm

def check_cidr(user_cidr):
	truth = False
	find_bs  = bool(re.search(r'/',user_cidr))
	ip_cidr,subnet = user_cidr.split('/', 1)
	ip_truth = bool(re.search(r'(^10.)',ip_cidr))
	subnet_truth = bool('16' <= subnet <= '28')
	if ip_truth and subnet_truth and find_bs == True:
		truth = True
	print('{} is acceptable'.format(user_cidr))
	return ((truth),ip_cidr)

def check_user_ip(user_ip,user_cidr):
	truth = False
	ip_add,subnet = user_ip.split('/', 1)
	truth = bool(IPAddress(ip_add) in IPNetwork(user_cidr))
	print('Network range {user_ip} resides within {user_cidr} range, acceptable'.format(user_ip=user_ip,user_cidr=user_cidr))
	return ((truth))

def check_vpc_name(vpc_name):
	truth = False
	find_space  = bool(re.search(r' +',user_vpc_name))
	if find_space != True:
		truth = True
	print('VPC name format is acceptable')
	return ((truth))

def check_user_key(user_key):
	truth = False
	find_space  = bool(re.search(r' +',user_vpc_name))
	if find_space != True:
		truth = True
	print('Key format is acceptable')
	return ((truth))

def information_collection():
	user_ec2 = False
	os.system('clear')
	print colored ("\n\t\tAWS Cloud Demo Python\n\n","red")
	default = raw_input("Use demo defaults or enter manually below? [y/n]:")
	if default == 'n':
		user_vpc_region = raw_input("\nEnter the region name that the new VPC will reside in [example:eu-west-2]\n:")
		user_cidr = raw_input("\nEnter the CIDR for the VPC\nThe CIDR range must be configured from /16 through /28\n[Example:10.1.0.0/16]\n:")
		user_ip = raw_input("\nEnter new ipv4 network subnet which will be bound to your VPC\nNote: The range must reside within {ip} or the subnet creation will fail\n:".format(ip=user_cidr))
		user_vpc_name = raw_input("\nEnter the name of the new VPC? (no spaces)\n:")
		user_key = raw_input("\nEnter a new SSH key name (no spaces)\n:")
		user_ec2 = raw_input("\nShall we create a new EC2 instances?\nDefault is [n]\n[y/n]:")
		os.system('clear')
		print colored('\n\t\t\tSummary of Build','red')
		print colored (('Deploying into {vpn_region}'.format(vpn_region=user_vpc_region)),'green')
		print('New VPC name is {vpc_name}'.format(vpc_name=user_vpc_name))
		print('New region name is {vpn_region}'.format(vpn_region=user_vpc_region))
		print('New CIDR block is {user_cidr}'.format(user_cidr=user_cidr))
		print('New network subnet block is {user_ip}'.format(user_ip=user_ip))
		if user_ec2 == 'y':
			print colored ('New VM instances will be created as part of this build','green')
			user_ec2 = True
		if user_ec2 == 'n':
			print colored ('No VM instances will be created as part of this build','red')
			user_ec2 = False
	else:
		user_cidr,user_ip,user_vpc_name,user_vpc_region,user_ec2,user_key = defaults()
		os.system('clear')
		print colored('\n\t\t\tSummary of Build\n','red')
		print('New VPC name is {vpc_name}'.format(vpc_name=user_vpc_name))
		print('New region name is {vpn_region}'.format(vpn_region=user_vpc_region))
		print('New CIDR block is {user_cidr}'.format(user_cidr=user_cidr))
		print('New network subnet block is {user_ip}'.format(user_ip=user_ip))
		print colored ('New VM instances will be created as part of this build','green')
	return(user_cidr,user_ip,user_vpc_name,user_vpc_region,user_ec2,user_key)

def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor

def proceed():
	print colored ('Proceed with build? default is yes ','red')
	proceed_yes = raw_input('[y/n]')
	if proceed_yes == '':
		proceed_yes = True
		spinner = spinning_cursor()
		for _ in range(50):
			sys.stdout.write(next(spinner))
			sys.stdout.flush()
			time.sleep(0.1)
			sys.stdout.write('\b')
	if proceed_yes == 'y':
		proceed_yes = True
		spinner = spinning_cursor()
		for _ in range(50):
			sys.stdout.write(next(spinner))
			sys.stdout.flush()
			time.sleep(0.1)
			sys.stdout.write('\b')
	if proceed_yes == 'n':
		print('Existing...')
		exit()
	return (proceed_yes)

def cleaner(result_input):
	result_input = result_input.replace('"','')
	result_input = result_input.replace("'",'')
	result_input = result_input.replace(',','')
	result_input = result_input.replace('}','')
	result_input = result_input.replace('{','')
	result_input = result_input.replace('[','')
	result_input = result_input.replace(']','')
	result_input = result_input.replace(': ',':')
	result_input = result_input.replace(' ','')
	return (result_input)

def tup_to_string(tup):
	stringed_tup = ''.join(tup)
	stringed_tup = cleaner(stringed_tup)
	return stringed_tup

#creation of new VPC

def create_vpc(user_cidr,user_vpc_region):
	create_vpc_now = ("""aws ec2 create-vpc \
	 --cidr-block {cidr} \
	 --region {region}""".format(cidr=user_cidr, region=user_vpc_region))
	print('sending {}'.format(create_vpc_now))
	results_json = commands.getoutput(create_vpc_now)
	results_json = cleaner(results_json)
	regex_name = 'vpc-[0-9a-f\s+-]+\n'
	results_json = re.findall(regex_name,results_json)
	results_json = [r.replace('\n','') for r in results_json]
	vpc_id = str(results_json)
	vpc_id = cleaner(vpc_id)
	print('VPC ID is {}'.format(vpc_id))
	return(vpc_id)

#adding name tag to new VPC

def name_vpc(user_vpc_name,user_vpc_region,vpc_id):
	create_vpc_name = ('aws ec2 create-tags \
	  --resources {vpc_id} \
	  --tags "Key=Name,Value={vpc_name}" \
	  --region {vpc_region}'.format(vpc_id=vpc_id,vpc_name=user_vpc_name,vpc_region=user_vpc_region))
	results_json = commands.getoutput(create_vpc_name)	

#creation of new subnet in eu-west-2a (availability-zone)

def create_subnet(user_ip,user_vpc_region,vpc_id):
	create_subnet = ('aws ec2 create-subnet \
	  --vpc-id {vpc_id} \
	  --cidr-block {subnet_ip} \
	  --availability-zone eu-west-2a \
	  --region {vpc_region}'.format(vpc_id=vpc_id,subnet_ip=user_ip,vpc_region=user_vpc_region))
	print('sending {}'.format(create_subnet))
	results_json = commands.getoutput(create_subnet)
	regex_name = 'subnet-[0-9a-f\s+-,]+'
	subnet_id = re.findall(regex_name,results_json)[0]
	print('\nSubnet created!\nsubnet ID is {subnet_id}'.format(subnet_id=subnet_id))
	return(subnet_id)

#creation of new default gateway. If one exist, this step is skipped. 

def create_gw(vpc_id):
	gateway_create = 'aws ec2 create-internet-gateway'
	gateway_query = ('aws ec2 describe-internet-gateways --filters "Name=attachment.vpc-id,Values={}"'.format(vpc_id))
	results_json = commands.getoutput(gateway_query)	
	if vpc_id in results_json:
		print ('found a valid internet gateway, not creating a new instance')
		regex_name = 'igw-[0-9a-f\s+-]+"\n'
		igw = re.findall(regex_name,results_json)[0]
		igw = [r.replace('\n','') for r in igw]
		igw = [r.replace('"','') for r in igw]
		igw = str(igw)
		igw = cleaner(igw)
		return(igw)
	else:
		print ("Creating a new Internet gateway, none found")
		create_json = commands.getoutput(gateway_create)	
		regex_name = 'igw-[0-9a-f\s+-]+"\n'
		igw = re.findall(regex_name,create_json)[0]
		igw = [r.replace('\n','') for r in igw]
		igw = [r.replace('"','') for r in igw]
		igw = str(igw)
		igw = cleaner(igw)
		attach_internet_gateway = ('aws ec2 attach-internet-gateway --internet-gateway-id {igw} --vpc-id {vpc_id}'.format(vpc_id=vpc_id,igw=igw))
		print('Our Internet Gateway ID is:{}'.format(igw))
		results_attach = commands.getoutput(attach_internet_gateway)
		return(results_attach,igw)

#creation of new default route

def default_route(igw,vpc_id):
	route_query = ('aws ec2 describe-route-tables --filters "Name=vpc-id,Values={}"'.format(vpc_id))
	results_json = commands.getoutput(route_query)	
	regex_name = 'rtb-[0-9a-f\s+-]+"\n'
	rtr = re.findall(regex_name,results_json)[0]
	rtr = [r.replace('\n','') for r in rtr]
	rtr = [r.replace('"','') for r in rtr]
	rtr = str(rtr)
	rtr = cleaner(rtr)
	igw = tup_to_string(igw)
	print('Route 0.0.0.0/0 has been added to AWS routing table id of {rtr}\n0.0.0.0\\0 is pointing towards {igw}'.format(rtr=rtr,igw=igw))
	attach_route = ('aws ec2 create-route --route-table-id {rtr} --destination-cidr-block 0.0.0.0/0 --gateway-id {igw}'.format(rtr=rtr,igw=igw))
	results_json = commands.getoutput(attach_route)
	return(results_json,rtr)

#creation of new security group

def create_security_group():
	attach_security = ('aws ec2 create-security-group --group-name demo-ic --description "Demo security group for IC environment" --vpc-id {vpc_id}'.format(vpc_id=vpc_id))
	results_json = commands.getoutput(attach_security)
	regex_name = 'sg-[0-9a-f\s+-]+"\n'
	sg = re.findall(regex_name,results_json)[0]
	sg = [r.replace('\n','') for r in sg]
	sg = [r.replace('"','') for r in sg]
	sg = str(sg)
	sg = cleaner(sg)
	attach_acl = ('aws ec2 authorize-security-group-ingress --group-id {sg} --protocol tcp --port 22 --cidr 0.0.0.0/0'.format(sg=sg))
	results_json = commands.getoutput(attach_acl)
	print('Security Group {sg} has been successful deployed into the VPC'.format(sg=sg))
	return (sg)

# queries AWS to see if there is already an active SSH key pair with the same name (as entered either using the demo setting or
#user override). If there is a key name match, python looks to see if there is a key with the same name residing within the local
#directory. If a match is found, the keys are examined. If this yields the same hash, they're used in the creation of the EC2 instance.
#If not, both the local and AWS keys (using the same name) are deleted. A new key pair is created, then installed on the local file system. 

def create_security_key(user_key):
	list_key= ('aws ec2 describe-key-pairs')
	result_aws = commands.getoutput(list_key)
	local_key = ('ls -l {}.pem'.format(user_key))
	result_local = commands.getoutput(local_key)
	key_local = False
	key_aws = False
	try:
		key_aws = re.findall(user_key,result_aws)[0]
		if user_key == key_aws:
			print('"{}" key has been found on AWS, will use existing, looking on the local file system'.format(user_key))
			key_aws = True
	except:
		print('{} was not found in AWS...'.format(user_key))
	try:
		key_local = re.findall(user_key,result_local)[0]
		if user_key == key_local:
			print('key has been found on local file system')
			key_local = True
	except:
		print('{} was not found on local file system...'.format(user_key))
	if key_local and key_aws == True:
		print ('identical key pair names found, comparing fingerprint values')
		aws_fp = ('aws ec2 describe-key-pairs --key-name "{}"'.format(user_key))
		local_fp = ('openssl pkcs8 -in {}.pem -nocrypt -topk8 -outform DER | openssl sha1 -c'.format(user_key))
		aws_key = commands.getoutput(aws_fp)
		aws_local = commands.getoutput(local_fp)
		aws_key = cleaner(aws_key)
		regex_name = 'KeyFingerprint:([0-9a-f:]+)\n'
		aws_key = re.findall(regex_name,aws_key)[0]
		aws_local = cleaner(aws_local)
		aws_local = aws_local.replace("(","")
		aws_local = aws_local.replace(")","")
		regex_name = 'stdin=([0-9a-f:]+)'
		aws_local = re.findall(regex_name,aws_local)[0]
		if aws_local == aws_key:
			print('key pair fingerprint match, about to move forward') 
		if aws_local != aws_key:
			print('key pair fingerprint do not match, must delete and recreate') 
			key_local = False
			key_aws = False
	if key_local == False or key_aws == False:
		os.system("rm -f {user_key}.pem".format(user_key=user_key))
		print('Removed existing local .pem file')
		delete_key = ('aws ec2 delete-key-pair --key-name {}'.format(user_key))
		attach_key = ('aws ec2 create-key-pair --key-name {user_key} --query "KeyMaterial" --output text > {user_key}.pem'.format(user_key=user_key))
		print('sending {}'.format(delete_key))
		print('sending {}'.format(attach_key))
		results_remove = commands.getoutput(delete_key)
		results_add = commands.getoutput(attach_key)
		os.system('chmod 400 {user_key}.pem'.format(user_key=user_key))

def build_ec2(subnet_id,sg,user_key):
	attach_ec2 = 'aws ec2 run-instances --image-id ami-7c1bfd1b \
	                         --subnet-id {subnet_id} \
	                         --security-group-ids {sg} \
	                         --count 1 \
	                         --instance-type t2.micro \
	                         --key-name {user_key} \
	                         --query "Instances[0].InstanceId" \
	                         --associate-public-ip-address'.format(subnet_id=subnet_id,sg=sg,user_key=user_key)
	results_json = commands.getoutput(attach_ec2)                        
	ec_id = cleaner(results_json)
	query_ec2 = ('aws ec2 describe-instances --instance-ids "{ec_id}" --query "Reservations[0].Instances[0].PublicIpAddress"'.format(ec_id=ec_id))
	print (query_ec2)
	results_json = commands.getoutput(query_ec2)   
	ip = cleaner(results_json)
	print('instances {} is starting now, will take up to two minutes'.format(ec_id))
	print('Public IP address is {}'.format(ip))
	return (ec_id,ip)

def query_status(ec_id,run):
	if run == False:
		init = ''
		ok = ''
		status = 'aws ec2 describe-instance-status --instance-ids "{id}"'.format(id=ec_id)
		result_input = commands.getoutput(status)
		init = bool(re.search(r'(initializing)',result_input))
		passed = bool(re.search(r'passed',result_input))
		if init == True:
			print('Still initializing')
			run = False
		if passed == True:
			print('{id} is up!'.format(id=ec_id))
			run = True
		return (run)

def connect_to_ec(user_key,ip):
	os.system("sed -i '/{ip}/d' ~/.ssh/known_hosts".format(ip=ip))
	os.system("clear")
	ssh_connect = ('ssh -o "StrictHostKeyChecking no" -i {user_key}.pem ec2-user@{ip}'.format(user_key=user_key,ip=ip))
	print ('sending:{}'.format(ssh_connect))
	os.system(ssh_connect)

user_cidr,user_ip,user_vpc_name,user_vpc_region,user_ec2,user_key = information_collection()
proceed_yes = proceed()
check_region_post = check_region(user_vpc_region)
check_cidr_post,ip_cidr = check_cidr(user_cidr)
check_user_ip_post = check_user_ip(user_ip,user_cidr)
check_vpc_name_post = check_vpc_name(user_vpc_name)
check_user_key_post = check_user_key(user_key)

if check_region_post == True and check_cidr_post == True and check_user_ip_post == True and check_vpc_name_post == True and check_user_key_post == True:
	print('Prestaging checks are acceptable, moving forward with build.\nUpdates will appear on screen')
else:
	print('Prestage validation failed, please check your settings')
	exit()

vpc_id = create_vpc(user_cidr,user_vpc_region)
name_vpc(user_vpc_name,user_vpc_region,vpc_id)
subnet_id = create_subnet(user_ip,user_vpc_region,vpc_id)
igw = create_gw(vpc_id)
rtr = default_route(igw,vpc_id)
sg = create_security_group()
create_security_key(user_key)

starttime = time.time()

if user_ec2 == True:
	ec_id,ip = build_ec2(subnet_id,sg,user_key)
	import time
	run = False
	while run == False:
		time.sleep(5.0 - ((time.time() - starttime) % 5.0))
		run = query_status(ec_id,run)
	connect_to_ec(user_key,ip)

if user_ec2 == False:
	print('Set to not run EC instance, existing')
	exit()

