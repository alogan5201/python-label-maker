import asyncio
from . import file_utils
from . import label_maker
from . import get_items
from icecream import ic
from loguru import logger
from . import db

async def main():
    # Load configuration
    config = file_utils.load_config()
    
    # Retrieve items from NetSuite and store in database
    await get_items.get_items()
    
    # Retrieve items from database
    items = db.get_all_items()
    if items and len(items) > 0:
        
        # Calculate the number of items per PDF
        items_per_pdf = config['layout']['columns'] * config['layout']['rows']
        
        # Create labels
        for i in range(0, len(items), items_per_pdf):
            sublist = items[i:i+items_per_pdf]
            pdf_filename = f"labels_batch_{i//items_per_pdf + 1}.pdf"
            config['output']['filename'] = f"output/pdfs/{pdf_filename}"
            label_maker.create_label_pdf(config, sublist)
            logger.info(f"Created PDF: {pdf_filename}")

if __name__ == "__main__":
    asyncio.run(main())