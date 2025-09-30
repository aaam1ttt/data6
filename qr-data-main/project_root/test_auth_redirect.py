"""Тест редиректа аутентификации на страницах сканирования и создания"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def test_scan_page_shows_login():
    """Проверка что страница сканирования показывает форму входа для неавторизованных пользователей"""
    app = create_app()
    with app.test_client() as client:
        response = client.get('/scan/')
        assert response.status_code == 200
        assert b'loginPrompt' in response.data or b'\xd0\xa2\xd1\x80\xd0\xb5\xd0\xb1\xd1\x83\xd0\xb5\xd1\x82\xd1\x81\xd1\x8f' in response.data  # "Требуется"
        print("[OK] Scan page shows login form")

def test_create_page_shows_login():
    """Проверка что страница создания показывает форму входа для неавторизованных пользователей"""
    app = create_app()
    with app.test_client() as client:
        response = client.get('/forms/create')
        assert response.status_code == 200
        assert b'loginPrompt' in response.data or b'\xd0\xa2\xd1\x80\xd0\xb5\xd0\xb1\xd1\x83\xd0\xb5\xd1\x82\xd1\x81\xd1\x8f' in response.data  # "Требуется"
        print("[OK] Create page shows login form")

def test_scan_login_redirects_back():
    """Проверка что вход со страницы сканирования возвращает обратно"""
    app = create_app()
    with app.test_client() as client:
        # Логин со страницы сканирования
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'admin123',
            'next': '/scan/'
        }, follow_redirects=False)
        
        # Должен быть редирект на /scan/
        assert response.status_code == 302
        assert '/scan/' in response.location or response.location.endswith('/scan/')
        print("[OK] Login from scan page redirects back to /scan/")

def test_create_login_redirects_back():
    """Проверка что вход со страницы создания возвращает обратно"""
    app = create_app()
    with app.test_client() as client:
        # Логин со страницы создания
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'admin123',
            'next': '/forms/create'
        }, follow_redirects=False)
        
        # Должен быть редирект на /forms/create
        assert response.status_code == 302
        assert '/forms/create' in response.location or response.location.endswith('/forms/create')
        print("[OK] Login from create page redirects back to /forms/create")

if __name__ == '__main__':
    print("\n=== Authentication Redirect Test ===\n")
    
    try:
        test_scan_page_shows_login()
        test_create_page_shows_login()
        test_scan_login_redirects_back()
        test_create_login_redirects_back()
        
        print("\n[SUCCESS] All tests passed!\n")
    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Test execution error: {e}\n")
        sys.exit(1)
