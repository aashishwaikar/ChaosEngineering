FROM python:3-alpine

MAINTAINER aashish

RUN pip install boto3

RUN pip install datetime

RUN pip install requests

RUN pip install requests

RUN pip install elasticsearch

RUN pip install requests_aws4auth

ADD ./ /code/

EXPOSE 3000

WORKDIR /code

ENTRYPOINT ["python" , "testESwithAWS.py"]

