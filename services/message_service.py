import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def save_message(phone, role, content):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO messages (phone, role, content) VALUES (%s, %s, %s)",
        (phone, role, content)
    )

    conn.commit()
    cur.close()
    conn.close()


def get_recent_messages(phone, limit=6):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT role, content FROM messages
        WHERE phone = %s
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (phone, limit)
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    # reverse to correct order
    rows.reverse()

    return [{"role": r[0], "content": r[1]} for r in rows]