from flask import Flask
from boto3.dynamodb.conditions import Key
from config import DefaultConfig
from flask import Flask, render_template, url_for, request, jsonify, session
from globalData import DefaultData
import datetime
import boto3

CONFIG = DefaultConfig()
DATA = DefaultData()

dynamodb = boto3.resource('dynamodb', endpoint_url=CONFIG.ENDPOINT_URL)

table1 = dynamodb.Table('ISS_room')
table2 = dynamodb.Table('ISS_candle')

def give_oxygen_status(gas):
    value='g'
    reason=''
    if float(gas['oxygen']) > 70.00:
        value = 'r'
        reason = 'Risk of eardrum explosion and damage to the equipment'
        return value, reason
    if float(gas['oxygen']) > 50.00:
        value = 'y'
        reason = 'Possible damage to the equipment'
        return value, reason
    if float(gas['oxygen']) > 15.00:
        value = 'g'
        reason = ''
        return value, reason
    if float(gas['oxygen']) > 8.00:
        value = 'y'
        reason = 'Increased stress on astronauts and possible physical harm'
        return value, reason
    if float(gas['oxygen']) > 8.00:
        value = 'y'
        reason = 'Increased stress on astronauts and possible physical harm'
        return value, reason
    if float(gas['oxygen']) < 8.00:
        value = 'r'
        reason = 'Breathable air'
        return value, reason
    return value,reason


def give_nitrogen_status(gas):
    value = 'g'
    reason = ''
    if float(gas['nitrogen']) > 80.00:
        value = 'r'
        reason = 'Astronauts can experience severe asphyxiation'
        return value, reason
    return value, reason

def give_argon_status(gas):
    value = 'g'
    reason = ''
    if float(gas['argon']) > 75.00:
        value = 'r'
        reason = 'Death of the astronauts'
        return value, reason
    if float(gas['argon']) > 25.00:
        value = 'y'
        reason = 'Astronauts may feel nauseous or vomit'
        return value, reason
    return value, reason

def give_carbon_dioxide_status(gas):
    value = 'g'
    reason = ''
    if float(gas['oxygen']) < float(gas['carbon_dioxide']) and float(gas['carbon_dioxide'])>40.00:
        value = 'r'
        reason = 'Astronauts brain necrosis, meaning death'
        return value, reason
    if float(gas['carbon_dioxide'])>10.00:
        value = 'y'
        reason = 'Polluted or poisonous air'
        return value, reason
    return value, reason

