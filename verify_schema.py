import sqlite3
import os

db_path = 'db.sqlite3'
output_file = 'schema_verification.txt'

with open(output_file, 'w') as f:
    if not os.path.exists(db_path):
        f.write(f"Database not found at {db_path}\n")
    else:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        f.write("Tables in database:\n")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table in tables:
            f.write(f" - {table[0]}\n")
        
        if ('store_product',) in [t for t in tables]:
            f.write("\nColumns in store_product:\n")
            cursor.execute("PRAGMA table_info(store_product)")
            columns = cursor.fetchall()
            for col in columns:
                f.write(f" - {col[1]} ({col[2]})\n")
        else:
            f.write("\nTable store_product not found.\n")
        
        conn.close()
    f.write("\nVerification complete.\n")
