
import os
import mysql.connector
from mysql.connector import Error


def get_connection():
    """Create a connection to the Pharmacy Management System database."""
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", "3306")),
        user=os.environ.get("DB_USER", "pharmacy_app"),
        password=os.environ["DB_PASSWORD"],
        database=os.environ.get("DB_NAME", "pharmacy_db")
    )


if __name__ == "__main__":
    connection = None
    cursor = None

    try:
        connection = get_connection()

        if connection.is_connected():
            print("Connected to pharmacy_db successfully!")

            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")

            print("\nDatabase tables:")
            for row in cursor.fetchall():
                print("-", row[0])

    except (Error, KeyError, ValueError) as error:
        print("Database connection failed. Check your environment variables and MySQL configuration.")

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()
            print("\nDatabase connection closed.")
