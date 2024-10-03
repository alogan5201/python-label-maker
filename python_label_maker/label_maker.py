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
    c.drawString(text_x, y + label_height - product_code_config['size'] - 5, product_code)

def draw_label(c, x, y, label_width, label_height, config, item):
    """
    Draw a complete label with background image and centered description.

    Args:
        c (canvas.Canvas): The ReportLab canvas object.
        x (float): The x-coordinate of the label.
        y (float): The y-coordinate of the label.
        label_width (float): The width of the label.
        label_height (float): The height of the label.
        config (dict): The configuration dictionary.
        item (dict): The item dictionary containing the product information.
    """
    # Draw background image
    draw_background_image(c, x, y, label_width, label_height, config, item)
    
    # Draw product code
    draw_product_code(c, x, y, label_width, label_height, config, item)
    
    # Calculate the space left for the description
    image_height = label_height * config['content']['image']['height_percentage']
    product_code_height = config['content']['product_code']['size'] + 5
    description_space = label_height - image_height - product_code_height - inches_to_points(0.2)  # 0.2 inches padding
    
    # Draw centered description
    draw_centered_description(c, x, y, label_width, label_height, config, item)
    
    # Draw label border if debug is enabled
    if config['debug']['draw_borders']:
        draw_label_border(c, x, y, label_width, label_height, config)

def draw_background_image(c, x, y, label_width, label_height, config, item):
    """
    Draw the product image aligned to the far-left middle of the label.

    Args:
        c (canvas.Canvas): The ReportLab canvas object.
        x (float): The x-coordinate of the label.
        y (float): The y-coordinate of the label.
        label_width (float): The width of the label.
        label_height (float): The height of the label.
        config (dict): The configuration dictionary.
        item (dict): The item dictionary containing the product information.
    """
    image_url = item['item_img']
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    img_width, img_height = img.size
    aspect = img_height / float(img_width)
    
    # Calculate image dimensions
    image_height = label_height * config['content']['image']['height_percentage']
    image_width = image_height / aspect
    
    # Apply max width constraint
    max_width = inches_to_points(config['content']['image']['max_width'])
    if image_width > max_width:
        image_width = max_width
        image_height = image_width * aspect
    
    # Align the image to the far-left
    img_x = x + config['content']['image']['padding']
    
    # Center the image vertically
    img_y = y + (label_height - image_height) / 2
    
    c.drawImage(ImageReader(img), img_x, img_y, width=image_width, height=image_height)

def draw_centered_description(c, x, y, label_width, label_height, config, item):
    """
    Draw the product description centered vertically and horizontally on the label.

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

    # Set the width to 2.5 inches
    desc_width = inches_to_points(2.5)
    
    # Add horizontal padding
    horizontal_padding = inches_to_points(desc_config['horizontal_padding'])
    
    # Calculate the starting x-coordinate to center the description
    start_x = x + (label_width - desc_width) / 2 + horizontal_padding

    # Wrap the text to fit the new width (accounting for padding)
    wrapped_desc = wrap(description, width=int((desc_width - 4 * horizontal_padding) / (desc_config['size'] / 2)))

    # Calculate the total height of the wrapped text
    line_height = desc_config['size'] + 2  # Add 2 for line spacing
    text_height = len(wrapped_desc) * line_height

    # Calculate the vertical center of the label
    label_center_y = y + label_height / 2

    # Calculate the starting y-coordinate to vertically center the text
    start_y = label_center_y + text_height / 2

    # Draw each line of the wrapped description
    for i, line in enumerate(wrapped_desc):
        line_width = c.stringWidth(line, desc_config['font'], desc_config['size'])
        line_x = x + (label_width - line_width) / 2  # Center each line horizontally
        c.drawString(line_x, start_y - i * line_height, line)

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
        
        draw_label(c, x, y, label_width, label_height, config, item)
        
        if (index + 1) % (columns * rows) == 0:
            c.showPage()  # Start a new page

    c.save()
    return config['output']['filename']

if __name__ == "__main__":
    config = load_config()
    pdf_path = create_label_pdf(config)