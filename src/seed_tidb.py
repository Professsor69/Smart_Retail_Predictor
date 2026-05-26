"""
seed_tidb.py
------------
Seeds ALL empty tables in the TiDB smart_retail_db with realistic demo data.
Matches the exact live schema found via DESCRIBE queries.

Run from the src/ directory:
    python seed_tidb.py
"""

import sys
import random
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8')

from db_connection import get_db_connection, get_cursor


# ── Helpers ───────────────────────────────────────────────────────────────────

def table_count(cursor, table: str) -> int:
    cursor.execute(f"SELECT COUNT(*) AS n FROM {table}")
    return cursor.fetchone()["n"]


# ── 1. Suppliers ──────────────────────────────────────────────────────────────
# Schema: Supplier_ID | Name | Location | Type

def seed_suppliers(cursor) -> list[int]:
    if table_count(cursor, "Supplier") > 0:
        cursor.execute("SELECT Supplier_ID FROM Supplier")
        ids = [r["Supplier_ID"] for r in cursor.fetchall()]
        print(f"   Suppliers already exist ({len(ids)} rows). Skipping.")
        return ids

    suppliers = [
        ("TechSource India",   "Mumbai, India",   "Electronics"),
        ("Global Electronics", "New York, USA",   "Electronics"),
        ("EuroGoods GmbH",     "Berlin, Germany", "Accessories"),
        ("AsiaTrade Co.",      "Shenzhen, China", "Mixed"),
    ]
    cursor.executemany(
        "INSERT INTO Supplier (Name, Location, Type) VALUES (%s, %s, %s)",
        suppliers,
    )
    cursor.execute("SELECT Supplier_ID FROM Supplier")
    ids = [r["Supplier_ID"] for r in cursor.fetchall()]
    print(f"   Inserted {len(ids)} suppliers.")
    return ids


# ── 2. Products ───────────────────────────────────────────────────────────────
# Schema: Product_ID | Name | Category | Cost_Price | Selling_Price | Supplier_ID

def seed_products(cursor, supplier_ids: list[int]) -> list[dict]:
    if table_count(cursor, "Product") > 0:
        cursor.execute("SELECT Product_ID, Name FROM Product")
        rows = cursor.fetchall()
        print(f"   Products already exist ({len(product_rows)} rows). Skipping.")
        # Fix any NULLs in Selling_Price from old schema
        cursor.execute("""
            UPDATE Product SET Selling_Price = CASE Name
                WHEN 'Wireless Mouse'       THEN 25.99
                WHEN 'Mechanical Keyboard'  THEN 89.50
                WHEN 'Gaming Monitor'       THEN 299.99
                WHEN 'USB-C Hub'            THEN 39.99
                WHEN 'Laptop Stand'         THEN 24.99
                WHEN 'Cable Organizer'      THEN 9.99
                WHEN 'Noise-Cancel Headset' THEN 129.00
                WHEN 'Smart Webcam 4K'      THEN 110.00
                WHEN 'Ergonomic Chair'      THEN 299.00
                WHEN 'LED Desk Lamp'        THEN 22.99
                ELSE 29.99
            END
            WHERE Selling_Price IS NULL
        """)
        print(f"   Fixed NULL prices on existing products.")
        return rows

    s = supplier_ids
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
        "INSERT INTO Product (Name, Category, Cost_Price, Selling_Price, Supplier_ID) "
        "VALUES (%s, %s, %s, %s, %s)",
        products,
    )
    cursor.execute("SELECT Product_ID, Name FROM Product")
    rows = cursor.fetchall()
    print(f"   Inserted {len(rows)} products.")
    return rows


# ── 3. Warehouses ─────────────────────────────────────────────────────────────
# Schema: Warehouse_ID | Location | Capacity

def seed_warehouses(cursor) -> list[int]:
    if table_count(cursor, "Warehouse") > 0:
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
    print(f"   Inserted {len(ids)} warehouses.")
    return ids


# ── 4. Inventory Records ──────────────────────────────────────────────────────
# Schema: Inventory_ID | Product_ID | Warehouse_ID | Qty_On_Hand

