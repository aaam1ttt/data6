from app import create_app
from app.models.users import find_user_by_username, create_user, set_password

USERNAME = "admin"
PASSWORD = "admin123"

app = create_app()
with app.app_context():
    u = find_user_by_username(USERNAME)
    if u:
        ok = set_password(u["id"], PASSWORD)
        print("Пароль админа обновлён" if ok else "Не удалось обновить пароль")
    else:
        ok = create_user(USERNAME, PASSWORD, is_admin=True)
        print("Админ создан" if ok else "Не удалось создать админа")