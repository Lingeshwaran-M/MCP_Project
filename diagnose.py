
import os
import mysql.connector
from mysql.connector import pooling
import time

# Use the same env vars
DB_HOST = os.getenv("DB_HOST", "Host_name")
DB_PORT = int(os.getenv("DB_PORT", "3300"))
DB_USER = os.getenv("DB_USER", "Useer_name")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "Your_database_name")

print(f"Connecting to {DB_HOST}:{DB_PORT} user={DB_USER} db={DB_NAME}")

def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def test_direct_connection():
    print("\n--- Testing Direct Connection ---")
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT @@hostname, @@port;")
        print(f"Connected to: {cur.fetchone()}")
        
        cur.execute("SELECT id, name FROM student ORDER BY id")
        rows = cur.fetchall()
        print(f"Total rows found: {len(rows)}")
        for r in rows:
            print(f"  {r}")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

def test_pool_behavior():
    print("\n--- Testing Pool Behavior (Simulating Stale Reads) ---")
    # Create a pool similar to app
    pool = pooling.MySQLConnectionPool(
        pool_name="test_pool",
        pool_size=2,
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    
    # Connection 1: Read
    conn1 = pool.get_connection()
    cur1 = conn1.cursor()
    cur1.execute("SELECT count(*) FROM student")
    c1 = cur1.fetchone()[0]
    print(f"Conn1 (Trace 1): Count = {c1}")
    
    # Connection 2: Insert a temp record
    print("Conn2: Inserting temp record...")
    conn2 = pool.get_connection()
    cur2 = conn2.cursor()
    cur2.execute("INSERT INTO student (name, email, phone_number) VALUES ('Temp', 'temp@test.com', '000')")
    temp_id = cur2.lastrowid
    conn2.commit()
    conn2.close()
    print(f"Conn2: Inserted ID {temp_id}")

    # Connection 1: Read again (Without commit/rollback/close)
    try:
        cur1.execute("SELECT count(*) FROM student")
        c2 = cur1.fetchone()[0]
        print(f"Conn1 (Trace 2 - Reusing same conn object): Count = {c2}")
        if c2 == c1:
            print("  -> STALE READ DETECTED! (Conn1 didn't see the update)")
        else:
            print("  -> Read updated successfully.")
    except Exception as e:
        print(e)
    
    # Clean up
    conn3 = pool.get_connection()
    cur3 = conn3.cursor()
    cur3.execute("DELETE FROM student WHERE id = %s", (temp_id,))
    conn3.commit()
    conn3.close()
    print("Cleaned up temp record.")
    
    # Close Conn1 finally
    conn1.close()

if __name__ == "__main__":
    if not DB_PASSWORD:
        print("DB_PASSWORD not set")
    else:
        test_direct_connection()
        test_pool_behavior()