def seed_inventory(cursor, product_rows: list[dict], warehouse_ids: list[int]):
    if table_count(cursor, "Inventory_Record") > 0:
        print("   Inventory already exists. Skipping.")
        return

    rows = []
    for p in product_rows:
        for wid in warehouse_ids:
            qty = random.randint(30, 300)
            rows.append((p["Product_ID"], wid, qty))

    cursor.executemany(
        "INSERT INTO Inventory_Record (Product_ID, Warehouse_ID, Qty_On_Hand) VALUES (%s, %s, %s)",
        rows,
    )
    print(f"   Inserted {len(rows)} inventory records.")


# ── 5. Promotions ─────────────────────────────────────────────────────────────
# Schema: Promo_ID | Product_ID | Discount_Percent | Offer_Details | Validity

def seed_promotions(cursor, product_rows: list[dict]):
    if table_count(cursor, "Promotion") > 0:
        print("   Promotions already exist. Skipping.")
        return

    promos = []
    promo_templates = [
        (10.00, "New Year Flash Sale - 10% off",       "2026-01-07"),
        (15.00, "Republic Day Special - 15% off",      "2026-01-28"),
        (8.00,  "Holi Weekend Deal - 8% off",          "2026-03-15"),
        (20.00, "Summer Clearance - 20% off",          "2026-05-31"),
        (12.00, "Weekend Bonanza - 12% off",           "2026-04-30"),
    ]

    for i, p in enumerate(product_rows):
        disc, details, validity = promo_templates[i % len(promo_templates)]
        promos.append((p["Product_ID"], disc, details, validity))

    cursor.executemany(
        "INSERT INTO Promotion (Product_ID, Discount_Percent, Offer_Details, Validity) "
        "VALUES (%s, %s, %s, %s)",
        promos,
    )
    print(f"   Inserted {len(promos)} promotions.")


# ── 6. Sales + Sales_Items ────────────────────────────────────────────────────
# Sales schema: Transaction_ID | id (customer) | Date | Total_Amount | Total_Quantity
# Sales_Items schema: Transaction_ID | Product_ID | Quantity | Subtotal

def seed_sales(cursor, product_rows: list[dict]):
    if table_count(cursor, "Sales") > 0:
        print("   Sales already exist. Skipping.")
        return

    # Get customer IDs
    cursor.execute("SELECT id FROM Customer")
    customer_ids = [r["id"] for r in cursor.fetchall()]
    if not customer_ids:
        print("   No customers found — skipping Sales seeding.")
        return

    start_date = datetime(2026, 1, 1)
    transactions = []
    items = []
    tx_id = 1

    for day_offset in range(90):  # 90 days of transactions
        current_dt = start_date + timedelta(days=day_offset)
        # 2-5 transactions per day
        n_txns = random.randint(2, 5)
        for _ in range(n_txns):
            customer_id = random.choice(customer_ids)
            # Each transaction has 1-3 items
            n_items = random.randint(1, 3)
            sampled_products = random.sample(product_rows, min(n_items, len(product_rows)))

            total_amount = 0
            total_qty = 0
            tx_items = []

            for prod in sampled_products:
                qty = random.randint(1, 5)
                price = float(prod["Selling_Price"]) if prod.get("Selling_Price") is not None else 29.99
                subtotal = round(qty * price, 2)
                total_amount += subtotal
                total_qty += qty
                tx_items.append((tx_id, prod["Product_ID"], qty, subtotal))

            transactions.append((tx_id, customer_id, current_dt.strftime("%Y-%m-%d %H:%M:%S"),
                                  round(total_amount, 2), total_qty))
            items.extend(tx_items)
            tx_id += 1

    # Need Selling_Price in product_rows — fetch it
    cursor.executemany(
        "INSERT INTO Sales (Transaction_ID, id, Date, Total_Amount, Total_Quantity) "
        "VALUES (%s, %s, %s, %s, %s)",
        transactions,
    )
    cursor.executemany(
        "INSERT INTO Sales_Items (Transaction_ID, Product_ID, Quantity, Subtotal) "
        "VALUES (%s, %s, %s, %s)",
        items,
    )
    print(f"   Inserted {len(transactions)} sales transactions and {len(items)} line items.")


# ── 7. External Factors ───────────────────────────────────────────────────────
# Schema: Factor_ID | Type_Weather_Event | Date | Impact_Level

