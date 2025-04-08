import requests
import boto3

sns = boto3.client("sns", region_name="ap-south-1")
# Product IDs we care about
target_ids = {
    "66bcad006760c5002bc81922", #amul-high-protein-plain-lassi-200-ml-or-pack-of-30
    "651d0a21e8ac81a61d2d1a74"  #amul-high-protein-rose-lassi-200-ml-or-pack-of-30
}

TOPIC_ARN = "arn:aws:sns:ap-south-1:808162501188:AmulStockAlerts"

# API URL and params
url = "https://shop.amul.com/api/1/entity/ms.products"
params = {
    "fields[available]": 1,
    "fields[name]": 1,
    "fields[_id]": 1,
    "fields[alias]": 1,
    "limit": 50,
    "start": 0,
    "filters[0][field]": "categories",
    "filters[0][value][0]": "protein",
    "filters[0][operator]": "in"
}

# Fetch the response
response = requests.get(url, params=params)
data = response.json().get("data", [])

# Filter and print status
for product in data:
    product_id = product.get("_id")
    if product_id in target_ids:
        name = product.get("name", "Unnamed Product")
        available = product.get("available", 0)
        if available:
            message = f"🟢 Product in stock: {name}"
            try:
                response = sns.publish(
                    TopicArn=TOPIC_ARN,
                    Message=message,
                    Subject="Amul Product Alert"
                )
                print(f"\nSNS sent: Product: {name} MessageId = {response['MessageId']}")
            except Exception as e:
                print(f"Error sending SNS: {e}")

