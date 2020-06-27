import csv
import requests
import time
import boto3
import datetime
from boto3.dynamodb.conditions import Key
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

#host = 'search-myes-q6vqjhdvc4ghafvw4n275b3gau.ap-south-1.es.amazonaws.com' # For example, my-test-domain.us-east-1.es.amazonaws.com
host = 'search-es-downgraded-y7b2ejeyuizhapib6s2abis5cy.ap-south-1.es.amazonaws.com'
region = 'ap-south-1' # e.g. us-west-1

service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

es = Elasticsearch(
    hosts = [{'host': host, 'port': 443}],
    http_auth = awsauth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection
)

base_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/"

def next_date(curr_date):
	l = curr_date.split('-')
	month = int(l[0])
	date = int(l[1])
	year = l[2]

	if month==1 or month==3 or month==5 or month==7 or month==8 or month==10 or month==12:
		if date<31:
			date+=1
		else:
			date=1
			month+=1
	elif month==4 or month==6 or month==9 or month==11:
		if date<30:
			date+=1
		else:
			date=1
			month+=1
	else:
		if date<29:
			date+=1
		else:
			date=1
			month+=1

	if month<10:
		month='0'+str(month)
	else:
		month=str(month)
	if date<10:
		date='0'+str(date)
	else:
		date=str(date)

	return month+'-'+date+'-'+year

def create_table():
	client = boto3.client('dynamodb', region_name='ap-south-1')
	try:
		resp = client.create_table(
			TableName="DateforES",
			# Declare your Primary Key in the KeySchema argument
			KeySchema=[
				{
					"AttributeName": "index",
					"KeyType": "HASH"
				}
			],
			# Any attributes used in KeySchema or Indexes must be declared in AttributeDefinitions
			AttributeDefinitions=[
				{
				"AttributeName": "index",
				"AttributeType": "S"
				}
			],
			# ProvisionedThroughput controls the amount of data you can read or write to DynamoDB per second.
			# You can control read and write capacity independently.
			ProvisionedThroughput={
				"ReadCapacityUnits": 1,
				"WriteCapacityUnits": 1
			}
		)
		#print("ES Date table created successfully!")
	except client.exceptions.ResourceInUseException:
		print("ES Date table already present")

def delete_table():
	client = boto3.client('dynamodb', region_name='ap-south-1')
	try:
		resp = client.delete_table(
		    TableName="DateforES"
		)
		#print("Tables deleted successfully!")
	except Exception as e:
		print("Error deleting tables:")
		print(e)

def myint(st):
	if st=='':
		return 0
	else:
		return int(st)

if __name__ == "__main__":

	date='01-22-2020'
	datel=[]
	for i in range(200):
		datel.append(date)
		date=next_date(date)

	sft_ind=datel.index('03-22-2020')

	create_table()
	time.sleep(5)

	dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

	dtable = dynamodb.Table('DateforES')
	if dtable.query(KeyConditionExpression=Key('index').eq('1'))['Items'] != []:
		date_in_db = dtable.query(KeyConditionExpression=Key('index').eq('1'))['Items'][0]['date']
	else:
		date_in_db = ''

	start = date_in_db
	if start == '':
		start = '01-22-2020'
		#start = '03-18-2020'
	else:
		start = next_date(date_in_db)

	curr = start
	prev = None

	# request_body = {
	# 				"settings" : {
	# 				"number_of_shards": 5,
	# 				"number_of_replicas": 1
	# 				},

	# 				'mappings': {
	# 				'properties': {
	# 				'Country': {'type': 'text'},
	# 				'Date': {'type': 'date'},
	# 				'Confirmed': {'type': 'integer'},
	# 				'Deaths': {'type': 'integer'},
	# 				'Recovered': {'type': 'integer'},
	# 				}}
	# 				}

	# print("creating 'example_index' index...")
	# es.indices.create(index = 'us', body = request_body)
	while True:
		print("curr ",curr)
		url = base_url+curr+'.csv'

		with requests.Session() as s:
			download = s.get(url)
			decoded_content = download.content.decode('utf-8')
			if(decoded_content=="404: Not Found"):
				delete_table()
				time.sleep(5)
				create_table()
				time.sleep(5)
				with dtable.batch_writer() as batch:
					item = {"index":"1","date":prev}
					batch.put_item(Item=item)
				break
			#print(decoded_content)  #404: Not Found
			state_list = decoded_content.splitlines()[1:]

		case_map = {}

		if datel.index(curr)<sft_ind:
			for line in state_list:
				line = line.split(',')
				#print(line)
				if line[1] == '"Gambia' or line[1] == '"Bahamas':
					continue

				if line[1]== '"Korea':# or (line[0]!='' and line[0][0]=='"'):
					country =  line[1]
					cases = [myint(x) for x in line[4:7]]
				elif line[0]!='' and line[0][0]=='"':
					country =  line[2]
					cases = [myint(x) for x in line[4:7]]
				else:
					country =  line[1]
					# print(country)
					# print(line)
					cases = [myint(x) for x in line[3:6]]
					
				if country in case_map.keys():
					cases_prev = case_map[country]
					case_map[country] = [cases_prev[i] + cases[i] for i in range(3)]
				else:
					case_map[country] = cases
				#print(country, case_map[country])

		else:
			for line in state_list:
				line = line.split(',')
				#print(line)
				if line[3]== '"Korea' or (line[2]!='' and line[2][0]=='"'):
					country =  line[3]
					cases = [myint(x) for x in line[8:11]]
				elif line[2]!='' and line[2][0]=='"':
					country =  line[4]
					cases = [myint(x) for x in line[8:11]]
				else:
					country =  line[3]
					cases = [myint(x) for x in line[7:10]]
					
				if country in case_map.keys():
					cases_prev = case_map[country]
					case_map[country] = [cases_prev[i] + cases[i] for i in range(3)]
				else:
					case_map[country] = cases
				#print(country, case_map[country])


		
		for key in case_map.keys():
			if key == "US" or key == "India" or key == "Brazil" or key == "Italy":
				item = {}

				key1 = key.replace(" ","")
				key1 = key1.replace("\"","")
				key1 = key1.replace(",","").lower()

				item["Country"] = key1
				l=curr.split('-')
				item["Date"] = datetime.date(2020,int(l[0]),int(l[1]))
				item["Confirmed"] = case_map[key][0]
				item["Deaths"] = case_map[key][1]
				item["Recovered"] = case_map[key][2]
				#es.index(index="covid", doc_type="scraped-data", id=key+l[0]+l[1], body=item)
				es.index(index=key1, doc_type="doc", id=int(l[0]+l[1]), body=item)
				i+=1

		#time.sleep(2)

		prev = curr
		curr = next_date(curr)


