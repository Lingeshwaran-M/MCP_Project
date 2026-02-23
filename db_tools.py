import os
import mysql.connector
from mysql.connector import pooling


DB_HOST = os.getenv("DB_HOST", "Host_Name")
DB_PORT = int(os.getenv("DB_PORT", "3300"))
DB_USER = os.getenv("DB_USER", "mcp_user")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "simple_db")

if not DB_PASSWORD:
    raise RuntimeError("DB_PASSWORD environment variable not set.")


pool = pooling.MySQLConnectionPool(
    pool_name="student_pool",
    pool_size=5,
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
)

def get_conn():
    return pool.get_connection()


def read_records():
    with get_conn() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(
                "SELECT id, name, email, phone_number FROM student ORDER BY id"
            )
            return cur.fetchall()



def create_student(name, email, phone_number):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO student (name, email, phone_number) VALUES (%s, %s, %s)",
                (name, email, phone_number),
            )
            conn.commit()
            return cur.lastrowid



def update_student(student_id, name=None, email=None, phone_number=None):
    fields = []
    values = []

    if name is not None:
        fields.append("name = %s")
        values.append(name)

    if email is not None:
        fields.append("email = %s")
        values.append(email)

    if phone_number is not None:
        fields.append("phone_number = %s")
        values.append(phone_number)

    if not fields:
        return 0

    values.append(student_id)

    query = f"UPDATE student SET {', '.join(fields)} WHERE id = %s"

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query, tuple(values))
            conn.commit()
            return cur.rowcount



def delete_student(student_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM student WHERE id = %s", (student_id,))
            conn.commit()
            return cur.rowcount