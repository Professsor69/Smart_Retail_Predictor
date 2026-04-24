import sys
sys.path.insert(0, 'src')
from db_connection import get_db_connection, get_cursor

conn = get_db_connection()
c = get_cursor(conn)

# Check procedures
c.execute("SHOW PROCEDURE STATUS WHERE Db='smart_retail'")
procs = [r['Name'] for r in c.fetchall()]
print("PROCEDURES:", procs)

# Check functions
c.execute("SHOW FUNCTION STATUS WHERE Db='smart_retail'")
funcs = [r['Name'] for r in c.fetchall()]
print("FUNCTIONS:", funcs)

# Check Prediction_Model table
c.execute("SHOW TABLES LIKE 'prediction%'")
print("PREDICTION TABLES:", c.fetchall())

# Check Customer table
c.execute("DESCRIBE customer")
print("CUSTOMER SCHEMA:", [r['Field'] for r in c.fetchall()])

# Test the sales query
c.execute("SELECT * FROM sales_data LIMIT 2")
rows = c.fetchall()
print("SAMPLE SALES:", rows[:1])

conn.close()
