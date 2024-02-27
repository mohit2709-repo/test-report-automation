import os, sys, json
import boto3
import time
import paramiko


# Importing Functions
functions_dir = os.path.join(os.path.dirname(__file__), '..','functions')
print ('Current Path')
sys.path.append(functions_dir)
from common.general import *

#--------------------------------------------------------------------
# Importing EC2 Config file
#--------------------------------------------------------------------
#ec2_config_filePath = os.path.join(os.path.dirname(__file__), 'config','basic_ec2.config')
ec2_config_filePath = os.path.join(os.path.dirname(__file__), 'config','JMeter_Machine_Creation.config')
#ec2_config_filePath = os.path.join(os.path.dirname(__file__), 'config','LR_Machine_Creation.config')
with open(ec2_config_filePath, 'r') as ec2_config_file:
    ec2_configJson = json.load(ec2_config_file)
    AWS_profile = ec2_configJson.get("lt_perf_test", {}).get("AWS_PROFILE")
    AWS_region = ec2_configJson.get("lt_perf_test", {}).get("AWS_REGION")
    aws_profileNregion_message = f"AWS_Profile: {AWS_profile}; AWS_Region: {AWS_region}"
    #print(f"{aws_profileNregion_message}")
    tag_cost_centre = ec2_configJson.get("lt_perf_test", {}).get("Cost_Centre")
    tag_AppID = ec2_configJson.get("lt_perf_test", {}).get("AppID")
    tag_environment = ec2_configJson.get("lt_perf_test", {}).get("Environment")
    aws_costCenter_message = f"Cost Centre: {tag_cost_centre}; AppID: {tag_AppID}; Environment: {tag_environment}"
    #print(f"{aws_costCenter_message}")
    key_PairName = ec2_configJson.get("lt_perf_test", {}).get("Key_PairName")
    aws_key_PairName_message = f"Key Pair Name: {key_PairName}"
    #print(f"{aws_key_PairName_message}")
    default_ec2_instanceType = ec2_configJson.get("lt_perf_test", {}).get("ec2_settings",{}).get("instance_type")
    default_ec2_ami = ec2_configJson.get("lt_perf_test", {}).get("ec2_settings",{}).get("ami_id")
    aws_ec2_basic_Specs_message = f"Instance Type: {default_ec2_instanceType}; AMI: {default_ec2_ami}"
    #print(f"{aws_ec2_basic_Specs_message}")
    ec2_ebs_volumeSize = ec2_configJson.get("lt_perf_test", {}).get("ec2_settings",{}).get("ebs_settings",{}).get("volume_size")
    ec2_ebs_volumeType = ec2_configJson.get("lt_perf_test", {}).get("ec2_settings",{}).get("ebs_settings",{}).get("volume_type")
    ec2_ebs_iops = ec2_configJson.get("lt_perf_test", {}).get("ec2_settings",{}).get("ebs_settings",{}).get("iops")
    ec2_ebs_device = ec2_configJson.get("lt_perf_test", {}).get("ec2_settings",{}).get("ebs_settings",{}).get("device")
    aws_ec2_ebs_Specs_message = f"EBS Volume Size: {ec2_ebs_volumeSize}; EBS Volume Type: {ec2_ebs_volumeType}; EBS IOPS: {ec2_ebs_iops}; EBS Device: {ec2_ebs_device}"
    #print(f"{aws_ec2_ebs_Specs_message}")
    ec2_secuirty_groupId = ec2_configJson.get("lt_perf_test", {}).get("ec2_settings",{}).get("security_settings",{}).get("security_group_id")
    ec2_secuirty_vpc = ec2_configJson.get("lt_perf_test", {}).get("ec2_settings",{}).get("security_settings",{}).get("vpc_id")
    ec2_secuirty_subnetId = ec2_configJson.get("lt_perf_test", {}).get("ec2_settings",{}).get("security_settings",{}).get("subnet_id")
    ec2_secuirty_iam_instance_profile_arn = ec2_configJson.get("lt_perf_test", {}).get("ec2_settings",{}).get("security_settings",{}).get("iam_instance_profile_arn")
    aws_ec2_security_Specs_message = f"Security Group: {ec2_secuirty_groupId}; VPC: {ec2_secuirty_vpc}; Subnet: {ec2_secuirty_subnetId}; IAM Instance Profile ARN: {ec2_secuirty_iam_instance_profile_arn}"
    #print(f"{aws_ec2_security_Specs_message}")
    print(f"{aws_profileNregion_message}\n {aws_costCenter_message}\n {aws_ec2_basic_Specs_message}\n {aws_ec2_ebs_Specs_message}\n {aws_ec2_security_Specs_message}\n ")
#--------------------------------------------------------------------

