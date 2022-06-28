import json
import csv
from datetime import datetime
import os
import boto3
import sys
from datetime import datetime
import logging
import time

# Global variable initialization
ssm_send_command_output_file 	= sys.argv[1].strip()
env			 	= 'stg'
ec2_client 			= boto3.client('ec2')
now_str 			= datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
mongo_version_file 		= f"{env}-mongodb_version_details-{now_str}.csv"

logging.basicConfig(format='%(asctime)s :: %(levelname)s :: %(funcName)s :: %(lineno)d :: %(message)s', level = logging.INFO)
logging.info(f"mongodb version details output will be saved in file = {mongo_version_file}")

### open the csv_file csv in write mode to log mongodb details
if (not os.path.isfile(mongo_version_file)):
	mongo_output_creds_csv = open(mongo_version_file, 'a')
	with mongo_output_creds_csv:
		writer = csv.writer(mongo_output_creds_csv)
		writer.writerow(("DateTime", "EC2Name", "Team", "Service", "MongoDB Status", "MongoDB Version","Remarks")) 


def save_mongo_version_to_csv(instance_name, instance_status, instance_output ,remarks, Team, Service):
	mongo_output_creds_csv = open(mongo_version_file, 'a')
	with mongo_output_creds_csv:
		writer = csv.writer(mongo_output_creds_csv)
		writer.writerow((str(datetime.now()), instance_name, Team, Service, instance_status, instance_output, remarks)) 

def get_mongodb_version_details():
	global ssm_send_command_output_file
	try:
		with open(ssm_send_command_output_file) as json_file:
    			data = json.load(json_file)

		for instanceData in data[0]:
			instance_status	= ""
			instance_output	= ""
			instance_name	= instanceData['InstanceName']
			instance_id 	= instanceData['InstanceId']
			Team 		= ""
			Service 	= ""
			ec2_res		= ec2_client.describe_instances(InstanceIds=[instance_id])
			if ec2_res['ResponseMetadata']['HTTPStatusCode'] == 200:
				instance_status	= ec2_res['Reservations'][0]['Instances'][0]['State']['Name']
				Tags		 = ec2_res['Reservations'][0]['Instances'][0]['Tags']
				for tags in Tags:
					if tags['Key'] == 'Team':
						Team	= tags['Value']
					if tags['Key'] == 'Service':
						Service	= tags['Value']
					if tags['Key'] == 'Name':
						instance_name	= tags['Value']

			for CommandPlugins in instanceData['CommandPlugins']:
				instance_output = instance_output + ":" + str(CommandPlugins['Output'].split("\n")[0]).strip("db version v")
			save_mongo_version_to_csv(instance_name, instance_status, instance_output.lstrip(':') ,"", Team, Service)

	except Exception as error:
		logging.exception(f"Error in function get_mongodb_version_details {str(error)}")



if __name__ == '__main__':
	"""
	main module to execute the functionality to parse SSM output and return mongoDB version details.

	"""
	get_mongodb_version_details()


