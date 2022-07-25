import boto3
from config import DefaultConfig

CONFIG= DefaultConfig
dynamodb = boto3.resource('dynamodb', endpoint_url=CONFIG.ENDPOINT_URL)

table1 = dynamodb.create_table(
    TableName='ISS_room',
    KeySchema=[
        {
            'AttributeName': 'room',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'date',
            'KeyType': 'RANGE'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'room',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'date',
            'AttributeType': 'S'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
)

table2 = dynamodb.create_table(
    TableName='ISS_candle',
    KeySchema=[
        {
            'AttributeName': 'date',
            'KeyType': 'HASH'
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'date',
            'AttributeType': 'S'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
)

print('Table1', table1, 'created!')
print('Table2', table2, 'created!')

#creating the log group

client = boto3.client('logs', endpoint_url=CONFIG.ENDPOINT_URL)
retention_period_in_days = 7

client.create_log_group(logGroupName='ISS_Candle')

client.put_retention_policy(
	logGroupName='ISS_Candle',
	retentionInDays=retention_period_in_days
)
client.create_log_stream(
    logGroupName='ISS_Candle',
    logStreamName='EmailSent'
)