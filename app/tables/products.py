import os
import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
products_table = dynamodb.Table(name=os.environ.get("TABLE_NAME"))
