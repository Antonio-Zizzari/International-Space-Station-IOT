import boto3
import datetime
import json
from config import DefaultConfig
from globalData import DefaultData
import time

CONFIG = DefaultConfig
DATA = DefaultData


def lambda_handler(event, context):
    sqs = boto3.resource('sqs', endpoint_url=CONFIG.ENDPOINT_URL)
    dynamodb = boto3.resource('dynamodb', endpoint_url=CONFIG.ENDPOINT_URL)

    table = dynamodb.Table('ISS_room')
    rooms = DATA.ROOMS
    for room in rooms:
        queue = sqs.get_queue_by_name(QueueName=room)
        messages = []
        while True:
            response = queue.receive_messages(MaxNumberOfMessages=9, VisibilityTimeout=1, WaitTimeSeconds=1)
            if response:
                messages.extend(response)
                date = ""
                temperature = ""
                humidity = ""
                nitrogen = ""
                oxygen = ""
                argon = ""
                carbon_dioxide = ""
                for message in messages:
                    content = json.loads(message.body)

                    device = content["device"]
                    date = content["measure_date"]

                    if (device == 'air_gas'):
                        nitrogen = content["nitrogen"]
                        oxygen = content["oxygen"]
                        argon = content["argon"]
                        carbon_dioxide = content["carbon_dioxide"]
                    elif (device == 'air_humidity'):
                        humidity = content['humidity']
                    elif (device == 'air_temperature'):
                        temperature = content['temperature']

                    message.delete()

                    sqs2 = boto3.resource('sqs', endpoint_url=CONFIG.ENDPOINT_URL)
                    queue2 = sqs2.get_queue_by_name(QueueName='OnOffOxygen')
                    #if the oxygen is too much, we need to close the oxygen valves
                    #or open it if oxygen is too low
                    if oxygen == '':
                        test=1 #do nothing
                    elif float(oxygen) > 50: #this is a fake request to an iot device
                        msg_body = '{"operation": "close"}'
                        queue2.send_message(MessageBody=msg_body)
                        print("requests.get('https://OnOffOxygen?operation=close")
                    else:#this is a fake request to an iot device
                        msg_body = '{"operation": "open"}'
                        queue2.send_message(MessageBody=msg_body)
                        print("requests.get('https://OnOffOxygen?operation=open")

                    #savings data collected from the iot devices
                    item = {
                        'room': room,
                        'date': str(date),
                        'temperature': str(temperature),
                        'humidity': str(humidity),
                        'gas': {
                            "nitrogen": nitrogen,
                            "oxygen": oxygen,
                            "argon": argon,
                            "carbon_dioxide": carbon_dioxide
                        }
                    }
                    table.put_item(Item=item)
            else:
                break


