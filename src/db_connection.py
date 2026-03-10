import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",        # Using the IP is safer than 'localhost'
        user="root",
        password="Kushagra", # Use your actual password
        database="smart_retail",
        autocommit=True          # This is the "Auto-Save" button
    )