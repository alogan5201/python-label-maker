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
    
    # * Retrieve items from NetSuite and store in database
    await get_items.get_items()
    
    # * Retrieves items from database
    items = db.get_all_items()
    if items and len(items) > 0:
        ic(items)
        # Create labels
        # label_maker.create_label_pdf(config)

    


if __name__ == "__main__":
    asyncio.run(main())