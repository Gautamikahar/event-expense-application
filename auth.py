import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    try:
        conn = sqlite3.connect("event_splitter.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                       (username, hash_password(password)))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False  # Username already exists

def login_user(username, password):
    conn = sqlite3.connect("event_splitter.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=? AND password=?",
                   (username, hash_password(password)))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None
