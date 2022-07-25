import random
import boto3


def air_humidity(ENDPOINT_URL, DATA,ROOMS):
    sqs = boto3.resource('sqs', endpoint_url=ENDPOINT_URL)

    for i in range(len(ROOMS)):
        queue = sqs.get_queue_by_name(QueueName=ROOMS[i])
        if random.random() < 0.05:
            error_queue = sqs.get_queue_by_name(QueueName="Errors")
            error_msg = '{"device": "air_humidity","room": "%s","error_date": "%s"}' % (ROOMS[i], DATA)
            print(error_msg)
            error_queue.send_message(MessageBody=error_msg)
        else:
            humidity = random.randint(20, 80)
            msg_body = '{"device": "air_humidity","room": "%s","measure_date": "%s","humidity": "%s"}' \
                       % (str(i), DATA, str(humidity))
            print(msg_body)
            queue.send_message(MessageBody=msg_body)

