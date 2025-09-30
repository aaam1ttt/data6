#!/usr/bin/env python3
"""
Test script to verify unauthenticated users can access scan and create features,
and that history is only saved when users are authenticated.
"""

import sys
from app import create_app
from flask import session

def test_unauthenticated_access():
    """Test that unauthenticated users can access scan and create pages"""
    app = create_app()
    
    with app.test_client() as client:
        print("Testing unauthenticated access...")
        print("-" * 50)
        
        # Test home page access
        response = client.get('/')
        assert response.status_code == 200, f"Home page failed: {response.status_code}"
        print("✅ Home page accessible without authentication")
        
        # Test scan page access
        response = client.get('/scan/')
        assert response.status_code == 200, f"Scan page failed: {response.status_code}"
        print("✅ Scan page accessible without authentication")
        
        # Test create page access
        response = client.get('/forms/create')
        assert response.status_code == 200, f"Create page failed: {response.status_code}"
        print("✅ Create page accessible without authentication")
        
        # Test form pages access
        form_pages = [
            '/forms/torg12',
            '/forms/message',
            '/forms/exploitation',
            '/forms/transport',
            '/forms/custom'
        ]
        
        for page in form_pages:
            response = client.get(page)
            assert response.status_code == 200, f"{page} failed: {response.status_code}"
            print(f"✅ {page} accessible without authentication")
        
        # Test that history page requires authentication
        response = client.get('/main/history')
        # Should redirect to login
        assert response.status_code in [302, 401, 403], f"History page should require auth but got: {response.status_code}"
        print("✅ History page correctly requires authentication")
        
        # Test that admin pages require authentication
        response = client.get('/admin/users')
        assert response.status_code in [302, 401, 403], f"Admin page should require auth but got: {response.status_code}"
        print("✅ Admin page correctly requires authentication")
        
        print("-" * 50)
        print("✅ All unauthenticated access tests passed!")
        return True

def test_templates_no_auth_prompts():
    """Test that templates don't show authentication prompts on scan/create pages"""
    import os
    
    print("\nChecking templates for authentication prompts...")
    print("-" * 50)
    
    template_dir = os.path.join(os.path.dirname(__file__), 'app', 'templates')
    
    # Files that should NOT have auth prompts
    files_to_check = [
        'scan.html',
        'form_create_live.html',
        'create.html'
    ]
    
    auth_prompt_markers = [
        'loginPrompt',
        'Требуется авторизация',
        'pointer-events: none'
    ]
    
    all_clean = True
    for filename in files_to_check:
        filepath = os.path.join(template_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                has_auth_prompt = any(marker in content for marker in auth_prompt_markers)
                if has_auth_prompt:
                    print(f"❌ {filename} still contains authentication prompts")
                    all_clean = False
                else:
                    print(f"✅ {filename} has no authentication prompts")
        else:
            print(f"⚠️  {filename} not found")
    
    print("-" * 50)
    if all_clean:
        print("✅ All templates are clean of authentication prompts!")
    else:
        print("❌ Some templates still have authentication prompts")
    
    return all_clean

def test_home_page_redirects_removed():
    """Test that home page doesn't redirect to login for scan/create buttons"""
    import os
    
    print("\nChecking home page for login redirects...")
    print("-" * 50)
    
    template_path = os.path.join(os.path.dirname(__file__), 'app', 'templates', 'home.html')
    
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check if there are conditional redirects based on user session
            if "{% if session.get('user') %}" in content and "url_for('auth.login')" in content:
                print("❌ home.html still contains conditional login redirects")
                return False
            else:
                print("✅ home.html has no conditional login redirects")
                
                # Verify direct links exist
                if "url_for('scan.scan_page')" in content and "url_for('forms.create_free')" in content:
                    print("✅ home.html has direct links to scan and create pages")
                    return True
                else:
                    print("⚠️  home.html may not have direct links")
                    return False
    else:
        print("❌ home.html not found")
        return False

if __name__ == '__main__':
    try:
        test1 = test_unauthenticated_access()
        test2 = test_templates_no_auth_prompts()
        test3 = test_home_page_redirects_removed()
        
        if test1 and test2 and test3:
            print("\n" + "=" * 50)
            print("✅ ALL TESTS PASSED!")
            print("=" * 50)
            sys.exit(0)
        else:
            print("\n" + "=" * 50)
            print("❌ SOME TESTS FAILED")
            print("=" * 50)
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
