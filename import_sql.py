import os
import sys

# Remove DEFINERs from SQL
sql_file = r"C:\Users\Kush\Desktop\smart_retail_dump.sql"
with open(sql_file, 'r', encoding='utf-8') as f:
    sql_script = f.read()

# TiDB and other cloud providers often reject DEFINER=`root`@`localhost`
sql_script = sql_script.replace("DEFINER=`root`@`localhost`", "")

sys.path.insert(0, 'src')
from db_connection import get_db_connection

print("Connecting to TiDB...")
conn = get_db_connection()
cursor = conn.cursor()

print("Executing SQL script...")
try:
    for result in cursor.execute(sql_script, multi=True):
        if result.with_rows:
            result.fetchall()
    conn.commit()
    print("Successfully imported the database to TiDB!")
except Exception as e:
    print(f"Error executing SQL: {e}")
finally:
    cursor.close()
    conn.close()
