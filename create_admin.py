
from getpass import getpass
from werkzeug.security import generate_password_hash
from db import get_connection

username = input("Enter admin username: ").strip()
password = getpass("Enter admin password (minimum 12 characters): ")

if len(password) < 12:
    raise SystemExit("Password must be at least 12 characters.")

conn = get_connection()

try:
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO AdminUser (username, password_hash)
        VALUES (%s, %s)
        """,
        (username, generate_password_hash(password))
    )

    conn.commit()
    print("Admin account created successfully!")

except Exception as error:
    conn.rollback()
    print("Could not create admin account:", error)

finally:
    cursor.close()
    conn.close()
