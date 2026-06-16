import sqlite3
from pathlib import Path

DATABASE_PATH = Path("local_request_manager.db")


def get_connection():
    return sqlite3.connect(DATABASE_PATH)


def init_database():
    connection = get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                customer_phone TEXT NOT NULL,
                customer_email TEXT,
                message TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'new',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()
    finally:
        connection.close()


def save_request(
    customer_name: str,
    customer_phone: str,
    customer_email: str,
    message: str,
):
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO requests (
                customer_name,
                customer_phone,
                customer_email,
                message
            ) VALUES (?, ?, ?, ?)
            """,
            (
                customer_name,
                customer_phone,
                customer_email,
                message,
            ),
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()