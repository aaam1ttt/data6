#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

# Добавляем текущую директорию в путь Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.users import find_user_by_username, create_user, set_password, list_users, delete_user

USERNAME = "admin"
PASSWORD = "183729"

def main():
    app = create_app()
    with app.app_context():
        print("Текущие пользователи:")
        users = list_users()
        for user in users:
            print(f"  - {user['username']} (ID: {user['id']}, admin: {bool(user['is_admin'])})")
        
        print(f"\nУдаляем всех существующих пользователей...")
        for user in users:
            delete_user(user['id'])
            print(f"  Удалён: {user['username']} (ID: {user['id']})")
        
        print(f"\nСоздаём нового админа...")
        ok = create_user(USERNAME, PASSWORD, is_admin=True)
        if ok:
            print(f"✓ Админ '{USERNAME}' создан с паролем '{PASSWORD}'")
            new_user = find_user_by_username(USERNAME)
            print(f"  ID: {new_user['id']}")
        else:
            print("✗ Не удалось создать админа")
            return 1
        
        return 0

if __name__ == "__main__":
    sys.exit(main())
