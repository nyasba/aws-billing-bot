# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

import boto3
import json
import logging
import pytz
import os

from urllib2 import Request, urlopen, URLError, HTTPError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def post_current_charges():

    startDate = datetime.today() - timedelta(days = 1)
    endDate = datetime.today()

    session = boto3.Session()
    client = session.client('cloudwatch')   
    response = client.get_metric_statistics (
        MetricName = 'EstimatedCharges',
        Namespace  = 'AWS/Billing',
        Period   = 86400,
        StartTime  = startDate,
        EndTime = endDate,
        Statistics = ['Maximum'],
        Dimensions = [
            {
                'Name': 'Currency',
                'Value': 'USD'
            }
        ]
    )

    maximum = response['Datapoints'][0]['Maximum']
    date = response['Datapoints'][0]['Timestamp'].strftime('%Y/%m/%d')

    webhookUrl = os.environ['WEBHOOKURL']
    env = os.environ['ENVIRONMENT']

    message = "[" + env + "] " + date + "時点でのAWS利用料は" + str(maximum) + "ドルです" 
    print message

    slack_message = {
        'channel': os.environ['CHANNEL'],
        'text': message
    }

    req = Request(webhookUrl, json.dumps(slack_message))
    try:
        response = urlopen(req)
        response.read()
        logger.info("Message posted to %s", slack_message['channel'])
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)


def lambda_handler(event, context):
    """Lambda使う場合のエントリポイント"""
    post_current_charges()


if __name__ == "__main__":
    """コマンド実行のエントリポイント"""
    post_current_charges()