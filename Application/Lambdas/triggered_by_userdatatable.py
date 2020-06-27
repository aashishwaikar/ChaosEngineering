import boto3
import requests
from requests_aws4auth import AWS4Auth

region = 'ap-south-1' # e.g. us-east-1
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = 'https://search-myes-q6vqjhdvc4ghafvw4n275b3gau.ap-south-1.es.amazonaws.com' # the Amazon ES domain, with https://
index = 'covid'
type = 'userdata'
url = host + '/' + index + '/' + type + '/'

headers = { "Content-Type": "application/json" }


# {'eventID': 'b8f6d74cd7b7c85dd44b4f5bbc26bf0e', 'eventName': 'INSERT', 'eventVersion': '1.1', 'eventSource': 'aws:dynamodb', 
# 'awsRegion': 'ap-south-1', 'dynamodb': {'ApproximateCreationDateTime': 1592363446.0, 'Keys': {'Location': {'S': 'Chandigarh'}}, 'NewImage': {'Positive': {'N': '1'}, 'ProbablyPositive': {'N': '0'}, 'Location': {'S': 'Chandigarh'}},
# 'SequenceNumber': '23204700000000009911740488', 'SizeBytes': 63, 'StreamViewType': 'NEW_IMAGE'}, 'eventSourceARN': 'arn:aws:dynamodb:ap-south-1:773591337265:table/RealTimeUpdates/stream/2020-06-16T02:07:40.641'}


def handler(event, context):
    count = 0
    for record in event['Records']:
        # Get the primary key for use as the Elasticsearch ID
        id = record['dynamodb']['Keys']['Location']['S']
        #console.log('record', record)
        print(record)

        if record['eventName'] == 'REMOVE':
            r = requests.delete(url + id, auth=awsauth)
        else:
            document = record['dynamodb']['NewImage']
            r = requests.put(url + id, auth=awsauth, json=document, headers=headers)
            print(r.content)
        count += 1
    return str(count) + ' records processed.'