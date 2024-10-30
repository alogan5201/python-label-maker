import asyncio
from . import file_utils  # Module to handle file operations, including loading configurations
from . import label_maker  # Module responsible for creating label PDFs
from . import get_items  # Module to retrieve items from an external source (NetSuite)
from icecream import ic  # Debugging tool for printing values with context
from loguru import logger  # Logging library for structured logging
from . import db  # Module to handle database operations for caching items

async def main():
    """
    Main asynchronous function that orchestrates the label PDF generation process:
    1. Loads the configuration settings.
    2. Retrieves and caches items from NetSuite.
    3. Processes items in chunks to generate PDFs with specific layout settings.
    """    
    
    config = file_utils.load_config()  # Dictionary containing layout and output settings
    
    # Retrieve items from Netsuite and cache it locally
    await get_items.get_items()
    
    # Retrieve items from cache
    items = db.get_cached_items()

    if items and len(items) > 0:
        # Determine the number of items per PDF page based on layout settings
        items_per_pdf = config['layout']['columns'] * config['layout']['rows']
        
        # Process items in batches to fit the defined layout per PDF
        for i in range(0, len(items), items_per_pdf):
            sublist = items[i:i + items_per_pdf]
            
            # Set the pdf file name
            first_item_name = sublist[0]['name'].replace(' ', '_').lower()
            last_item_name = sublist[-1]['name'].replace(' ', '_').lower()
            pdf_filename = f"{first_item_name}_to_{last_item_name}.pdf"            
            config['output']['filename'] = f"output/pdfs/{pdf_filename}"
    
            # Generate a PDF with labels for the items in the current set
            label_maker.create_label_pdf(config, sublist)
            
            # Log the creation of the new PDF
            logger.info(f"Created PDF: {pdf_filename}")

# Run the main function asynchronously if the script is executed as the main program
if __name__ == "__main__":
    asyncio.run(main())
