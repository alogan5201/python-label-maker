import os
import json
from netsuite import NetSuite, Config, TokenAuth
import asyncio
from icecream import ic
import requests
from io import BytesIO
from PIL import Image

def load_config():
    with open('data/config.json', 'r') as f:
        return json.load(f)

config = load_config()

# Fetch TokenAuth parameters from environment variables
consumer_key = os.getenv("NETSUITE_CONSUMER_KEY")
consumer_secret = os.getenv("NETSUITE_CONSUMER_SECRET")
token_id = os.getenv("NETSUITE_TOKEN_ID")
token_secret = os.getenv("NETSUITE_TOKEN_SECRET")
account = os.getenv("NETSUITE_ACCOUNT")

# Ensure all necessary environment variables are available
if not all([consumer_key, consumer_secret, token_id, token_secret, account]):
    raise EnvironmentError("One or more NetSuite TokenAuth environment variables are not set.")

# Configuring NetSuite with TokenAuth sourced from environment variables
ns_config = Config(
    account=account,
    auth=TokenAuth(consumer_key=consumer_key, consumer_secret=consumer_secret, token_id=token_id, token_secret=token_secret),
)
ns = NetSuite(ns_config)

async def process_data(query: dict):
    try:
        restlet_response = await ns.restlet.post(script_id=1171, deploy=1, body=query)
        return restlet_response
    except Exception as e:
        print(f"Error calling RESTlet: {e}")

async def get_vendor_images():
    query = {
        "procedure": "queryRun",
        "query": """
            SELECT v.id AS vendor_id,
                   v.entityid AS vendor_name,
                   f.name AS image_name,
                   f.url AS image_url
            FROM vendor v
            LEFT JOIN file f ON v.image = f.id
            WHERE v.isinactive = 'F'
            ORDER BY v.entityid;
        """
    }
    
    vendor_images = await process_data(query)
    
    # Ensure the path is correct and exists
    item_image_directory = os.path.join('input', 'images', 'vendors')
    os.makedirs(item_image_directory, exist_ok=True)
    
    records = vendor_images.get('records', [])
    for vendor in records:
        vendor_id = vendor.get('vendor_id')
        vendor_name = vendor.get('vendor_name')
        image_name = vendor.get('image_name')
        image_url = vendor.get('image_url')
        
        if image_url:
            full_image_url = f"https://{account}.app.netsuite.com{image_url}"
            try:
                response = requests.get(full_image_url)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content))
                
                # Save the image
                file_name = f"{vendor_id}_{vendor_name}.png"
                file_path = os.path.join(item_image_directory, file_name)
                image.save(file_path)
                ic(f"Saved image for vendor: {vendor_name}")
            except Exception as e:
                ic(f"Error downloading image for vendor {vendor_name}: {e}")
        else:
            ic(f"No image URL for vendor: {vendor_name}")

if __name__ == "__main__":
    asyncio.run(get_vendor_images())
