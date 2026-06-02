import os
import boto3
from dotenv import load_dotenv

load_dotenv()
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get("REGION_NAME"))
products_table = dynamodb.Table(name=os.environ.get("TABLE_NAME"))
