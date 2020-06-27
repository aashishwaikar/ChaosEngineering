FROM python:3-alpine

MAINTAINER aashish

RUN pip install boto3

RUN pip install datetime

RUN pip install requests

ADD ./ /code/

EXPOSE 3000

WORKDIR /code

ENTRYPOINT ["python" , "scraper_ddb.py"]

