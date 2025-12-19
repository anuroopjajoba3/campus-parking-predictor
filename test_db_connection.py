import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

try:
    # Connect to database
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    
    print("✅ Successfully connected to MySQL database!")
    
    # Test query
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM parking_lots")
    lots = cursor.fetchall()
    
    print(f"\n📊 Found {len(lots)} parking lots:")
    for lot in lots:
        print(f"  - {lot['name']}: {lot['capacity']} spaces")
    
    cursor.close()
    conn.close()
    
    print("\n✅ Database connection test successful!")
    
except mysql.connector.Error as err:
    print(f"❌ Error: {err}")
    print("\nTroubleshooting tips:")
    print("1. Check if MySQL is running: brew services list")
    print("2. Verify credentials in .env file")
    print("3. Check if database exists: mysql -u root -p -e 'SHOW DATABASES;'")
