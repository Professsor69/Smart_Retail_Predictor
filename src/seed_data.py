import mysql.connector
import random
from db_connection import get_db_connection

def seed_inventory_data():
    try:
        # Use the connection from your db_connection file
        conn = get_db_connection()
        cursor = conn.cursor()
        print("🌱 Connection successful! Adding Warehouse and Inventory...")

        # 1. Add a Warehouse
        sql_warehouse = "INSERT INTO Warehouse (Location, Capacity) VALUES (%s, %s)"
        cursor.execute(sql_warehouse, ("Central Hub - Mumbai", 10000))
        warehouse_id = cursor.lastrowid 

        # 2. Get Product IDs
        cursor.execute("SELECT Product_ID FROM Product")
        products = cursor.fetchall()

        # 3. Add Inventory Records
        sql_inventory = "INSERT INTO Inventory_Record (Product_ID, Warehouse_ID, Qty_On_Hand) VALUES (%s, %s, %s)"
        
        for p in products:
            qty = random.randint(50, 200) 
            cursor.execute(sql_inventory, (p[0], warehouse_id, qty))

        print(f"✅ Success! Linked {len(products)} products to the Warehouse.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    seed_inventory_data()