def seed_external_factors(cursor):
    if table_count(cursor, "external_factor") > 0:
        print("   External factors already exist. Skipping.")
        return

    factors = [
        ("Heatwave",          "2026-01-15", "High"),
        ("Monsoon Rain",      "2026-02-10", "Medium"),
        ("Festival Season",   "2026-03-05", "Critical"),
        ("Stock Market Drop", "2026-03-20", "High"),
        ("Cold Front",        "2026-04-01", "Low"),
        ("Public Holiday",    "2026-01-26", "High"),
        ("Tech Expo Event",   "2026-02-20", "Medium"),
        ("Cyclone Warning",   "2026-04-15", "Critical"),
    ]
    cursor.executemany(
        "INSERT INTO external_factor (Type_Weather_Event, Date, Impact_Level) "
        "VALUES (%s, %s, %s)",
        factors,
    )
    print(f"   Inserted {len(factors)} external factors.")


# ── 8. Prediction Models ──────────────────────────────────────────────────────
# Schema: Model_ID | Product_ID | Factor_ID | Forecast_Value | Confidence_Score
#         | Seasonality_Index | Forecast_Date

def seed_prediction_models(cursor, product_rows: list[dict]):
    if table_count(cursor, "prediction_model") > 0:
        print("   Prediction models already exist. Skipping.")
        return

    # Get factor IDs
    cursor.execute("SELECT Factor_ID FROM external_factor")
    factor_ids = [r["Factor_ID"] for r in cursor.fetchall()]
    if not factor_ids:
        print("   No external factors — skipping prediction models.")
        return

    models = []
    base_date = datetime(2026, 5, 1)

    for i, prod in enumerate(product_rows):
        for day in range(30):  # 30-day forecast per product
            forecast_date = (base_date + timedelta(days=day)).strftime("%Y-%m-%d")
            factor_id = random.choice(factor_ids)
            # Seasonal wave
            import math
            seasonality = round(1.0 + 0.3 * math.sin(2 * math.pi * day / 7), 2)
            base_demand = random.randint(10, 80)
            forecast_val = int(base_demand * seasonality)
            confidence = round(random.uniform(0.72, 0.97), 4)

            models.append((prod["Product_ID"], factor_id, forecast_val,
                           confidence, seasonality, forecast_date))

    cursor.executemany(
        "INSERT INTO prediction_model "
        "(Product_ID, Factor_ID, Forecast_Value, Confidence_Score, Seasonality_Index, Forecast_Date) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        models,
    )
    print(f"   Inserted {len(models)} prediction model records.")


# ── 9. Audit Log ─────────────────────────────────────────────────────────────
# Schema: log_id | action_type | table_affected | user_id | details | action_timestamp

def seed_audit_log(cursor):
    if table_count(cursor, "audit_log") > 0:
        print("   Audit log already has entries. Skipping.")
        return

    cursor.execute("SELECT id FROM Customer")
    customer_ids = [r["id"] for r in cursor.fetchall()]
    if not customer_ids:
        return

    actions = [
        ("INSERT", "Sales_Data",     "Bulk upload: 60 rows via CSV"),
        ("INSERT", "Product",        "New product added via dashboard"),
        ("UPDATE", "Inventory_Record","Stock level adjusted after delivery"),
        ("INSERT", "Sales_Data",     "Bulk upload: 30 rows via Excel"),
        ("DELETE", "Promotion",      "Expired campaign removed"),
        ("INSERT", "Customer",       "New user registered"),
        ("INSERT", "Sales",          "Manual transaction entry"),
        ("UPDATE", "Product",        "Selling price updated"),
    ]

    logs = []
    base_dt = datetime(2026, 1, 1, 9, 0, 0)
    for i, (action, table, detail) in enumerate(actions):
        uid = random.choice(customer_ids)
        ts = (base_dt + timedelta(hours=i * 6 + random.randint(0, 3))).strftime("%Y-%m-%d %H:%M:%S")
        logs.append((action, table, uid, detail, ts))

    cursor.executemany(
        "INSERT INTO audit_log (action_type, table_affected, user_id, details, action_timestamp) "
        "VALUES (%s, %s, %s, %s, %s)",
        logs,
    )
    print(f"   Inserted {len(logs)} audit log entries.")


# ── 10. Sales_Data (main ML feed) ────────────────────────────────────────────

