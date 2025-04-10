import requests
import sys # Import sys for exiting
import boto3 # Import AWS SDK

# SNS Topic ARN
TOPIC_ARN = "arn:aws:sns:ap-south-1:808162501188:AmulStockAlerts"

# Same product IDs
target_ids = {
    "66bcad006760c5002bc81922",  #amul-high-protein-plain-lassi-200-ml-or-pack-of-30
    "651d0a21e8ac81a61d2d1a74"  #amul-high-protein-rose-lassi-200-ml-or-pack-of-30
}

# Use browser headers (Cookie removed)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://shop.amul.com/",
    "Origin": "https://shop.amul.com",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Cookie": "jsessionid=s%3AFQUkz%2FUQiR9D6VcDstzCjXpm.nmx44aAZo9Oz%2BtTTruf4NjKq17mKeUz2xjjUMKwYeQQ", # Re-added jsessionid
    "X-Requested-With": "XMLHttpRequest" # Added common AJAX header
}

# API URL and base params
url = "https://shop.amul.com/api/1/entity/ms.products"
params = {
    # --- Fields from browser request ---
    "fields[name]": 1,
    "fields[brand]": 1,
    "fields[categories]": 1,
    "fields[collections]": 1,
    "fields[alias]": 1,
    "fields[sku]": 1,
    "fields[price]": 1,
    "fields[compare_price]": 1,
    "fields[original_price]": 1,
    "fields[images]": 1,
    "fields[metafields]": 1,
    "fields[discounts]": 1,
    "fields[catalog_only]": 1,
    "fields[is_catalog]": 1,
    "fields[seller]": 1,
    "fields[available]": 1,
    "fields[inventory_quantity]": 1,
    "fields[net_quantity]": 1,
    "fields[num_reviews]": 1,
    "fields[avg_rating]": 1,
    "fields[inventory_low_stock_quantity]": 1,
    "fields[inventory_allow_out_of_stock]": 1,
    "fields[lp_seller_ids]": 1,
    "fields[_id]": 1, # Ensure _id is still requested
    # --- Other params ---
    "limit": len(target_ids), # Keep limit based on target_ids
    "start": 0,
    # --- Filter by specific IDs ---
    "filters[0][field]": "_id",
    "filters[0][operator]": "in"
    # We won't add facets/facetgroup for now, focusing on fields first.
}

# Dynamically add target IDs to params
for i, product_id in enumerate(target_ids):
    params[f"filters[0][value][{i}]"] = product_id


# Make the request with error handling
try:
    response = requests.get(url, headers=headers, params=params, timeout=10) # Added timeout
    response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
    sys.exit(1) # Exit if request fails

# Initialize SNS client (ensure AWS credentials and region are configured)
try:
    sns = boto3.client('sns', region_name='ap-south-1') # Explicitly set region
except Exception as e:
    print(f"Error initializing SNS client: {e}")
    sns = None # Set sns to None if initialization fails

# Debug output (optional - can be removed)
#print("Request URL:", response.request.url) # Print the exact request URL
#print("Status Code:", response.status_code)
# print("Raw Response:", response.text) # Commented out raw response

# Extract and process data with error handling
try:
    data = response.json().get("data", [])
except requests.exceptions.JSONDecodeError:
    print("Failed to decode JSON response.")
    print("Raw Response:", response.text)
    sys.exit(1) # Exit if JSON decoding fails


if not data:
    print("No product data found in the response.")
else:
    print(f"Checking stock for {len(data)} product(s):\n")
    in_stock_products = [] # List to hold details of products in stock

    for product in data:
        name = product.get("name", "Unnamed Product")
        available = product.get("available", 0)
        inventory_qty = product.get("inventory_quantity", "N/A")

        print(f"Product: {name}")
        status_text = f"Available: {'✅ In Stock' if available else '❌ Out of Stock'} (Qty: {inventory_qty})"
        print(status_text)

        if available:
            in_stock_products.append({"name": name, "qty": inventory_qty})

        print() # Add a newline for spacing

    # After checking all products, send one consolidated notification if any are in stock
    if in_stock_products and sns:
        print("--- Sending Consolidated Notification ---")
        subject = f"{len(in_stock_products)} Amul Product(s) In Stock!"
        message_body = "The following products are back in stock:\n\n"
        for item in in_stock_products:
            message_body += f"- {item['name']} (Qty: {item['qty']})\n"

        try:
            response = sns.publish(
                TopicArn=TOPIC_ARN,
                Message=message_body,
                Subject=subject
            )
            print(f"Consolidated SNS notification sent! MessageId = {response['MessageId']}")
        except Exception as e:
            print(f"Error sending consolidated SNS notification: {e}")
    elif in_stock_products and not sns:
        print("SNS client not initialized. Cannot send consolidated notification.")
    else:
        print("--- No target products currently in stock. --- ")
