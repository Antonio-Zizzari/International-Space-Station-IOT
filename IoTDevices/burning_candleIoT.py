import random
import boto3


def burn_candle(ENDPOINT_URL, DATA):
    sqs = boto3.resource('sqs', endpoint_url=ENDPOINT_URL)
    queue = sqs.get_queue_by_name(QueueName='candle')

    if random.random() < 0.05:
        error_queue = sqs.get_queue_by_name(QueueName="Errors")
        error_msg = '{"device": "burning_candel","error_date": "%s"}' % (DATA)
        print(error_msg)
        error_queue.send_message(MessageBody=error_msg)
    else:
        state= ""
        if random.random() < 0.2:
            state="EMPTY"
        else:
            state="FULL"

        msg_body = '{"device": "burn_candle","measure_date": "%s", "state": "%s"}' \
                   % (DATA, state)
        print(msg_body)
        queue.send_message(MessageBody=msg_body)

