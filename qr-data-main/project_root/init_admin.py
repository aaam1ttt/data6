#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скрипт для инициализации админа.
Создаёт базу данных если её нет, затем создаёт админа с указанными учётными данными.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import get_db
from app.models.users import list_users, delete_user, create_user, find_user_by_username

USERNAME = "admin"
PASSWORD = "183729"

def main():
    print("=" * 60)
    print("Инициализация админа")
    print("=" * 60)
    
    # Создаём приложение - это инициализирует базу данных
    app = create_app()
    
    with app.app_context():
        # Проверяем подключение к БД
        try:
            db = get_db()
            print(f"✓ Подключение к БД: {app.config['DATABASE_PATH']}")
        except Exception as e:
            print(f"✗ Ошибка подключения к БД: {e}")
            return 1
        
        # Показываем текущих пользователей
        print("\nТекущие пользователи:")
        try:
            users = list_users()
            if not users:
                print("  (нет пользователей)")
            for user in users:
                print(f"  - {user['username']} (ID: {user['id']}, admin: {bool(user['is_admin'])})")
        except Exception as e:
            print(f"  Ошибка при получении списка: {e}")
            users = []
        
        # Удаляем всех пользователей
        if users:
            print(f"\nУдаляем {len(users)} пользователей...")
            for user in users:
                try:
                    delete_user(user['id'])
                    print(f"  ✓ Удалён: {user['username']} (ID: {user['id']})")
                except Exception as e:
                    print(f"  ✗ Ошибка при удалении {user['username']}: {e}")
        
        # Создаём нового админа
        print(f"\nСоздаём админа '{USERNAME}' с паролем '{PASSWORD}'...")
        try:
            ok = create_user(USERNAME, PASSWORD, is_admin=True)
            if ok:
                print(f"✓ Админ '{USERNAME}' создан")
                new_user = find_user_by_username(USERNAME)
                if new_user:
                    print(f"  ID: {new_user['id']}")
                    print(f"  Admin: {bool(new_user['is_admin'])}")
            else:
                print("✗ Не удалось создать админа (возможно, уже существует)")
                return 1
        except Exception as e:
            print(f"✗ Ошибка при создании админа: {e}")
            return 1
        
        print("\n" + "=" * 60)
        print("✓ Готово!")
        print(f"  Логин: {USERNAME}")
        print(f"  Пароль: {PASSWORD}")
        print("=" * 60)
        
        return 0

if __name__ == "__main__":
    sys.exit(main())
