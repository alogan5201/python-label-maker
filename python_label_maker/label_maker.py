import os
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from textwrap import wrap
from .db import get_all_items
from icecream import ic
from loguru import logger
import requests
from io import BytesIO

def load_config():
    """
    Load the configuration from the JSON file.

    Returns:
        dict: The configuration data.
    """
    with open('data/config.json', 'r') as f:
        return json.load(f)

def inches_to_points(inches):
    """
    Convert inches to points.

    Args:
        inches (float): The value in inches.

    Returns:
        float: The value in points.
    """
    return inches * 72

def register_fonts(fonts):
    """
    Register custom fonts for use in the PDF.

    Args:
        fonts (dict): A dictionary of font configurations.
    """
    for font in fonts.values():
        font_path = os.path.join(os.path.dirname(__file__), '..', font['file'])
        pdfmetrics.registerFont(TTFont(font['name'], font_path))

def draw_label_border(c, x, y, width, height, config):
    """
    Draw a border around the label.

    Args:
        c (canvas.Canvas): The ReportLab canvas object.
        x (float): The x-coordinate of the label.
        y (float): The y-coordinate of the label.
        width (float): The width of the label.
        height (float): The height of the label.
        config (dict): The configuration dictionary.
    """
    c.setStrokeColorRGB(*config['debug']['border_color'])
    c.setLineWidth(config['debug']['border_width'])
    c.rect(x, y, width, height, stroke=1, fill=0)
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)

def draw_product_code(c, x, y, label_width, label_height, config, item):
    """
    Draw the product code on the label.

    Args:
        c (canvas.Canvas): The ReportLab canvas object.
        x (float): The x-coordinate of the label.
        y (float): The y-coordinate of the label.
        label_width (float): The width of the label.
        label_height (float): The height of the label.
        config (dict): The configuration dictionary.
        item (dict): The item dictionary containing the product information.
    """
    product_code_config = config['content']['product_code']
    c.setFont(product_code_config['font'], product_code_config['size'])
    product_code = item['name']
    text_width = c.stringWidth(product_code, product_code_config['font'], product_code_config['size'])
    text_x = x + (label_width - text_width) / 2
    c.drawString(text_x, y + label_height - 25, product_code)

def draw_product_image(c, x, y, label_width, label_height, config, item):
    """
    Draw the product image on the label.

    Args:
        c (canvas.Canvas): The ReportLab canvas object.
        x (float): The x-coordinate of the label.
        y (float): The y-coordinate of the label.
        label_width (float): The width of the label.
        label_height (float): The height of the label.
        config (dict): The configuration dictionary.
        item (dict): The item dictionary containing the product information.

    Returns:
        float: The x-coordinate where the text should start after the image.
    """
    image_url = item['item_img']
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    img_width, img_height = img.size
    aspect = img_height / float(img_width)
    
    desired_img_height = label_height * config['content']['image']['height_percentage']
    img_width = desired_img_height / aspect
    img_x = x + config['content']['image']['padding']
    img_y = y + (label_height - desired_img_height) / 2
    
    c.drawImage(ImageReader(img), img_x, img_y, width=img_width, height=desired_img_height)
    return img_x + img_width + config['content']['image']['padding']

def draw_product_description(c, x, y, label_width, label_height, config, item):
    """
    Draw the product description on the label with left alignment.

    Args:
        c (canvas.Canvas): The ReportLab canvas object.
        x (float): The x-coordinate of the label.
        y (float): The y-coordinate of the label.
        label_width (float): The width of the label.
        label_height (float): The height of the label.
        config (dict): The configuration dictionary.
        item (dict): The item dictionary containing the product information.
    """
    desc_config = config['content']['description']
    c.setFont(desc_config['font'], desc_config['size'])
    description = item['description']

    # Calculate available width for description
    image_width = label_height * config['content']['image']['height_percentage']
    available_width = label_width - image_width - 3 * config['content']['image']['padding']

    # Wrap the text to fit the available width
    wrapped_desc = wrap(description, width=int(available_width / (desc_config['size'] / 2)))

    # Calculate the total height of the wrapped text
    line_height = desc_config['size'] + 2  # Add 2 for line spacing
    text_height = len(wrapped_desc) * line_height

    # Calculate the starting y-coordinate to center the text vertically
    start_y = y + (label_height - text_height) / 2 + text_height

    # Calculate the left-aligned x-coordinate for the text
    text_x = x + image_width + 2 * config['content']['image']['padding']

    for i, line in enumerate(wrapped_desc):
        c.drawString(text_x, start_y - i * line_height, line)

def get_image_dimensions(image_url):
    """
    Fetch an image from a URL and return its dimensions.

    Args:
        image_url (str): The URL of the image.

    Returns:
        tuple: A tuple containing the width and height of the image.
    """
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    return img.size

def create_label_pdf(config, items):
    """
    Create a PDF file with labels based on the provided configuration and items.

    Args:
        config (dict): The configuration dictionary.
        items (list): A list of item dictionaries to create labels for.

    Returns:
        str: The path to the created PDF file.
    """
    page_width, page_height = letter
    label_width = inches_to_points(config['label']['width'])
    label_height = inches_to_points(config['label']['height'])
    
    x_margin = inches_to_points(config['layout']['left_margin'])
    y_margin = inches_to_points(config['layout']['top_margin'])
    x_gap = inches_to_points(config['layout']['horizontal_spacing'])
    y_gap = inches_to_points(config['layout']['vertical_spacing'])
    
    columns, rows = config['layout']['columns'], config['layout']['rows']
    
    register_fonts(config['fonts'])
    
    c = canvas.Canvas(config['output']['filename'], pagesize=letter)
    
    for index, item in enumerate(items):
        row = index // columns
        col = index % columns
        
        x = x_margin + col * (label_width + x_gap)
        y = page_height - y_margin - (row + 1) * (label_height + y_gap)
        
        draw_label_border(c, x, y, label_width, label_height, config)
        draw_product_code(c, x, y, label_width, label_height, config, item)
        
        # Get image dimensions
        img_width, img_height = get_image_dimensions(item['item_img'])
        
        # Calculate the width taken by the image
        desired_img_height = label_height * config['content']['image']['height_percentage']
        image_width = (desired_img_height / img_height) * img_width
        image_width += 2 * config['content']['image']['padding']
        
        # Adjust x-coordinate and width for description
        desc_x = x + image_width
        desc_width = label_width - image_width
        
        draw_product_image(c, x, y, label_width, label_height, config, item)
        draw_product_description(c, desc_x, y, desc_width, label_height, config, item)
        
        if (index + 1) % (columns * rows) == 0:
            c.showPage()  # Start a new page

    c.save()
    return config['output']['filename']

if __name__ == "__main__":
    config = load_config()
    pdf_path = create_label_pdf(config)