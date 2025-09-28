#!/usr/bin/env python3
"""
Test build script
"""

try:
    from app import create_app
    app = create_app()
    print("Build successful")
    exit(0)
except Exception as e:
    print(f"Build failed: {e}")
    exit(1)