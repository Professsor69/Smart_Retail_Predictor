"""
seed_data.py
------------
Populates the smart_retail database with realistic demo data
so the app is usable immediately after running smart_retail_setup.sql.

Run once:
    python seed_data.py

Safe to re-run — it checks for existing records before inserting.
"""

import random
from datetime import datetime, timedelta
from db_connection import get_db_connection, get_cursor


# ── Helpers ───────────────────────────────────────────────────────────────────

def _table_is_empty(cursor, table: str) -> bool:
    cursor.execute(f"SELECT COUNT(*) AS n FROM {table}")
    return cursor.fetchone()["n"] == 0


# ── Seed functions ────────────────────────────────────────────────────────────

def seed_warehouses(cursor) -> list[int]:
    """Insert warehouses if not already present. Returns list of Warehouse_IDs."""
    if not _table_is_empty(cursor, "Warehouse"):
        cursor.execute("SELECT Warehouse_ID FROM Warehouse")
        ids = [r["Warehouse_ID"] for r in cursor.fetchall()]
        print(f"   Warehouses already exist ({len(ids)} rows). Skipping.")
        return ids

    warehouses = [
        ("Central Hub - Mumbai", 10000),
        ("North Hub - Delhi",     5000),
        ("South Hub - Chennai",   3000),
    ]
    cursor.executemany(
        "INSERT INTO Warehouse (Location, Capacity) VALUES (%s, %s)",
        warehouses,
    )
    cursor.execute("SELECT Warehouse_ID FROM Warehouse")
    ids = [r["Warehouse_ID"] for r in cursor.fetchall()]
    print(f"   ✅ Inserted {len(ids)} warehouses.")
    return ids


def seed_suppliers(cursor) -> list[int]:
    """Insert suppliers. Returns list of Supplier_IDs."""
    if not _table_is_empty(cursor, "Supplier"):
        cursor.execute("SELECT Supplier_ID FROM Supplier")
        ids = [r["Supplier_ID"] for r in cursor.fetchall()]
        print(f"   Suppliers already exist ({len(ids)} rows). Skipping.")
        return ids

    suppliers = [
        ("TechSource India",   "Ravi Sharma",   "+91-9810000001", "ravi@techsource.in",     "India"),
        ("Global Electronics", "Sarah Johnson", "+1-2025550100",  "sarah@globalelec.com",    "USA"),
        ("EuroGoods GmbH",     "Klaus Müller",  "+49-30-123456",  "klaus@eurogoods.de",      "Germany"),
        ("AsiaTrade Co.",      "Li Wei",        "+86-10-555123",  "liwei@asiatrade.cn",      "China"),
    ]
    cursor.executemany(
        "INSERT INTO Supplier (Supplier_Name, Contact_Name, Phone, Email, Country) VALUES (%s,%s,%s,%s,%s)",
        suppliers,
    )
    cursor.execute("SELECT Supplier_ID FROM Supplier")
    ids = [r["Supplier_ID"] for r in cursor.fetchall()]
    print(f"   ✅ Inserted {len(ids)} suppliers.")
    return ids


def seed_products(cursor, supplier_ids: list[int]) -> list[dict]:
    """Insert products. Returns list of {Product_ID, Product_Name} dicts."""
    if not _table_is_empty(cursor, "Product"):
        cursor.execute("SELECT Product_ID, Product_Name FROM Product")
        rows = cursor.fetchall()
        print(f"   Products already exist ({len(rows)} rows). Skipping.")
        return rows

    s = supplier_ids   # shorthand
    products = [
        ("Wireless Mouse",       "Electronics",  12.00,  25.99, s[0]),
        ("Mechanical Keyboard",  "Electronics",  45.00,  89.50, s[0]),
        ("Gaming Monitor",       "Electronics", 180.00, 299.99, s[1]),
        ("USB-C Hub",            "Electronics",  18.00,  39.99, s[1]),
        ("Laptop Stand",         "Accessories",  10.00,  24.99, s[2]),
        ("Cable Organizer",      "Accessories",   2.00,   9.99, s[2]),
        ("Noise-Cancel Headset", "Electronics",  60.00, 129.00, s[3]),
        ("Smart Webcam 4K",      "Electronics",  55.00, 110.00, s[3]),
        ("Ergonomic Chair",      "Furniture",   150.00, 299.00, s[1]),
        ("LED Desk Lamp",        "Accessories",   8.00,  22.99, s[2]),
    ]
    cursor.executemany(
        "INSERT INTO Product (Product_Name, Category, Cost_Price, Selling_Price, Supplier_ID) "
        "VALUES (%s,%s,%s,%s,%s)",
        products,
    )
    cursor.execute("SELECT Product_ID, Product_Name FROM Product")
    rows = cursor.fetchall()
    print(f"   ✅ Inserted {len(rows)} products.")
    return rows


def seed_inventory(cursor, product_rows: list[dict], warehouse_ids: list[int]):
    """Link every product to every warehouse with a random stock level."""
    if not _table_is_empty(cursor, "Inventory_Record"):
        print("   Inventory already exists. Skipping.")
        return

    rows = []
    for p in product_rows:
        for wid in warehouse_ids:
            qty = random.randint(30, 300)
            rows.append((p["Product_ID"], wid, qty))

    cursor.executemany(
        "INSERT INTO Inventory_Record (Product_ID, Warehouse_ID, Qty_On_Hand) VALUES (%s,%s,%s)",
        rows,
    )
    print(f"   ✅ Inserted {len(rows)} inventory records.")


