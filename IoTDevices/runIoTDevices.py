import boto3
import datetime
import time

from gas_recognizerIoT import *
from humidity_sensorIoT import *
from termometerIoT import *
from burning_candleIoT import *

from config import DefaultConfig
from globalData import DefaultData

URL=DefaultConfig.ENDPOINT_URL
ROOMS = DefaultData.ROOMS
today = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

air_gas(URL,today,ROOMS)
air_humidity(URL,today,ROOMS)
air_temperature(URL,today,ROOMS)
burn_candle(URL,today)



