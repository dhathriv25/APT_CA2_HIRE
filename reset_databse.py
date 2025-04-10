"""
Script to clear all entries from the HIRE platform database.
This directly uses SQLite3 to ensure all data is removed.
"""

import sqlite3
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# The database is in the 'instance' folder
db_path = os.path.join('instance', 'hire.db')

print(f"Connecting to database at: {db_path}")

try:
    # Check if the database file exists
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        exit(1)
        
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable foreign keys support
    cursor.execute("PRAGMA foreign_keys = OFF")
    
    # Get a list of all tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = cursor.fetchall()
    
    print(f"Found {len(tables)} tables in the database")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Delete data from each table in an order that respects foreign key constraints
    # We'll manually specify the order to ensure dependencies are handled correctly
    
    # List of tables to clear in the correct order
    tables_to_clear = [
        "otp_verifications", 
        "payments",
        "bookings",
        "addresses",
        "provider_categories",
        "customers", 
        "providers"
        # Keeping service_categories as these are needed for the application
    ]
    
    # Clear each table
    for table in tables_to_clear:
        try:
            print(f"Clearing table: {table}")
            cursor.execute(f"DELETE FROM {table}")
            print(f"  Deleted {cursor.rowcount} rows")
        except sqlite3.Error as e:
            print(f"  Error clearing table {table}: {e}")
    
    # Commit the changes
    conn.commit()
    
    # Re-enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Vacuum the database to reclaim space and reset auto-increment counters
    print("Vacuuming database to reclaim space...")
    cursor.execute("VACUUM")
    
    print("Database entries successfully cleared!")
    
except sqlite3.Error as e:
    print(f"SQLite error: {e}")
finally:
    if 'conn' in locals() and conn:
        conn.close()