def seed_sales_data(cursor):
    if table_count(cursor, "Sales_Data") > 0:
        print(f"   Sales_Data already has {table_count(cursor, 'Sales_Data')} rows. Skipping.")
        return

    cursor.execute("SELECT id, Name FROM Customer")
    customers = cursor.fetchall()
    if not customers:
        print("   No customers — skipping Sales_Data.")
        return

    product_profiles = [
        ("Wireless Mouse",       "Electronics",  20, 3,  25.99, 0.0,  "North"),
        ("Mechanical Keyboard",  "Electronics",   7, 3,  89.50, 5.0,  "West"),
        ("Gaming Monitor",       "Electronics",   2, 2, 299.99, 15.0, "South"),
        ("USB-C Hub",            "Electronics",  15, 5,  39.99, 0.0,  "East"),
        ("Laptop Stand",         "Accessories",  10, 4,  24.99, 0.0,  "North"),
        ("Noise-Cancel Headset", "Electronics",   5, 3, 129.00, 10.0, "West"),
        ("LED Desk Lamp",        "Accessories",  12, 5,  22.99, 0.0,  "South"),
    ]

    start_date = datetime(2026, 1, 1)
    for customer in customers:
        uid = customer["id"]
        # Check if this customer already has rows
        cursor.execute("SELECT COUNT(*) AS n FROM Sales_Data WHERE user_id = %s", (uid,))
        if cursor.fetchone()["n"] > 0:
            print(f"   Sales_Data for '{customer['Name']}' already exists. Skipping.")
            continue

        batch_id = f"SEED_{customer['Name'].upper()}_001"
        rows = []

        for day_offset in range(90):
            current_date = (start_date + timedelta(days=day_offset)).strftime("%Y-%m-%d")
            order_base = day_offset * 10
            weekday = (start_date + timedelta(days=day_offset)).weekday()
            weekend_boost = 1.5 if weekday >= 5 else 1.0

            for i, (pname, cat, base, variance, price, disc, region) in enumerate(product_profiles):
                qty = max(1, int((base + random.randint(-variance, variance)) * weekend_boost))
                rows.append((
                    uid,
                    f"ORD-{order_base + i:04d}",
                    pname, cat, qty, price, disc, region,
                    current_date, batch_id,
                ))

        cursor.executemany(
            """INSERT INTO Sales_Data
               (user_id, order_id, product_name, category,
                quantity_sold, unit_price, discount, region,
                sale_date, upload_batch)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            rows,
        )
        print(f"   Inserted {len(rows)} Sales_Data rows for '{customer['Name']}'.")


# ── Entry Point ───────────────────────────────────────────────────────────────

def run_all():
    print("\nSmart Retail Predictor - TiDB Seeder")
    print("=" * 48)

    conn = get_db_connection()
    conn.autocommit = False
    cursor = get_cursor(conn)

    try:
        print("\n[1/9] Seeding suppliers...")
        supplier_ids = seed_suppliers(cursor)

        print("\n[2/9] Seeding products...")
        # Re-fetch with Selling_Price for Sales seeding
        if table_count(cursor, "Product") > 0:
            cursor.execute("SELECT Product_ID, Name, Selling_Price FROM Product")
            product_rows = cursor.fetchall()
        else:
            product_rows = []
        # Run seeder
        if not product_rows:
            product_rows = seed_products(cursor, supplier_ids)
            # Re-fetch with Selling_Price
            cursor.execute("SELECT Product_ID, Name, Selling_Price FROM Product")
            product_rows = cursor.fetchall()
        else:
            print(f"   Products already exist ({len(product_rows)} rows). Skipping.")

        print("\n[3/9] Seeding warehouses...")
        warehouse_ids = seed_warehouses(cursor)

        print("\n[4/9] Seeding inventory...")
        seed_inventory(cursor, product_rows, warehouse_ids)

        print("\n[5/9] Seeding promotions...")
        seed_promotions(cursor, product_rows)

        print("\n[6/9] Seeding sales transactions + line items...")
        seed_sales(cursor, product_rows)

        print("\n[7/9] Seeding external factors...")
        seed_external_factors(cursor)

        print("\n[8/9] Seeding prediction models...")
        seed_prediction_models(cursor, product_rows)

        print("\n[9/9] Seeding audit log...")
        seed_audit_log(cursor)

        # Sales_Data (ML feed — uses existing customers)
        print("\n[+] Seeding Sales_Data (ML training data)...")
        seed_sales_data(cursor)

        conn.commit()
        print("\n" + "=" * 48)
        print("All seed data committed successfully!")

    except Exception as e:
        conn.rollback()
        print(f"\nSeeding FAILED - rolled back. Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    run_all()
