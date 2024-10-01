import os
from pathlib import Path
import json

# Define base paths
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / 'output'
INPUT_DIR = BASE_DIR / 'input'
DATA_DIR = BASE_DIR / 'data'

def save_manufacturer_logo(manufacturer_name, logo_data):
    logo_path = OUTPUT_DIR / 'images' / 'manufacturer_logos' / f"{manufacturer_name}.png"
    logo_path.parent.mkdir(parents=True, exist_ok=True)
    with open(logo_path, 'wb') as f:
        f.write(logo_data)

def save_item_image(item_name, image_data):
    image_path = OUTPUT_DIR / 'images' / 'items' / f"{item_name}.png"
    image_path.parent.mkdir(parents=True, exist_ok=True)
    with open(image_path, 'wb') as f:
        f.write(image_data)

def save_label_pdf(label_name, pdf_data):
    pdf_path = OUTPUT_DIR / 'pdfs' / f"{label_name}.pdf"
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    with open(pdf_path, 'wb') as f:
        f.write(pdf_data)

def load_template(template_name):
    template_path = INPUT_DIR / 'templates' / f"{template_name}.json"
    with open(template_path, 'r') as f:
        return f.read()

def load_config():
    config_path = DATA_DIR / 'config.json'
    with open(config_path, 'r') as f:
        return json.load(f)  # Parse the JSON string into a dictionary