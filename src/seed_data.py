import mysql.connector

def seed_basic_data():
    try:
        # 1. Connect to your database
        conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="Kushagra", # <--- UPDATE THIS
            database="smart_retail_db"
        )
        cursor = conn.cursor()
        print("🌱 Connection successful! Starting to add data...")

        # 2. Add a Supplier (Every product needs a supplier first)
        sql_supplier = "INSERT INTO Supplier (Name, Location, Type) VALUES (%s, %s, %s)"
        supplier_data = ("Fresh Mart Wholesale", "Mumbai", "Main Distributor")
        cursor.execute(sql_supplier, supplier_data)
        
        # Get the ID of the supplier we just added
        supplier_id = cursor.lastrowid

        # 3. Add some Products
        sql_product = "INSERT INTO Product (Name, Category, Cost_Price, Selling_Price, Supplier_ID) VALUES (%s, %s, %s, %s, %s)"
        products = [
            ("Basmati Rice", "Grains", 60.00, 85.00, supplier_id),
            ("Organic Milk", "Dairy", 40.00, 55.00, supplier_id),
            ("Dark Chocolate", "Snacks", 90.00, 150.00, supplier_id)
        ]
        
        cursor.executemany(sql_product, products)

        # 4. Save the changes
        conn.commit()
        print(f"✅ Success! Added 1 Supplier and {cursor.rowcount} Products.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    seed_basic_data()