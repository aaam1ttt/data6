#!/usr/bin/env python3
import py_compile
import sys
import os

files_to_check = [
    'app/routes/scan.py',
    'app/routes/forms.py',
    'app/routes/main.py',
    'app/routes/admin.py',
    'app/__init__.py',
]

print("Validating Python syntax...")
all_valid = True

for filepath in files_to_check:
    full_path = os.path.join(os.path.dirname(__file__), filepath)
    try:
        py_compile.compile(full_path, doraise=True)
        print(f"✅ {filepath}: OK")
    except py_compile.PyCompileError as e:
        print(f"❌ {filepath}: SYNTAX ERROR")
        print(f"   {e}")
        all_valid = False

if all_valid:
    print("\n✅ All Python files have valid syntax")
    sys.exit(0)
else:
    print("\n❌ Some files have syntax errors")
    sys.exit(1)
