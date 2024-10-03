import asyncio
from . import file_utils
from . import label_maker
from . import get_items
from icecream import ic

async def main():
    ic("Welcome to python_label_maker!")
    
    # Load configuration
    config = file_utils.load_config()
    
    # Create labels
    label_maker.create_label_pdf(config)
    await get_items.get_items()


if __name__ == "__main__":
    asyncio.run(main())