
# Installation and usage

### Prerequisities

1. Docker
2. AWS CLI
3. boto3
4. Flask
5. (Optional) nodejs for database interface
6. (Optional) telegram bot

#### **Prerequisites fast guide:**
- Docker: https://docs.docker.com/engine/install/ubuntu/
    remember to create enable the use of Docker without root
    https://docs.docker.com/engine/install/linux-postinstall/
- Python3 https://docs.python-guide.org/starting/install3/linux/
- pip `sudo apt install python3-pip`
- Boto3 `pip install boto3`

Install and configure the AWS CLI:
- Installation: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
- Configuration: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html
	
-	commands to run:
	``` sudo apt install npm
	sudo apt update
	pip install flask
	pip install flask-login
	pip install flask-sqlalchemy
	```
# Setting up the environment
1. Clone the repository:
	```
	git clone https://github.com/Antonio-Zizzari/International-Space-Station-IOT.git
	```
2. Launch LocalStack:
	```
	docker run --rm -it -p 4566:4566 -p 4571:4571 localstack/localstack
	```

	- test the docker container:
		```
		aws s3 mb s3://test --endpoint-url=http://localhost:4566
		```

3. Run DynamoDB and create tables of DynamoDB:
	```
	DYNAMO_ENDPOINT=http://localhost:4566 dynamodb-admin
	```
	```
	python3 DynamoDB/createTable.py
	```
4. Create and check the SQS queue:
	```aws sqs create-queue --queue-name room1 --endpoint-url=http://localhost:4566
	aws sqs create-queue --queue-name room2 --endpoint-url=http://localhost:4566
	aws sqs create-queue --queue-name room3 --endpoint-url=http://localhost:4566
	aws sqs create-queue --queue-name candle --endpoint-url=http://localhost:4566
	aws sqs create-queue --queue-name Errors --endpoint-url=http://localhost:4566
	aws sqs create-queue --queue-name OnOffOxygen --endpoint-url=http://localhost:4566
	```
	- Print all the SQS queue:
	```
	aws sqs list-queues --endpoint-url=http://localhost:4566
	```

5. Verify email identity:
	```
	aws ses verify-email-identity --email-address nasa@nasa.com --endpoint-url=http://localhost:4566
	```

###   Create the time-triggered Lambda functions to elaborate the data

1. Create the role:
	```
	aws iam create-role --role-name lambdarole --assume-role-policy-document file://ServerlessFunction/role_policy.json --query 'Role.Arn' --endpoint-url=http://localhost:4566
	```

2.  Attach the policy:
	```
	aws iam put-role-policy --role-name lambdarole --policy-name lambdapolicy --policy-document file://ServerlessFunction/policy.json --endpoint-url=http://localhost:4566
	```

3.  Create the zip file, move in the folder 'code'
	```
	cd ServerlessFunction
	zip -j data.zip dataFunc.py ../config.py ../globalData.py
	zip -j error.zip errorFunc.py ../config.py ../globalData.py
	zip -j mail.zip mailFunc.py ../config.py ../globalData.py
	```
4.  Create the function and save the Arn (it should be something like arn:aws:lambda:us-east-2:000000000000:function:smartIrrigation):

	```
	aws lambda create-function --function-name data --zip-file fileb://data.zip --handler dataFunc.lambda_handler --runtime python3.8 --role arn:aws:iam::000000000000:role/lambdarole --endpoint-url=http://localhost:4566
	```
	```
	aws lambda create-function --function-name error --zip-file fileb://error.zip --handler errorFunc.lambda_handler --runtime python3.8 --role arn:aws:iam::000000000000:role/lambdarole --endpoint-url=http://localhost:4566
	```
	```
	aws lambda create-function --function-name mail --zip-file fileb://mail.zip --handler mailFunc.lambda_handler --runtime python3.8 --role arn:aws:iam::000000000000:role/lambdarole --endpoint-url=http://localhost:4566
	```
	- If you want invoke the lambda function manually, at the first generate the random values of sensors and then invoke the serverless function:
		```
		python3 IoTDevices/runIoTDevices.py
		```
		```
		aws lambda invoke --function-name data out --endpoint-url=http://localhost:4566
		```
		```
		aws lambda invoke --function-name error out --endpoint-url=http://localhost:4566
		```
		```
		aws lambda invoke --function-name mail out --endpoint-url=http://localhost:4566
		```

5.  Set up a CloudWatch rule to trigger the lambda functions, create the rule and save the Arn (it should be something like arn:aws:events:us-east-2:000000000000:rule/<--name>):

	```
	aws events put-rule --name everyMin --schedule-expression "rate(10 minutes)" --endpoint-url=http://localhost:4566
	```
	-  Check that the rules has been correctly created with the frequency wanted:
		```
		aws events list-rules --endpoint-url=http://localhost:4566
		```
	-  Add permissions to the rule:

		```
		aws lambda add-permission --function-name data --statement-id everyMin --action 'lambda:InvokeFunction' --principal events.amazonaws.com --source-arn arn:aws:events:us-east-2:000000000000:rule/data --endpoint-url=http://localhost:4566
		```
		```
		aws lambda add-permission --function-name error --statement-id everyMin --action 'lambda:InvokeFunction' --principal events.amazonaws.com --source-arn arn:aws:events:us-east-2:000000000000:rule/error --endpoint-url=http://localhost:4566
		```
		```
		aws lambda add-permission --function-name mail --statement-id everyMin --action 'lambda:InvokeFunction' --principal events.amazonaws.com --source-arn arn:aws:events:us-east-2:000000000000:rule/mail --endpoint-url=http://localhost:4566
		```
	-  Add the lambda functions to the rule using the JSON file containing the Lambda function Arn:
		```
		aws events put-targets --rule everyMin --targets file://data_targets.json --endpoint-url=http://localhost:4566
		```
		```
		aws events put-targets --rule everyMin --targets file://error_targets.json --endpoint-url=http://localhost:4566
		```
		```
		aws events put-targets --rule everyMin --targets file://mail_targets.json --endpoint-url=http://localhost:4566
		```
### Telegram bot settings:
1.  Create a new bot requiring it from BotFather through telegram.
2.  Obtain your bot_id from  [https://api.telegram.org/bot](https://api.telegram.org/bot)<YOUR_TOKEN>/getUpdates.
3.  Open config.py and edit the fields: TELEGRAM_SWITCH = "true", TOKEN_TELEGRAM_BOT= <YOUR_TOKEN>, ID_PRODUCER= <YOUR_ID>.

### Last settings:
- Edit the values into the config.py (The port of the service, the cookie key for the website, endpoint url of localstack, emails, id of the telegram account, token telegram, if you want mail and telegram mode on) also you can edit globalData.py.

## How run
1.  Simulate the IoT devices:
	```
	python3 IoTDevices/runIoTDevices.py
	```
2. Load data into DynamoDB:
	```
	python3 DynamoDB/loadData.py
	```
3. Run Flask website:
	```
	python3 main.py
	```
4.  Go to the website and see the informations what you want.
5.   To check the logs about the sent emails, run this command:
		```
		aws logs get-log-events --log-group-name ISS_Candle --log-stream-name EmailSent --endpoint-url=http://localhost:4566
		```

