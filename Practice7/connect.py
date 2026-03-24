# connect.py
# This file handles CONNECTING to PostgreSQL.
# It also creates the phonebook table if it doesn't exist yet.
#
# WHY a separate file?
#   So we don't repeat connection code everywhere. We just import this module.

import psycopg2                  # The library that lets Python talk to PostgreSQL
from config import DB_CONFIG     # Import our settings from config.py


def get_connection():
    """
    Opens and returns a connection to the PostgreSQL database.
    A 'connection' is like opening a phone line between Python and the database.
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)  # ** unpacks the dictionary as keyword arguments
        return conn
    except psycopg2.OperationalError as e:
        print(f"[ERROR] Could not connect to the database: {e}")
        print("Make sure PostgreSQL is running and your config.py settings are correct.")
        return None


def create_table():
    """
    Creates the 'phonebook' table in the database IF it doesn't already exist.
    
    TABLE STRUCTURE:
        id        → auto-generated unique number for each contact (PRIMARY KEY)
        first_name → the contact's first name
        last_name  → the contact's last name (optional)
        phone      → the phone number (must be unique — no duplicate numbers)
    """
    conn = get_connection()
    if conn is None:
        return  # Stop if we couldn't connect

    try:
        cursor = conn.cursor()  # A cursor is like a "pen" that executes SQL commands

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS phonebook (
                id         SERIAL PRIMARY KEY,
                first_name VARCHAR(50)  NOT NULL,
                last_name  VARCHAR(50),
                phone      VARCHAR(20)  UNIQUE NOT NULL
            );
        """)
        # SERIAL      → auto-increments: 1, 2, 3, 4 ... automatically
        # PRIMARY KEY → each row has a unique identifier
        # NOT NULL    → this field cannot be empty
        # UNIQUE      → no two rows can have the same phone number

        conn.commit()  # IMPORTANT: save the changes to the database
        print("[OK] Table 'phonebook' is ready.")

    except Exception as e:
        print(f"[ERROR] Could not create table: {e}")
        conn.rollback()  # Undo any partial changes if something went wrong

    finally:
        cursor.close()  # Close the pen
        conn.close()    # Close the phone line


# This runs only when you execute this file directly: python connect.py
if __name__ == "__main__":
    create_table()