from __future__ import print_function
import boto3
import json

print('Loading function')

#set region
REGION = 'ap-south-1'
#set the SNS topic ARN you want to alert on
SNS_TOPIC_ARN = 'arn:aws:sns:ap-south-1:773591337265:Security-Notification'

def lambda_handler(event, context):
    #print(event)
    event = event['Records'][0]['Sns']['Message']
    s = "{'muffin' : 'lolz', 'foo' : 'kitty'}"
    json_acceptable_event = event.replace("\'", "\"")
    # print(json_acceptable_event)
    event = json.loads(json_acceptable_event)
    # print(event)
    # print(event['detail'])
    # print(event['detail']['eventName'])
    # print(event['detail']['sourceIPAddress'])
    # print(event['detail']['userAgent'])
    # print(event['detail']['requestParameters'])
    # print(event['detail']['responseElements'])
    # print(event['time'])
    
    sns_body = 'EventName: {}\nSourceIP: {}\nUserAgent: {}\nRequest: {}\nResponse: {}\nTime: {}'.format(event['detail']['eventName'], event['detail']['sourceIPAddress'], event['detail']['userAgent'], event['detail']['requestParameters'], event['detail']['responseElements'], event['time'])
    client = boto3.client('sns', region_name=REGION)
    # print(sns_body)
    response = client.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject='Security group state change notification',
        Message=sns_body
    )