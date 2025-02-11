import boto3
import json
import os



def lambda_handler(event, context):
    
    """This is the lambda handler"""
    
    print(event)
    return {
            'statusCode': 200,
            'body': json.dumps('Data stored successfully!')
        }
    