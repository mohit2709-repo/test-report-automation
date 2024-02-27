import os, sys, json
import boto3
import subprocess
import pandas as pd
from pathlib import Path

# Specify your AWS profile and region
awsProfile='--profile PCMPowerUser@510779331227'

# Importing Functions

cw_agent_linux_config_dir = os.path.join(os.path.dirname(__file__), 'linux')
cw_agent_linux_config_schemaFile = '\\amazon-cloudwatch-agent-schema.json'
cw_agent_linux_config_File = '\\amazon-cloudwatch-agent.json'
s3Path_CW_Agent_linux = "s3://qecoe-documents/CW_MemoryAgent/Linux/"

cw_agent_windows_config_dir = os.path.join(os.path.dirname(__file__), 'windows')
cw_agent_windows_config_schemaFile = '\\amazon-cloudwatch-agent-schema.json'
cw_agent_windows_config_File = '\\amazon-cloudwatch-agent.json'
s3Path_CW_Agent_linux = "s3://qecoe-documents/CW_MemoryAgent/Windows/"

def modify_localPath_forS3(localPath, fileName):
    FileWithlocalPath = localPath + fileName
    FileWithlocalPath = FileWithlocalPath.replace("\\", "\\")
    return FileWithlocalPath

cw_agent_linuxSchema_file = modify_localPath_forS3(cw_agent_linux_config_dir, cw_agent_linux_config_schemaFile)
cw_agent_linux_file = modify_localPath_forS3(cw_agent_linux_config_dir, cw_agent_linux_config_File)

cw_agent_winSchema_file = modify_localPath_forS3(cw_agent_windows_config_dir, cw_agent_windows_config_schemaFile)
cw_agent_win_file = modify_localPath_forS3(cw_agent_windows_config_dir, cw_agent_windows_config_File)

# Function to copy file in/out of S3
def publish_to_aws_s3(source_path, destination_path, profile):
    command = f'aws s3 cp {source_path} {destination_path} {profile}'
    try:
        subprocess.run(command, shell=True, check=True)
        print("AWS S3 cp command executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing the AWS S3 cp command: {e}")


#Upload CW Agent Schemas to S3
#publish_to_aws_s3(cw_agent_linuxSchema_file, s3Path_CW_Agent_linux, awsProfile)
publish_to_aws_s3(cw_agent_linux_file, s3Path_CW_Agent_linux, awsProfile)
##Upload CW Agent actual Config to S3
#publish_to_aws_s3(cw_agent_winSchema_file, s3Path_CW_Agent_linux, awsProfile)
publish_to_aws_s3(cw_agent_win_file, s3Path_CW_Agent_linux, awsProfile)
