import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def get_user_by_phone(phone):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name, state FROM farmers WHERE phone = %s", (phone,))
    user = cur.fetchone()

    cur.close()
    conn.close()

    return user


def create_user(phone):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO farmers (phone, state) VALUES (%s, %s)",
        (phone, "awaiting_name")
    )

    conn.commit()
    cur.close()
    conn.close()

def update_user_name(phone, name):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute(
        "UPDATE farmers SET name = %s, state = NULL WHERE phone = %s",
        (name, phone)
    )
    
    conn.commit()
    cur.close()
    conn.close()