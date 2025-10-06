#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
from werkzeug.security import generate_password_hash
import os

USERNAME = "admin"
PASSWORD = "183729"

# Путь к базе данных
db_path = os.path.join(os.path.dirname(__file__), "app", "data", "app.db")

print(f"Подключение к базе данных: {db_path}")

if not os.path.exists(db_path):
    print(f"ОШИБКА: Файл базы данных не найден: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Показываем текущих пользователей
print("\nТекущие пользователи:")
cursor.execute("SELECT id, username, is_admin FROM users")
users = cursor.fetchall()
for user in users:
    print(f"  ID: {user['id']}, Username: {user['username']}, Admin: {bool(user['is_admin'])}")

# Удаляем всех пользователей
print("\nУдаляем всех пользователей...")
cursor.execute("DELETE FROM users")
conn.commit()
print(f"Удалено: {cursor.rowcount} пользователей")

# Создаём нового админа
print(f"\nСоздаём админа '{USERNAME}' с паролем '{PASSWORD}'...")
password_hash = generate_password_hash(PASSWORD)
cursor.execute(
    "INSERT INTO users (username, password_hash, is_admin, last_login) VALUES (?, ?, 1, CURRENT_TIMESTAMP)",
    (USERNAME, password_hash)
)
conn.commit()
print("✓ Админ создан")

# Проверяем результат
print("\nНовые пользователи:")
cursor.execute("SELECT id, username, is_admin FROM users")
users = cursor.fetchall()
for user in users:
    print(f"  ID: {user['id']}, Username: {user['username']}, Admin: {bool(user['is_admin'])}")

conn.close()
print("\n✓ Готово! Теперь можно войти с логином 'admin' и паролем '183729'")
