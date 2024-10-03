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
    Draw a border around the label if debug mode is enabled.

    Args:
        c (canvas.Canvas): The ReportLab canvas object.
        x (float): The x-coordinate of the label.
        y (float): The y-coordinate of the label.
        width (float): The width of the label.
        height (float): The height of the label.
        config (dict): The configuration dictionary.
    """
    if config['debug']['draw_borders']:
        c.setStrokeColorRGB(*config['debug']['border_color'])
        c.setLineWidth(config['debug']['border_width'])
        c.rect(x, y, width, height, stroke=1, fill=0)
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)

def draw_product_code(c, x, y, label_width, label_height, config):
    """
    Draw the product code on the label.

    Args:
        c (canvas.Canvas): The ReportLab canvas object.
        x (float): The x-coordinate of the label.
        y (float): The y-coordinate of the label.
        label_width (float): The width of the label.
        label_height (float): The height of the label.
        config (dict): The configuration dictionary.
    """
    product_code_config = config['content']['product_code']
    c.setFont(product_code_config['font'], product_code_config['size'])
    product_code = "LAB-024-FUCK"  # This should come from your data source
    text_width = c.stringWidth(product_code, product_code_config['font'], product_code_config['size'])
    text_x = x + (label_width - text_width) / 2
    c.drawString(text_x, y + label_height - 25, product_code)

def draw_product_image(c, x, y, label_width, label_height, image_path, config):
    """
    Draw the product image on the label.

    Args:
        c (canvas.Canvas): The ReportLab canvas object.
        x (float): The x-coordinate of the label.
        y (float): The y-coordinate of the label.
        label_width (float): The width of the label.
        label_height (float): The height of the label.
        image_path (str): The path to the product image.
        config (dict): The configuration dictionary.

    Returns:
        float: The x-coordinate where the text should start after the image.
    """
    img = Image.open(image_path)
    img_width, img_height = img.size
    aspect = img_height / float(img_width)
    
    desired_img_height = label_height * config['content']['image']['height_percentage']
    img_width = desired_img_height / aspect
    img_x = x + config['content']['image']['padding']
    img_y = y + (label_height - desired_img_height) / 2
    
    c.drawImage(ImageReader(image_path), img_x, img_y, width=img_width, height=desired_img_height)
    return img_x + img_width + config['content']['image']['padding']

def draw_product_description(c, x, y, label_height, config):
    """
    Draw the product description on the label.

    Args:
        c (canvas.Canvas): The ReportLab canvas object.
        x (float): The x-coordinate to start drawing the description.
        y (float): The y-coordinate of the label.
        label_height (float): The height of the label.
        config (dict): The configuration dictionary.
    """
    desc_config = config['content']['description']
    c.setFont(desc_config['font'], desc_config['size'])
    description = "ACCESSORY, BRASS - BLACK, MICRO, RECESSED, CIRCULAR, FLUSH"  # This should come from your data source
    wrapped_desc = wrap(description, width=desc_config['max_width'])
    for i, line in enumerate(wrapped_desc):
        c.drawString(x, y + label_height - 50 - (i * 10), line)

def create_label_pdf(config):
    """
    Create a PDF file with labels based on the provided configuration.

    Args:
        config (dict): The configuration dictionary.

    Returns:
        str: The path to the created PDF file.
    """
    items = get_all_items()
    logger.success(items)
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
    
    image_dir = config['input']['item_image_directory']
    images = [os.path.join(image_dir, img) for img in os.listdir(image_dir) if img.endswith('.png')]
    
    for row in range(rows):
        for col in range(columns):
            x = x_margin + col * (label_width + x_gap)
            y = page_height - y_margin - (row + 1) * (label_height + y_gap)
            
            draw_label_border(c, x, y, label_width, label_height, config)
            draw_product_code(c, x, y, label_width, label_height, config)
            
            if images:
                text_start_x = draw_product_image(c, x, y, label_width, label_height, images.pop(0), config)
            else:
                text_start_x = x + config['content']['image']['padding']
            
            draw_product_description(c, text_start_x, y, label_height, config)

    c.save()
    return config['output']['filename']

if __name__ == "__main__":
    config = load_config()
    pdf_path = create_label_pdf(config)