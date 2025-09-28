from app import create_app
from app.extensions import DB_PATH, get_db
from app.models.users import find_user_by_username, verify_password

USERNAME = "admin"
PASSWORD = "admin123"

app = create_app()
with app.app_context():
    print(f"[DIAG] DB_PATH = {DB_PATH}")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, username, is_admin, length(password_hash) as len FROM users ORDER BY id")
    rows = cur.fetchall()
    print("[DIAG] users:")
    for r in rows:
        print(dict(r))
    conn.close()

    u = find_user_by_username(USERNAME)
    if not u:
        print(f"[DIAG] user '{USERNAME}' not found")
    else:
        ok = verify_password(u, PASSWORD)
        print(f"[DIAG] check_password({USERNAME}, {PASSWORD}) -> {ok}")