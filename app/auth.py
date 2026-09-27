import sqlite3
import hashlib
import os

DATABASE = "users.db"


def hash_password(password):
    salt = os.urandom(16)
    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        100000
    )
    return salt.hex() + ":" + hashed.hex()


def verify_password(password, stored_password):
    salt_hex, hash_hex = stored_password.split(":")
    salt = bytes.fromhex(salt_hex)

    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        100000
    )

    return hashed.hex() == hash_hex


def create_table():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            category TEXT NOT NULL,
            budget INTEGER NOT NULL,
            preference TEXT NOT NULL,
            recommendations TEXT NOT NULL
        )
    """)
def save_history(username, category, budget, preference, recommendations):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO history
        (username, category, budget, preference, recommendations)
        VALUES (?, ?, ?, ?, ?)
    """, (
        username,
        category,
        budget,
        preference,
        recommendations
    ))

    connection.commit()
    connection.close()


def register_user(username, password):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    hashed_password = hash_password(password)

    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_password)
        )

        connection.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        connection.close()


def login_user(username, password):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT password FROM users WHERE username = ?",
        (username,)
    )

    user = cursor.fetchone()
    connection.close()

    if user and verify_password(password, user[0]):
        return True

    return False


create_table()