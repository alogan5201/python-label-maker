import sys
from PIL import Image

def replace_color(image_path, color_to_replace, new_color, output_path):
    # Open the image
    img = Image.open(image_path)
    
    # Convert the image to RGBA if it's not already
    img = img.convert('RGBA')
    
    # Get the image data
    data = img.getdata()
    
    # Convert colors to RGBA tuples
    color_to_replace = tuple(color_to_replace)
    new_color = tuple(new_color)
    
    # Create a new list to store the modified pixel data
    new_data = []
    
    # Replace the color
    for item in data:
        if item[:3] == color_to_replace[:3]:  # Compare RGB values
            new_data.append(new_color[:3] + (item[3],))  # Keep original alpha
        else:
            new_data.append(item)
    
    # Update the image with the new data
    img.putdata(new_data)
    
    # Save the modified image
    img.save(output_path)
    print(f"Modified image saved as {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python script.py <input_image> <color_to_replace> <new_color> <output_image>")
        print("Colors should be in R,G,B format (e.g., 255,255,255 for white)")
        sys.exit(1)
    
    input_image = sys.argv[1]
    color_to_replace = [int(x) for x in sys.argv[2].split(',')]
    new_color = [int(x) for x in sys.argv[3].split(',')]
    output_image = sys.argv[4]
    
    replace_color(input_image, color_to_replace, new_color, output_image)