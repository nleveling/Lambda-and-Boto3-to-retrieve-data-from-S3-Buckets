import boto3
from botocore.client import Config
from botocore import UNSIGNED
import os

def download(event, context):
    # Create AWS credentials even though S3 is public
    cred = {"aws_access_key_id": "", 
            "aws_secret_access_key": "", 
            "config": Config(signature_version=UNSIGNED)}
    
    # Create session
    session = boto3.Session()
    s3_client = session.client('s3', **cred)
    
    # Define source S3 bucket and object key/prefix
    source_bucket = 'noaa-ocs-nationalbathymetry-pds'
    prefix = 'BlueTopo/_BlueTopo_Tile_Scheme/BlueTopo_Tile_Scheme'
    
    # Use paginator to iterate through objects
    paginator = s3_client.get_paginator("list_objects_v2")
    objs = paginator.paginate(Bucket=source_bucket, Prefix=prefix).build_full_result()
    
    if len(objs['Contents']) == 0:
        print(f"No geometry found in {prefix}")
        return
    
    # Source name variable. 
    source_name = objs['Contents'][0]['Key']
    
    # Define destination S3 bucket and key
    destination_bucket = 'geopackagebuck'
    destination_key = 'output/Output.gpkg' 
    
    # Download object from source bucket to a temporary file
    temp_file = '/tmp/Output.gpkg'  # AWS Lambda provides limited storage in /tmp
    s3_client.download_file(source_bucket, source_name, temp_file)
    
    # Create a new S3 client for upload
    s3_upload_client = session.client('s3')
    
    # Upload the temporary file to the destination bucket
    s3_upload_client.upload_file(temp_file, destination_bucket, destination_key)
    
    # Remove the temporary file
    os.remove(temp_file)

    print(f"Geopackage downloaded from {source_bucket}/{source_name} and uploaded to {destination_bucket}/{destination_key}")