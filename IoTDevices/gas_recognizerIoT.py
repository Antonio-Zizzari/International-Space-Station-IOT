import random
import boto3



def air_gas(ENDPOINT_URL, DATA,ROOMS):
    sqs = boto3.resource('sqs', endpoint_url=ENDPOINT_URL)

    for i in range(len(ROOMS)):
        queue = sqs.get_queue_by_name(QueueName=ROOMS[i])
        if random.random() < 0.05:
            error_queue = sqs.get_queue_by_name(QueueName="Errors")
            error_msg = '{"device": "air_gas","room": "%s","error_date": "%s"}' % (ROOMS[i], DATA)
            print(error_msg)
            error_queue.send_message(MessageBody=error_msg)
        else:
            total=100.00
            nitrogen = round(random.uniform(0.00, total), 2)
            total=total-nitrogen
            oxygen = round(random.uniform(0.00, total), 2)
            total=total - oxygen
            argon = round(random.uniform(0.00, total), 2)
            total=total-argon
            carbon_dioxide = round(random.uniform(0.00, total), 2)


            msg_body = '{"device": "air_gas","room": "%s","measure_date": "%s","nitrogen": "%s","oxygen": "%s","argon": "%s","carbon_dioxide": "%s"}' \
                       % (ROOMS[i], DATA, str(nitrogen), str(oxygen), str(argon), str(carbon_dioxide))
            print(msg_body)
            queue.send_message(MessageBody=msg_body)

