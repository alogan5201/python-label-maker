import asyncio
from . import file_utils
from . import label_maker
from . import get_items
from icecream import ic
from loguru import logger

async def main():
    
    
    # Load configuration
    config = file_utils.load_config()
    
    # * Retrieve items from NetSuite and store in database
    await get_items.get_items()
    
    # Create labels
    label_maker.create_label_pdf(config)


if __name__ == "__main__":
    asyncio.run(main())