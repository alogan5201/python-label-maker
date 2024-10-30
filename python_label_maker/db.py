import sqlite3
import os
from loguru import logger
from icecream import ic
# Database file name
db_file = "db.sqlite"

def create_database_and_table():
    # Check if the database file already exists
    db_exists = os.path.exists(db_file)

    # Connect to the database
    conn = sqlite3.connect(db_file)
    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()
    # Create the 'items' table if it doesn't exist
    create_table_sql = '''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        company TEXT,
        item_img TEXT,
        manufacturer TEXT
    )
    '''

    # Execute the SQL command
    cursor.execute(create_table_sql)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    # Print a message about what was done
    logger.info(f"Connected to database from: {db_file}")
    
def insert_item(name, description, company_img_url, item_img_url, manufacturer):
    if not name:
        ic("Error: Name cannot be empty")
        return

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    try:
        # Ensure the table exists
        create_database_and_table()

        # Check if an item with the same name already exists
        check_sql = 'SELECT id FROM items WHERE name = ?'
        cursor.execute(check_sql, (name,))
        existing_item = cursor.fetchone()

        if existing_item:
            logger.info(f"Item '{name}' exists. Skipped.")
        else:
            insert_sql = '''
            INSERT INTO items (name, description, company_img, item_img, manufacturer)
            VALUES (?, ?, ?, ?, ?)
            '''
            cursor.execute(insert_sql, (name, description, company_img_url, item_img_url, manufacturer))
            conn.commit()
            logger.info(f"Inserted item: {name}")

    except sqlite3.IntegrityError as e:
        logger.error(f"Integrity Error: {e}")
    except sqlite3.Error as e:
        logger.error(f"Database Error: {e}")
    finally:
        conn.close()

def get_cached_items():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    try:
        # SQL query to select all records from the items table
        select_all_sql = 'SELECT * FROM items'
        
        # Execute the query
        cursor.execute(select_all_sql)
        
        # Fetch all records
        rows = cursor.fetchall()
        
        # Get column names
        column_names = [description[0] for description in cursor.description]
        
        # Convert rows to list of dictionaries
        items = [dict(zip(column_names, row)) for row in rows]
        
        # Return the items
        return items

    except sqlite3.Error as e:
        ic(f"Database Error: {e}")
        return []

    finally:
        conn.close()

# Create the database and table
create_database_and_table()
# Example usage of the insert_item function
# insert_item(
#     name="Sample Item",
#     description="This is a sample item description.",
#     company_img_url="https://example.com/company_logo.png",
#     item_img_url="https://example.com/item_image.jpg"
# )