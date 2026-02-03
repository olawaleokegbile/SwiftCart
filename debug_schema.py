import sqlite3
import os

db_path = 'db.sqlite3'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Tables in database:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        print(f" - {table[0]}")
    
    if ('store_product',) in tables:
        print("\nColumns in store_product:")
        cursor.execute("PRAGMA table_info(store_product)")
        columns = cursor.fetchall()
        for col in columns:
            print(f" - {col[1]} ({col[2]})")
    else:
        print("\nTable store_product not found.")
    
    conn.close()
