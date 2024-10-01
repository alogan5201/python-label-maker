import os
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from textwrap import wrap

def load_config():
    with open('data/config.json', 'r') as f:
        return json.load(f)

def inches_to_points(inches):
    return inches * 72

def create_label_pdf(config):
    # Load configuration
    page_width, page_height = letter  # Assuming letter size is always used
    label_width = inches_to_points(config['label']['width'])
    label_height = inches_to_points(config['label']['height'])
    
    x_margin = inches_to_points(config['layout']['left_margin'])
    y_margin = inches_to_points(config['layout']['top_margin'])
    x_gap = inches_to_points(config['layout']['horizontal_spacing'])
    y_gap = inches_to_points(config['layout']['vertical_spacing'])
    
    columns = config['layout']['columns']
    rows = config['layout']['rows']
    
    # Register fonts
    for font in config['fonts'].values():
        font_path = os.path.join(os.path.dirname(__file__), '..', font['file'])
        pdfmetrics.registerFont(TTFont(font['name'], font_path))
    
    # Create canvas
    c = canvas.Canvas(config['output']['filename'], pagesize=letter)
    
    # Get list of images
    image_dir = config['input']['image_directory']
    images = [os.path.join(image_dir, img) for img in os.listdir(image_dir) if img.endswith('.png')]
    
    for row in range(rows):
        for col in range(columns):
            x = x_margin + col * (label_width + x_gap)
            y = page_height - y_margin - (row + 1) * (label_height + y_gap)
            
            # Draw label boundary for debugging
            if config['debug']['draw_borders']:
                c.setStrokeColorRGB(*config['debug']['border_color'])
                c.setLineWidth(config['debug']['border_width'])
                c.rect(x, y, label_width, label_height, stroke=1, fill=0)
            
            # Reset to black for text elements
            c.setStrokeColorRGB(0, 0, 0)
            c.setFillColorRGB(0, 0, 0)
            
            # Product code
            product_code_config = config['content']['product_code']
            c.setFont(product_code_config['font'], product_code_config['size'])
            product_code = "LAB-024-BK"  # This should come from your data source
            text_width = c.stringWidth(product_code, product_code_config['font'], product_code_config['size'])
            text_x = x + (label_width - text_width) / 2
            c.drawString(text_x, y + label_height - 25, product_code)
            
            # Product image
            if images:
                image_path = images.pop(0)
                img = Image.open(image_path)
                img_width, img_height = img.size
                aspect = img_height / float(img_width)
                
                desired_img_height = label_height * config['content']['image']['height_percentage']
                img_width = desired_img_height / aspect
                img_x = x + config['content']['image']['padding']
                img_y = y + (label_height - desired_img_height) / 2
                
                c.drawImage(ImageReader(image_path), img_x, img_y, width=img_width, height=desired_img_height)
                
                text_start_x = img_x + img_width + config['content']['image']['padding']
            else:
                text_start_x = x + config['content']['image']['padding']
            
            # Product description
            desc_config = config['content']['description']
            c.setFont(desc_config['font'], desc_config['size'])
            description = "ACCESSORY, BRASS - BLACK, MICRO, RECESSED, CIRCULAR, FLUSH"  # This should come from your data source
            wrapped_desc = wrap(description, width=desc_config['max_width'])
            for i, line in enumerate(wrapped_desc):
                c.drawString(text_start_x, y + label_height - 50 - (i * 10), line)

    c.save()
    return config['output']['filename']

if __name__ == "__main__":
    config = load_config()
    # pdf_path = create_label_pdf(config)
        
