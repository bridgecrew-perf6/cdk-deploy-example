import json
import boto3


def handler(event, context):
    response = "Received Message Body : " + event['Records'][0]['body']
    print(response)
    return {
        'statusCode': 200,
        'body': response
    }