def seed_promotions(cursor) -> list[int]:
    """Insert promotional campaigns."""
    if not _table_is_empty(cursor, "Promotion"):
        cursor.execute("SELECT Campaign_ID FROM Promotion")
        ids = [r["Campaign_ID"] for r in cursor.fetchall()]
        print(f"   Promotions already exist. Skipping.")
        return ids

    promos = [
        ("New Year Sale",       10.00, "2026-01-01", "2026-01-07"),
        ("Republic Day",        15.00, "2026-01-26", "2026-01-28"),
        ("Holi Flash Sale",      8.00, "2026-03-14", "2026-03-15"),
        ("Summer Clearance",    20.00, "2026-05-01", "2026-05-31"),
    ]
    cursor.executemany(
        "INSERT INTO Promotion (Campaign_Name, Discount_Pct, Start_Date, End_Date) VALUES (%s,%s,%s,%s)",
        promos,
    )
    cursor.execute("SELECT Campaign_ID FROM Promotion")
    ids = [r["Campaign_ID"] for r in cursor.fetchall()]
    print(f"   ✅ Inserted {len(ids)} promotions.")
    return ids


def seed_customers(cursor) -> list[dict]:
    """Insert demo customer accounts. Returns list of {id, Name} dicts."""
    demo_accounts = [
        ("Kush",      "Kushagra",   "kush@demo.com"),
        ("Admin",     "admin123",   "admin@demo.com"),
        ("DemoUser",  "demo1234",   "demo@demo.com"),
    ]
    inserted = []
    for name, pwd, email in demo_accounts:
        cursor.execute("SELECT id, Name FROM Customer WHERE Name = %s", (name,))
        row = cursor.fetchone()
        if row:
            inserted.append(row)
        else:
            cursor.execute(
                "INSERT INTO Customer (Name, Contact_Info, Email) VALUES (%s,%s,%s)",
                (name, pwd, email),
            )
            inserted.append({"id": cursor.lastrowid, "Name": name})
    print(f"   ✅ Ensured {len(inserted)} demo customer accounts.")
    return inserted


def seed_sales_data(cursor, customers: list[dict]):
    """
    Generate 60 days of realistic daily sales for each demo customer.
    Each customer gets a different product mix and volume pattern.
    Skips if that customer already has sales data.
    """
    product_profiles = [
        # (name,                  category,      base_qty,  price,   discount, region)
        ("Wireless Mouse",        "Electronics",  20, 3,   25.99,  0.0,    "North"),
        ("Mechanical Keyboard",   "Electronics",   7, 3,   89.50,  5.0,    "West"),
        ("Gaming Monitor",        "Electronics",   2, 2,  299.99, 15.0,    "South"),
        ("USB-C Hub",             "Electronics",  15, 5,   39.99,  0.0,    "East"),
        ("Laptop Stand",          "Accessories",  10, 4,   24.99,  0.0,    "North"),
        ("Noise-Cancel Headset",  "Electronics",   5, 3,  129.00, 10.0,    "West"),
        ("LED Desk Lamp",         "Accessories",  12, 5,   22.99,  0.0,    "South"),
    ]

    start_date = datetime(2026, 1, 1)

    for customer in customers:
        user_id = customer["id"]
        cursor.execute("SELECT COUNT(*) AS n FROM Sales_Data WHERE user_id = %s", (user_id,))
        if cursor.fetchone()["n"] > 0:
            print(f"   Sales for '{customer['Name']}' already exist. Skipping.")
            continue

        batch_id = f"SEED_{customer['Name'].upper()}_001"
        rows = []

        for day_offset in range(60):
            current_date = (start_date + timedelta(days=day_offset)).strftime("%Y-%m-%d")
            order_base   = day_offset * 10

            for i, (pname, cat, base, variance, price, disc, region) in enumerate(product_profiles):
                # Add seasonality: weekends sell more
                weekday = (start_date + timedelta(days=day_offset)).weekday()
                weekend_boost = 1.5 if weekday >= 5 else 1.0

                qty = max(0, int((base + random.randint(-variance, variance)) * weekend_boost))
                rows.append((
                    user_id,
                    f"ORD-{order_base + i:04d}",
                    pname, cat, qty, price, disc, region,
                    current_date, batch_id,
                ))

        cursor.executemany(
            """INSERT INTO Sales_Data
               (user_id, order_id, product_name, category,
                quantity_sold, unit_price, discount, region,
                sale_date, upload_batch)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            rows,
        )
        print(f"   ✅ Inserted {len(rows)} sales rows for '{customer['Name']}'.")


# ── Entry point ───────────────────────────────────────────────────────────────

def run_all():
    print("\n🌱 Smart Retail Predictor — Database Seeder")
    print("=" * 48)

    conn   = get_db_connection()
    conn.autocommit = False
    cursor = get_cursor(conn)

    try:
        print("\n[1/6] Seeding warehouses...")
        warehouse_ids = seed_warehouses(cursor)

        print("\n[2/6] Seeding suppliers...")
        supplier_ids = seed_suppliers(cursor)

        print("\n[3/6] Seeding products...")
        product_rows = seed_products(cursor, supplier_ids)

        print("\n[4/6] Seeding inventory...")
        seed_inventory(cursor, product_rows, warehouse_ids)

        print("\n[5/6] Seeding promotions...")
        seed_promotions(cursor)

        print("\n[6/6] Seeding customers + 60-day sales data...")
        customers = seed_customers(cursor)
        seed_sales_data(cursor, customers)

        conn.commit()
        print("\n" + "=" * 48)
        print("✅ All seed data committed successfully!")
        print("\nDemo accounts:")
        print("   Username: Kush      | Password: Kushagra")
        print("   Username: Admin     | Password: admin123")
        print("   Username: DemoUser  | Password: demo1234")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Seeding failed — rolled back. Error: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    run_all()