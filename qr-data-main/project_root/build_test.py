#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

try:
    from app import create_app
    app = create_app()
    print('Build successful')
    sys.exit(0)
except Exception as e:
    print(f'Build failed: {e}')
    sys.exit(1)