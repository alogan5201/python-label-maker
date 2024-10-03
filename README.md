# Python Label Maker

A label maker for NetSuite item records, designed to create custom labels with product information and images.

## Description

Python Label Maker is a tool that interfaces with NetSuite to retrieve item information and generate custom labels. It supports creating labels with product codes, descriptions, and images, formatted according to user-defined configurations.

## Features

- Retrieves item data from NetSuite
- Generates PDF labels with customizable layouts
- Supports multiple fonts and image placement
- Includes debugging options for label creation
- Stores item data in a local SQLite database

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/alogan5201/python_label_maker.git
   cd python_label_maker
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your NetSuite credentials as environment variables:
   - NETSUITE_CONSUMER_KEY
   - NETSUITE_CONSUMER_SECRET
   - NETSUITE_TOKEN_ID
   - NETSUITE_TOKEN_SECRET
   - NETSUITE_ACCOUNT

## Usage

To run the label maker:

```
python -m python_label_maker.main
```

## Configuration

The `data/config.json` file contains various settings for label layout, fonts, and output options. Modify this file to customize your label output.

## Project Structure

```
python_label_maker/
│
├── python_label_maker/
│   ├── __init__.py
│   ├── main.py
│   ├── label_maker.py
│   ├── get_items.py
│   ├── db.py
│   └── file_utils.py
│
├── tests/
│   ├── __init__.py
│   └── test_module1.py
│
├── docs/
│   └── documentation.md
│
├── output/
│   ├── images/
│   └── pdfs/
│
├── input/
│   └── templates/
│
├── data/
│   └── config.json
│
├── requirements.txt
├── setup.py
├── README.md
└── .gitignore
```

## License

This project is proprietary and not open-source. All rights reserved.

## Contact

Andrew Logan - drewthomaslogan5201@gmail.com

Project Link: [https://github.com/alogan5201/python_label_maker](https://github.com/alogan5201/python_label_maker)