# Specify tags for the instance
#def create_instance_tags(tag_cost_centre, tag_AppID, tag_environment, applicationTrack, applicationName, perfEngineerEmail):
def create_instance_tags(applicationTrack, applicationName, perfEngineerEmail, ec2_name):
    if ec2_name == 0:
        ec2_name = applicationName
    tags = [
        {'Key': 't_cost_centre', 'Value': tag_cost_centre},
        {'Key': 't_AppID', 'Value': tag_AppID},
        {'Key': 't_environment', 'Value': tag_environment},
        {'Key': 'customer', 'Value': applicationTrack},
        {'Key': 't_AppName', 'Value': applicationName},
        {'Key': 't_responsible_individuals', 'Value': perfEngineerEmail},
        {'Key': 't_owner_individual', 'Value': perfEngineerEmail},
        {'Key': 'Name', 'Value': ec2_name}
    ]
    return tags

def create_ec2(session, ec2_instanceType, ami, perfEngineerKeyName, tags, logFileName):
    ec2_client = session.client('ec2')
    if ami == 0:
        selected_ami = default_ec2_ami
    else:
        selected_ami = ami
    if ec2_instanceType == 0:
        selected_ec2_instanceType = default_ec2_instanceType
    else:
        selected_ec2_instanceType = ec2_instanceType
    if key_PairName != 0:
        perfEngineerKeyName = key_PairName
    else:
        perfEngineerKeyName = perfEngineerKeyName
        
    # Launch the EC2 instance
    response = ec2_client.run_instances(
        ImageId=selected_ami,    
        InstanceType=selected_ec2_instanceType,
        KeyName=perfEngineerKeyName,
        MinCount=1,MaxCount=1,
        #SubnetId=subnet_id,
        #SecurityGroupIds=[security_group_id],
        BlockDeviceMappings=[
            {
                'DeviceName': ec2_ebs_device,
                'Ebs': {'VolumeSize': ec2_ebs_volumeSize,'VolumeType': ec2_ebs_volumeType}
            }
        ],
        TagSpecifications=[{'ResourceType': 'instance','Tags': tags}
        ],
        NetworkInterfaces=[{'SubnetId': ec2_secuirty_subnetId, 'DeviceIndex': 0,'AssociatePublicIpAddress': True, 'Groups': [ec2_secuirty_groupId],'Ipv6Addresses': [] }],
        IamInstanceProfile={'Arn': ec2_secuirty_iam_instance_profile_arn}
    )
    ec2_instanceId = response['Instances'][0]['InstanceId'] # Get the instance ID
    ec2_launch_message = f"Launched EC2 instance with ID: {ec2_instanceId}, Full EC2 Details: {response}"
    logging(ec2_launch_message, logFileName)
    time.sleep(5)

    # Wait until the instance is running
    while True:
        response = ec2_client.describe_instances(InstanceIds=[ec2_instanceId])  
        instance_state = response['Reservations'][0]['Instances'][0]['State']['Name']
        if instance_state == 'running':
            ec2_detail_justStartedRunningStatus = f"EC2 instance {ec2_instanceId} is now running."
            logging(ec2_detail_justStartedRunningStatus, logFileName)
            break
        ec2_detail_waitingToRunStatus = f"Instance state: {instance_state}. Waiting for the instance to be running..."
        logging(ec2_detail_waitingToRunStatus, logFileName)
        time.sleep(10)  # Wait for 10 seconds before checking again

    # Get the latest details of the running instance
    response = ec2_client.describe_instances(InstanceIds=[ec2_instanceId])
    instance_details = response['Reservations'][0]['Instances'][0]
    public_dns_name = instance_details['PublicDnsName']
    public_ip_address = instance_details['PublicIpAddress']
    ec2_details_message = f"EC2 Instance details: {instance_details}"
    #logging(ec2_detail_inRunningStatus, logFileName)
    return ec2_instanceId, public_dns_name, public_ip_address

def get_ssh_command(perfEngineerKeyName, ip_address, logFileName):
    ssh_command = f"ssh -i {perfEngineerKeyName}.pem ec2-user@{ip_address}"
    ssh_command_message = f"SSH Connection String: {ssh_command}"
    logging(ssh_command_message, logFileName)
    return ssh_command

def run_ssh_command(hostname, ec2_username, private_key, commands):
    ssh = paramiko.SSHClient()     # Create an SSH client instance
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # Automatically add the server's host key
    #private_key_Wpath = private_key
    private_key_Wpath = os.path.join(os.path.dirname(__file__), private_key)
    try:
        #private_key = paramiko.RSAKey.from_private_key_file(private_key_Wpath) # Load the private key for authentication       
        ssh.connect(hostname, username=ec2_username, key_filename=private_key_Wpath) # Connect to the remote EC2 instance
        # Execute the provided shell commands
        for command in commands:
            stdin, stdout, stderr = ssh.exec_command(command)
            print(f"Command: {command}")
            print(f"Output:\n{stdout.read().decode('utf-8')}")
            print(f"Error:\n{stderr.read().decode('utf-8')}")
    except paramiko.AuthenticationException:
        print("Authentication failed. Make sure your private key and credentials are correct.")
    except paramiko.SSHException as ssh_ex:
        print(f"SSH connection failed: {ssh_ex}")
    finally:
        ssh.close()


## Example usage
#hostname = public_dns_name
#username = 'ec2-user'
##private_key_path = key_name+'.pem'
#private_key_path = key_file
#commands = ['ls', 'df -h', 'uptime']
#
#run_ssh_command(hostname, username, private_key_path, commands)
#