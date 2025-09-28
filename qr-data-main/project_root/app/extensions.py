import sqlite3
from flask import g, current_app
import os

def get_db():
    if "db_conn" not in g:
        db_path = current_app.config["DATABASE_PATH"]
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        g.db_conn = conn
    return g.db_conn

def close_db(e=None):
    conn = g.pop("db_conn", None)
    if conn is not None:
        conn.close()

def init_db_teardown(app):
    app.teardown_appcontext(close_db)

def ensure_dirs(paths):
    for p in paths:
        os.makedirs(p, exist_ok=True)