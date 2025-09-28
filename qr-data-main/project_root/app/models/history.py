from typing import List, Dict, Optional
from ..extensions import get_db
import os
from datetime import datetime, timedelta

def init_history_schema(app):
    with app.app_context():
        db = get_db()
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action TEXT NOT NULL,         -- 'created' | 'scanned'
                code_type TEXT NOT NULL,      -- 'QR' | 'DM'
                form_type TEXT,               -- 'torg12' | 'message' | 'exploitation' | 'transport' | 'custom' | NULL
                content TEXT NOT NULL,        -- исходная строка (кодированная форма)
                image_path TEXT,              -- путь до PNG/загруженного
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
            """
        )
        db.commit()

def add_history(user_id: int, action: str, code_type: str, form_type: Optional[str],
                content: str, image_path: Optional[str]) -> None:
    db = get_db()
    db.execute(
        "INSERT INTO history (user_id, action, code_type, form_type, content, image_path) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, action, code_type, form_type, content, image_path)
    )
    db.commit()

    prune_history_by_user(user_id, keep=100)

def list_history_by_user(user_id: int, limit: int = 200) -> List[Dict]:
    db = get_db()
    rows = db.execute(
        "SELECT id, action, code_type, form_type, substr(content,1,240) AS content, image_path, created_at "
        "FROM history WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit)
    ).fetchall()
    return [dict(r) for r in rows]

def _delete_files(paths: List[Optional[str]]) -> None:
    for p in paths:
        if p and isinstance(p, str):
            try:
                if os.path.isfile(p):
                    os.remove(p)
            except Exception:
                pass

def delete_history_by_user(user_id: int) -> None:
    db = get_db()
    rows = db.execute("SELECT image_path FROM history WHERE user_id = ?", (user_id,)).fetchall()
    _delete_files([r["image_path"] for r in rows])
    db.execute("DELETE FROM history WHERE user_id = ?", (user_id,))
    db.commit()

def prune_history_by_user(user_id: int, keep: int = 100) -> None:
    """
    Оставляем только последние keep записей по user_id.
    """
    db = get_db()
    rows = db.execute(
        "SELECT id, image_path FROM history WHERE user_id = ? ORDER BY id DESC LIMIT -1 OFFSET ?",
        (user_id, keep)
    ).fetchall()
    if not rows:
        return
    _delete_files([r["image_path"] for r in rows])
    ids = [str(r["id"]) for r in rows]
    db.execute(f"DELETE FROM history WHERE id IN ({','.join(['?']*len(ids))})", ids)
    db.commit()

def delete_history_older_than_days(user_id: int, days: int) -> None:
    """
    Удаляет записи, старше N дней (для принудительной уборки).
    """
    db = get_db()
    rows = db.execute(
        "SELECT id, image_path FROM history WHERE user_id = ? AND created_at < datetime('now', ?)",
        (user_id, f"-{int(days)} days")
    ).fetchall()
    if not rows:
        return
    _delete_files([r["image_path"] for r in rows])
    ids = [str(r["id"]) for r in rows]
    db.execute(f"DELETE FROM history WHERE id IN ({','.join(['?']*len(ids))})", ids)
    db.commit()
