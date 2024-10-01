from . import file_utils
from . import label_maker
from icecream import ic

def main():
    ic("Welcome to python_label_maker!")
    
    # Load configuration
    config = file_utils.load_config()
    
    # Create labels
    label_maker.create_label_pdf(config)
    ic("Label PDF created:")
    ic(config['output']['filename'])


if __name__ == "__main__":
    main()