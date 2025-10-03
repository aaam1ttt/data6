from app import create_app
from app.models.users import find_user_by_username, create_user, set_password, list_users, delete_user

USERNAME = "admin"
PASSWORD = "183729"

app = create_app()
with app.app_context():
    # Удаляем всех существующих пользователей
    users = list_users()
    for user in users:
        print(f"Удаляем: {user['username']} (ID: {user['id']})")
        delete_user(user['id'])
    
    # Создаём нового админа с нужными данными
    u = find_user_by_username(USERNAME)
    if u:
        ok = set_password(u["id"], PASSWORD)
        print("Пароль админа обновлён" if ok else "Не удалось обновить пароль")
    else:
        ok = create_user(USERNAME, PASSWORD, is_admin=True)
        print(f"Админ '{USERNAME}' создан с паролем '{PASSWORD}'" if ok else "Не удалось создать админа")
