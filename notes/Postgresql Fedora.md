### How to get your database ready for use with your FastAPI application:

1. Start the PostgreSQL service if you haven't already:

   ```
   sudo systemctl start postgresql
   sudo systemctl enable postgresql
   ```

2. Switch to the postgres user to access the PostgreSQL prompt:

   ```
   sudo -iu postgres
   ```

3. Create a new database for your application:

   ```
   createdb jls_items
   ```

   Replace `jls_items` with a name that fits your project.

4. Create a new user for your application:

   ```
   createuser --interactive --pwprompt
   ```

   Follow the prompts to set the username and password.

5. Grant privileges to the new user on the new database:

   ```
   psql
   ```

   Then in the PostgreSQL prompt:

   ```sql
   GRANT ALL PRIVILEGES ON DATABASE jls_items TO developer;
   ```

6. Exit the PostgreSQL prompt and the postgres user:

   ```
   \q
   exit
   ```

7. Modify PostgreSQL configuration to allow password authentication:

   ```
   sudo nano /var/lib/pgsql/data/pg_hba.conf
   ```

   Find the lines that look like this:

   ```
   # IPv4 local connections:
   host    all             all             127.0.0.1/32            ident
   # IPv6 local connections:
   host    all             all             ::1/128                 ident
   ```

   Change `ident` to `md5` for both IPv4 and IPv6 connections.

8. Restart PostgreSQL to apply changes:

   ```
   sudo systemctl restart postgresql
   ```

9. Test the connection:

   ```
   psql -h localhost -U developer -d jls_items
   ```

   You should be prompted for the password you set earlier.

10. In your FastAPI application, you can use SQLAlchemy to connect to the database. Here's a basic setup:

    ```python
    from sqlalchemy import create_engine
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker

    SQLALCHEMY_DATABASE_URL = "postgresql://developer:your_password@localhost/jls_items"

    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base = declarative_base()
    ```

Remember to replace `developer`, `your_password`, and `jls_items` with the actual values you used during setup.

Also, make sure to install the necessary Python packages:

```
pip install sqlalchemy psycopg2-binary
```

This setup should give you a working PostgreSQL database that your FastAPI application can connect to. Let me know if you need any clarification or run into any issues!