def create_app():
    app = Flask(__name__)
    # encrypt data for cookies
    app.config['SECRET_KEY'] = CONFIG.COOKIE_KEY

    @app.route('/')
    def home():

        item = {
            'iot': str(DATA.NUM_IOT_DEVICES),
            'astro': str(DATA.ASTRONAUTS)
        }

        return render_template("index.html",data=item)

    @app.route('/room1')
    def room1():
        return render_template("room1.html")
    @app.route('/room2')
    def room2():
        return render_template("room2.html")
    @app.route('/room3')
    def room3():
        return render_template("room3.html")

    @app.route('/process', methods=['POST', 'GET'])
    def process_data():
        if request.method == "POST":
            room1 = table1.query(KeyConditionExpression=Key('room').eq('room1'))['Items']
            room2 = table1.query(KeyConditionExpression=Key('room').eq('room2'))['Items']
            room3 = table1.query(KeyConditionExpression=Key('room').eq('room3'))['Items']
            rooms=[room1,room2,room3]
            r=['g','g','g']
            num=0

            for room in rooms:
                max_data = datetime.datetime.strptime(room[0]["date"], "%Y-%m-%d %H:%M:%S")
                max_gas = room[0]["gas"]
                for i in room:
                    temp = datetime.datetime.strptime(i['date'], "%Y-%m-%d %H:%M:%S")
                    if temp > max_data:
                        max_data = temp
                        max_gas = i["gas"]


                if give_nitrogen_status(max_gas)[0] == 'y' or give_oxygen_status(max_gas)[0] == 'y' or give_argon_status(max_gas)[0] == 'y' or give_carbon_dioxide_status(max_gas)[0] == 'y':
                    r[num]='y'
                if give_nitrogen_status(max_gas)[0] == 'r' or give_oxygen_status(max_gas)[0] == 'r' or give_argon_status(max_gas)[0] == 'r' or give_carbon_dioxide_status(max_gas)[0] == 'r':
                    r[num]='r'

                num=num+1

            values = table2.scan()['Items']
            max_data = datetime.datetime.strptime(values[0]["date"], "%Y-%m-%d %H:%M:%S")
            max_state = values[0]["state"]
            for i in values:
                temp = datetime.datetime.strptime(i['date'], "%Y-%m-%d %H:%M:%S")
                if temp > max_data:
                    max_data = temp
                    max_state = i['state']
            results = {'room1': r[0],
                       'room2': r[1],
                       'room3': r[2],
                       'state': max_state}

        return jsonify(results)

    @app.route('/roomsDetails', methods=['POST', 'GET'])
    def roomDetails():
        if request.method == "POST":
            data = request.get_json()[0]['room']

            room = table1.query(KeyConditionExpression=Key('room').eq(data))['Items']
            r = 'g'
            arrayn = []
            arrayo = []
            arraya = []
            arrayc = []
            arrayt = []

            max_data = datetime.datetime.strptime(room[0]["date"], "%Y-%m-%d %H:%M:%S")
            max_temperature = room[0]["temperature"]
            max_humidity = room[0]["humidity"]
            max_gas = room[0]["gas"]
            for i in room:
                temp = datetime.datetime.strptime(i['date'], "%Y-%m-%d %H:%M:%S")
                arrayt.append(temp)
                arrayn.append(i["gas"]['nitrogen'])
                arrayo.append(i["gas"]['oxygen'])
                arraya.append(i["gas"]['argon'])
                arrayc.append(i["gas"]['carbon_dioxide'])
                if temp > max_data:
                    max_data = temp
                    max_temperature = i["temperature"]
                    max_humidity = i["humidity"]
                    max_gas = i["gas"]

            if give_nitrogen_status(max_gas)[0] == 'y' or give_oxygen_status(max_gas)[0] == 'y' or \
                    give_argon_status(max_gas)[0] == 'y' or give_carbon_dioxide_status(max_gas)[0] == 'y':
                r = 'y'

            if give_nitrogen_status(max_gas)[0] == 'r' or give_oxygen_status(max_gas)[0] == 'r' or \
                    give_argon_status(max_gas)[0] == 'r' or give_carbon_dioxide_status(max_gas)[0] == 'r':
                r = 'r'



            results = {'humidity': max_humidity,
                       'temperature': max_temperature,
                       'nitrogen': max_gas['nitrogen'],
                       'oxygen': max_gas['oxygen'],
                       'argon': max_gas['argon'],
                       'carbon_dioxide': max_gas['carbon_dioxide'],
                       'ov': give_oxygen_status(max_gas)[0],
                       'orr': give_oxygen_status(max_gas)[1],
                       'nv': give_nitrogen_status(max_gas)[0],
                       'nr': give_nitrogen_status(max_gas)[1],
                       'av': give_argon_status(max_gas)[0],
                       'ar': give_argon_status(max_gas)[1],
                       'cv': give_carbon_dioxide_status(max_gas)[0],
                       'cr': give_carbon_dioxide_status(max_gas)[1],
                       'color': r,
                       'arrayn': arrayn,
                       'arrayo': arrayo,
                       'arraya': arraya,
                       'arrayc': arrayc,
                       'arrayt': arrayt}

        return jsonify(results)

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('pages-error-404.html'), 404

        return app.route()

    #aJax function updated by javascript




    return app
