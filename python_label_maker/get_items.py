import os
import json
from netsuite import NetSuite, Config, TokenAuth
from typing import List
from pydantic import BaseModel
import asyncio
import pprint
import re
import base64
from icecream import ic
from PIL import Image
from io import BytesIO
import requests
from .db import insert_item

def load_config():
    with open('data/config.json', 'r') as f:
        return json.load(f)

config = load_config()

def extract_file_id(url):
    # Use regex to extract the value of the 'id' parameter
    match = re.search(r'id=(\d+)', url)
    if match:
        return match.group(1)  # Return the file ID
    return None

def base64_to_image(base64_string):
    # Remove the data URI prefix if present
    if "data:image" in base64_string:
        base64_string = base64_string.split(",")[1]

    # Decode the Base64 string into bytes
    image_bytes = base64.b64decode(base64_string)
    return image_bytes

def create_image_from_bytes(image_bytes):
    # Create a BytesIO object to handle the image data
    image_stream = BytesIO(image_bytes)

    # Open the image using Pillow (PIL)
    image = Image.open(image_stream)
    return image

# Fetch TokenAuth parameters from environment variables
consumer_key = os.getenv("NETSUITE_CONSUMER_KEY")
consumer_secret = os.getenv("NETSUITE_CONSUMER_SECRET")
token_id = os.getenv("NETSUITE_TOKEN_ID")
token_secret = os.getenv("NETSUITE_TOKEN_SECRET")
account = os.getenv("NETSUITE_ACCOUNT")

# Ensure all necessary environment variables are available
if not all([consumer_key, consumer_secret, token_id, token_secret]):
    raise EnvironmentError("One or more NetSuite TokenAuth environment variables are not set.")

# Configuring NetSuite with TokenAuth sourced from environment variables
ns_config = Config(
    account="7313488_SB1",  # Ensure this matches your actual NetSuite account ID
    auth=TokenAuth(consumer_key=consumer_key, consumer_secret=consumer_secret, token_id=token_id, token_secret=token_secret),
)
ns = NetSuite(ns_config)

async def process_data(query: dict):
    try:
        restlet_response = await ns.restlet.post(script_id=1171, deploy=1, body=query)
        return restlet_response
    except Exception as e:
        print(f"Error calling RESTlet: {e}")

def prprint(data):
    return pprint.pprint(data)

async def getRecord(id):
    query = {
        "procedure": "recordGet",
          "type": "inventoryitem",
           "id": id
      }
    record = await process_data(query)
    return record

async def get_file(id):
    query = {
        "procedure": "fileGet",
        "id": id
    }
    file = await process_data(query)
    return file

def get_first_word(text: str) -> str:
    # Split the text by whitespace and return the first word
    return text.split()[0] if text else ""

async def get_items():
    limit_results = "FETCH FIRST 5 ROWS ONLY;"
    query = {
        "procedure": "queryRun",
        "query": f"SELECT item.id AS id, item.itemid AS name, item.displayName AS display_name, item.purchasedescription as description, item.manufacturer AS manufacturer, item.custitem_jls_item_image_url AS item_img FROM item WHERE item.manufacturer = ? {limit_results}",
        "params": ["LUMIEN LIGHTING"],  # Use the MANUFACTURER variable
    }
    items = await process_data(query)
    
    # Ensure the path is correct and exists
    item_image_directory = os.path.join('input', 'images', 'items')
    os.makedirs(item_image_directory, exist_ok=True)
    company_image_directory = os.path.join('input', 'images', 'companies')
    os.makedirs(company_image_directory, exist_ok=True)
    records = items.get('records')
    if records:
        for item in records:
            image = item.get('item_img')
            name = item.get('name')
            description = item.get('description')
            display_name = item.get('display_name')
            manufacturer = item.get('manufacturer')
            if image:
                image_url = f"https://{account}.app.netsuite.com{image}"
                # if "LUMIEN" in manufacturer:
                # Extract the first word from the manufacturer and lowercase it
                company_name = manufacturer.split()[0].lower()
                # Check if there is a file with the company name in the company image directory
                company_image_path = os.path.join(company_image_directory, f"{company_name}.png")
                ic(company_image_path)
                company_logo_links = {
                    "lumien": "https://i.imgur.com/cxcXM5J.png"
                }
                # Check if the company name exists in manufacturer_logo_links
                if company_name in company_logo_links:
                    company_logo_url = company_logo_links[company_name]
                    ic(f"Found logo URL for {company_name}: {company_logo_url}")
                    # Writes the item record to the database
                    if company_logo_url:
                        insert_item(
                            name=display_name,
                            description=description,
                            company_img_url=company_logo_url,
                            item_img_url=image_url
                        )                         
                else:
                    ic(f"No logo URL found for {company_name}")
                
        else:
            ic(name)

def to_snake_case(text: str) -> str:
    # Replace any non-alphanumeric characters with underscores
    snake_case = re.sub(r'[^\w\s]', '_', text)
    # Replace spaces with underscores
    snake_case = re.sub(r'\s+', '_', snake_case)
    # Convert to lowercase and remove any consecutive underscores
    return re.sub(r'_+', '_', snake_case.lower()).strip('_')
