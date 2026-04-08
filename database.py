import sqlite3
import hashlib
from datetime import datetime

DB_NAME = "users.db"

def connect_db():
    return sqlite3.connect(DB_NAME)

def create_table():
    conn = connect_db()
    cursor = conn.cursor()

    # Base users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT    NOT NULL UNIQUE,
            password    TEXT    NOT NULL
        )
    """)

    # Migration: add new columns safely
    existing_cols = [row[1] for row in cursor.execute("PRAGMA table_info(users)")]

    # ⚠ SQLite does NOT allow DEFAULT (datetime('now')) in ALTER TABLE
    # So we use NULL default and fill manually
    if "created_at" not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN created_at TEXT")
        cursor.execute("UPDATE users SET created_at = ? WHERE created_at IS NULL",
                       (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))

    if "last_login" not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN last_login TEXT")

    if "is_active" not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1")
        cursor.execute("UPDATE users SET is_active = 1 WHERE is_active IS NULL")

    # Usage tracking table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usage_logs (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT NOT NULL,
            module     TEXT NOT NULL,
            timestamp  TEXT NOT NULL,
            status     TEXT DEFAULT 'success'
        )
    """)

    # Activity feed table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_feed (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT NOT NULL,
            action     TEXT NOT NULL,
            detail     TEXT,
            timestamp  TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    if not username or not password:
        return False
    conn = connect_db()
    cursor = conn.cursor()
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO users (username, password, created_at, is_active) VALUES (?, ?, ?, 1)",
            (username, hash_password(password), now)
        )
        conn.commit()
        log_activity(username, "Registered", "New account created")
        return True
    except:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=? AND (is_active=1 OR is_active IS NULL)",
        (username, hash_password(password))
    )
    user = cursor.fetchone()
    if user:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("UPDATE users SET last_login=? WHERE username=?", (now, username))
        conn.commit()
        log_activity(username, "Login", "User logged in")
    conn.close()
    return user

def delete_user(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username=?", (username,))
    conn.commit()
    conn.close()

def get_all_users():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users ORDER BY id DESC")
    users = cursor.fetchall()
    conn.close()
    return [u[0] for u in users]

def get_all_users_details():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.username, u.created_at, u.last_login, u.is_active,
               COUNT(ul.id) AS total_uses
        FROM users u
        LEFT JOIN usage_logs ul ON u.username = ul.username
        GROUP BY u.username
        ORDER BY u.id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def toggle_user_active(username, is_active):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_active=? WHERE username=?",
                   (1 if is_active else 0, username))
    conn.commit()
    conn.close()

def change_user_password(username, new_password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password=? WHERE username=?",
                   (hash_password(new_password), username))
    conn.commit()
    conn.close()

def get_user_count():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_active_user_count():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_active=1 OR is_active IS NULL")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def log_usage(username, module, status="success"):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO usage_logs (username, module, timestamp, status) VALUES (?, ?, ?, ?)",
            (username, module, now, status)
        )
        conn.commit()
        conn.close()
    except:
        pass

def get_module_usage_counts():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT module, COUNT(*) FROM usage_logs GROUP BY module ORDER BY COUNT(*) DESC")
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}

def get_usage_by_day(days=30):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DATE(timestamp) as day, COUNT(*) as cnt
        FROM usage_logs
        WHERE timestamp >= datetime('now', ?)
        GROUP BY day ORDER BY day ASC
    """, (f"-{days} days",))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_usage_by_user(limit=10):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT username, COUNT(*) as cnt
        FROM usage_logs GROUP BY username ORDER BY cnt DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_total_usage():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM usage_logs")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_today_usage():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM usage_logs WHERE DATE(timestamp) = DATE('now')")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_recent_usage(limit=20):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT username, module, timestamp, status
        FROM usage_logs ORDER BY timestamp DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def log_activity(username, action, detail=""):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO activity_feed (username, action, detail, timestamp) VALUES (?, ?, ?, ?)",
            (username, action, detail, now)
        )
        conn.commit()
        conn.close()
    except:
        pass

def get_recent_activity(limit=15):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT username, action, detail, timestamp
            FROM activity_feed ORDER BY timestamp DESC LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    except:
        return []