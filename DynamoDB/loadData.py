import boto3
import datetime
import random
import json
from globalData import DefaultData
from config import DefaultConfig

CONFIG = DefaultConfig
DATA = DefaultData()

dynamodb = boto3.resource('dynamodb', endpoint_url=CONFIG.ENDPOINT_URL)

table = dynamodb.Table('ISS_room')

rooms = DATA.ROOMS

for i in range(len(rooms)):
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    temperature = random.randint(3, 35)
    humidity = random.randint(20, 80)
    gas = DATA.GAS
    item = {
        'room': rooms[i],
        'date': str(date),
        'temperature': str(temperature),
        'humidity': str(humidity),
        'gas': gas
    }
    print("Stored item", item)
    table.put_item(Item=item)

table = dynamodb.Table('ISS_candle')
date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
item = {
        'date': str(date),
        'state': 'FULL'
    }
print("Stored item", item)
table.put_item(Item=item)