import boto3
import datetime
import json
from config import DefaultConfig
from globalData import DefaultData
import time
import requests

CONFIG = DefaultConfig
DATA = DefaultData


def lambda_handler(event, context):
    sqs = boto3.resource('sqs', endpoint_url=CONFIG.ENDPOINT_URL)
    dynamodb = boto3.resource('dynamodb', endpoint_url=CONFIG.ENDPOINT_URL)

    table = dynamodb.Table('ISS_candle')
    queue = sqs.get_queue_by_name(QueueName='candle')
    messages = []
    while True:
        response = queue.receive_messages(MaxNumberOfMessages=9, VisibilityTimeout=1, WaitTimeSeconds=1)
        if response:
            messages.extend(response)
            date = ""
            state = ""
            for message in messages:
                content = json.loads(message.body)

                state = content["state"]
                date = content["measure_date"]

                message.delete()

                item = {
                    'date': str(date),
                    'state': str(state)
                }
                table.put_item(Item=item)

                if (state == 'EMPTY'):
                    if (CONFIG.MAIL_SWITCH == 'ON'):
                        client = boto3.client('ses', endpoint_url=CONFIG.ENDPOINT_URL)
                        message_mail = {
                            'Subject': {
                                'Data': 'Candles order',
                                'Charset': 'UTF-8'
                            },
                            'Body': {
                                'Text': {
                                    'Data': 'The ISS ended all the candle, we need new candles at LC-39A • Kennedy Space Center.',
                                    'Charset': 'string'
                                },
                                'Html': {
                                    'Data': 'This message body contains HTML formatting.',
                                    'Charset': 'UTF-8'
                                }
                            }
                        }

                        response = client.send_email(
                            Source=CONFIG.EMAIL_ISS,
                            Destination={
                                'ToAddresses': [
                                    CONFIG.EMAIL_CANDLE_PRODUCER,
                                ],
                                'CcAddresses': [],
                                'BccAddresses': []
                            },
                            Message=message_mail
                        )

                        log_client = boto3.client('logs', endpoint_url=CONFIG.ENDPOINT_URL)

                        log_event = {
                            'logGroupName': 'ISS_Candle',
                            'logStreamName': 'EmailSent',
                            'logEvents': [
                                {
                                    'timestamp': int(round(time.time() * 1000)),
                                    'message': str(message_mail)
                                },
                            ],
                        }

                        log_client.put_log_events(**log_event)

        else:
            break
