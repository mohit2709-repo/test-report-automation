import boto3, os, sys
import json

# Importing Functions
functions_dir = os.path.join(os.path.dirname(__file__), '..','functions')
print ('Current Path')
sys.path.append(functions_dir)
from common.general import *

def initialize_aws_session(logFileName):
    ec2_config_filePath = os.path.join(os.path.dirname(__file__), 'config','basic_ec2.config')
    with open(ec2_config_filePath, 'r') as ec2_config_file:
        ec2_configJson = json.load(ec2_config_file)
        AWS_profile = ec2_configJson.get("lt_perf_test", {}).get("AWS_PROFILE")
        AWS_region = ec2_configJson.get("lt_perf_test", {}).get("AWS_REGION")
        aws_session_message = f"AWS_Profile: {AWS_profile}; AWS_Region: {AWS_region}"
        logging(aws_session_message, logFileName)
        session = boto3.Session(region_name=AWS_region, profile_name=AWS_profile)
        return session
