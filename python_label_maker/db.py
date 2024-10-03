import sqlite3
import os
from icecream import ic

# Database file name
db_file = "db.sqlite"

def create_database_and_table():
    # Check if the database file already exists
    db_exists = os.path.exists(db_file)

    # Connect to the database (this will create it if it doesn't exist)
    conn = sqlite3.connect(db_file)

    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()

    # SQL command to create the 'items' table if it doesn't exist
    create_table_sql = '''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        company TEXT,
        item_img TEXT
    )
    '''

    # Execute the SQL command
    cursor.execute(create_table_sql)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    # Print a message about what was done
    if db_exists:
        print(f"Connected to existing database: {db_file}")
    else:
        print(f"Created new database: {db_file}")
    print("Ensured 'items' table exists with all required columns.")

def insert_item(name, description, company_img_url, item_img_url):
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
            ic(f"Item with name '{name}' already exists. Skipping insertion.")
        else:
            insert_sql = '''
            INSERT INTO items (name, description, company_img, item_img)
            VALUES (?, ?, ?, ?)
            '''
            cursor.execute(insert_sql, (name, description, company_img_url, item_img_url))
            conn.commit()
            ic(f"Inserted new item: {name}")

    except sqlite3.IntegrityError as e:
        ic(f"Integrity Error: {e}")
    except sqlite3.Error as e:
        ic(f"Database Error: {e}")
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