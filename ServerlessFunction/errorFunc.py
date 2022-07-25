import boto3
import datetime
import json
from config import DefaultConfig
from globalData import DefaultData
import time
import requests

CONFIG = DefaultConfig
DATA = DefaultData

def replace_escapes(text: str=None) -> str:
    text = text.replace("-", "\-").replace(".", "\.").replace("[", "[").replace("]", "]").replace("_","\_").replace("!","\!").replace(":","\:").replace("?","\?").replace(">","\>").replace("<","\<").replace("&#39;","\'").replace("(","\(").replace(")","\)").replace("&quot;", '"').replace("+", "\+")
    return text

def lambda_handler(event, context):
    sqs = boto3.resource('sqs', endpoint_url=CONFIG.ENDPOINT_URL)

    queue = sqs.get_queue_by_name(QueueName='Errors')
    messages = []
    while True:
        response = queue.receive_messages(MaxNumberOfMessages=9, VisibilityTimeout=1, WaitTimeSeconds=1)
        if response:
            messages.extend(response)
            for message in messages:
                content = json.loads(message.body)

                device = content["device"]
                room = ''
                error_date= ''
                body_write = 'test'
                if device == 'burning_candel':
                    error_date = content["error_date"]
                    body_write = ' The IOT device %s had problems on the date %s.' % (device,error_date)

                else:
                    room = content["room"]
                    error_date = content["error_date"]
                    body_write = ' The IOT device %s, inthe room %s had problems on the date %s.' % (device, room,error_date)

                message.delete()
                #send a message to telegram
                if (CONFIG.TELEGRAM_SWITCH == 'ON'):
                    requests.get(
                        'https://api.telegram.org/bot' + CONFIG.TOKEN_TELEGRAM_BOT + '/sendMessage?chat_id=' + CONFIG.ID_PRODUCER + '&parse_mode=Markdown&text=' + str(
                            replace_escapes(body_write)))
        else:
            break


