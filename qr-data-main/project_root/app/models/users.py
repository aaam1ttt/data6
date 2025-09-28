from typing import Optional, List, Dict
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import get_db
from flask import current_app
import os
import datetime

def _column_exists(table: str, column: str) -> bool:
    db = get_db()
    rows = db.execute(f"PRAGMA table_info({table})").fetchall()
    for r in rows:
        if r["name"] == column:
            return True
    return False

def init_users_schema(app):
    with app.app_context():
        db = get_db()
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin INTEGER NOT NULL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        # добавим last_login если нет
        if not _column_exists("users", "last_login"):
            try:
                db.execute("ALTER TABLE users ADD COLUMN last_login DATETIME")
            except Exception:
                pass
        db.commit()

def ensure_admin_seed(app):
    with app.app_context():
        if count_admins() == 0:
            username = os.getenv("ADMIN_USERNAME", "admin")
            password = os.getenv("ADMIN_PASSWORD", "admin123")
            create_user(username, password, is_admin=True)

def count_admins() -> int:
    db = get_db()
    row = db.execute("SELECT COUNT(*) AS c FROM users WHERE is_admin = 1").fetchone()
    return int(row["c"]) if row else 0

def create_user(username: str, password: str, is_admin: bool=False) -> bool:
    db = get_db()
    try:
        db.execute(
            "INSERT INTO users (username, password_hash, is_admin, last_login) VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
            (username, generate_password_hash(password), 1 if is_admin else 0),
        )
        db.commit()
        return True
    except Exception:
        return False

def list_users() -> List[Dict]:
    db = get_db()
    rows = db.execute(
        "SELECT id, username, is_admin, created_at, last_login FROM users ORDER BY id"
    ).fetchall()
    return [dict(r) for r in rows]

def find_user_by_id(user_id: int) -> Optional[Dict]:
    db = get_db()
    row = db.execute(
        "SELECT id, username, password_hash, is_admin, last_login FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()
    return dict(row) if row else None

def find_user_by_username(username: str) -> Optional[Dict]:
    db = get_db()
    row = db.execute(
        "SELECT id, username, password_hash, is_admin, last_login FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    return dict(row) if row else None

def set_password(user_id: int, new_password: str) -> bool:
    db = get_db()
    try:
        db.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (generate_password_hash(new_password), user_id)
        )
        db.commit()
        return True
    except Exception:
        return False

def delete_user(user_id: int) -> bool:
    db = get_db()
    try:
        db.execute("DELETE FROM users WHERE id = ?", (user_id,))
        db.commit()
        return True
    except Exception:
        return False

def verify_password(stored_hash: str, password: str) -> bool:
    return check_password_hash(stored_hash, password)

def touch_last_login(user_id: int) -> None:
    db = get_db()
    db.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user_id,))
    db.commit()