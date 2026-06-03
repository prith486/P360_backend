#!/usr/bin/env python
"""Test if app can be imported."""
import sys
print("Starting import test...")
sys.stdout.flush()

try:
    from app.main import app
    print("✓ Import successful!")
    print(f"✓ App created: {app.title}")
    sys.exit(0)
except Exception as e:
    print(f"✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
