import sys
sys.stdout.reconfigure(encoding='utf-8')

from db_connection import get_db_connection, get_cursor

conn = get_db_connection()
cursor = get_cursor(conn)

tables = ['Supplier', 'Product', 'Inventory_Record', 'Promotion', 'Sales', 'Sales_Items',
          'Warehouse', 'audit_log', 'external_factor', 'prediction_model', 'Customer', 'Sales_Data']

for t in tables:
    try:
        cursor.execute(f"DESCRIBE {t}")
        cols = cursor.fetchall()
        print(f"\n=== {t} ===")
        for c in cols:
            print(f"  {c['Field']} | {c['Type']} | Null={c['Null']} | Key={c['Key']} | Default={c['Default']}")
    except Exception as e:
        print(f"\n=== {t} === ERROR: {e}")

conn.close()
