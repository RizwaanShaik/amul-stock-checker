import boto3

sns = boto3.client('sns', region_name='ap-south-1')  # Change region if needed

# Create a topic
#response = sns.create_topic(Name='AmulStockAlerts')
#print("Topic ARN:", response['TopicArn'])
#Topic ARN: arn:aws:sns:ap-south-1:808162501188:AmulStockAlerts

# Subscribe to the topic
response = sns.subscribe(
    TopicArn='arn:aws:sns:ap-south-1:808162501188:AmulStockAlerts',
    Protocol='email',
    Endpoint='shaikrizwaan@gmail.com'
)

response2 = sns.subscribe(
    TopicArn='arn:aws:sns:ap-south-1:808162501188:AmulStockAlerts',
    Protocol='sms',
    Endpoint='+918639136086'
)

response2 = sns.subscribe(
    TopicArn='arn:aws:sns:ap-south-1:808162501188:AmulStockAlerts',
    Protocol='sms',
    Endpoint='+918106990600'
)




