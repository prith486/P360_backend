#!/usr/bin/env python
"""Test which router import causes the hang."""
import sys
import time

routers = [
    "health", "auth", "students", "faculty", "questions", 
    "assessments", "submissions", "external_platforms", 
    "analytics", "companies", "ai", "database", "test_items"
]

print("Testing router imports one by one...")
sys.stdout.flush()

for router_name in routers:
    print(f"Importing {router_name}...", end=" ", flush=True)
    start = time.time()
    try:
        exec(f"from app.api.v1.{router_name} import router as {router_name}_router")
        elapsed = time.time() - start
        print(f"✓ ({elapsed:.2f}s)")
        sys.stdout.flush()
    except Exception as e:
        elapsed = time.time() - start
        print(f"✗ Error after {elapsed:.2f}s: {e}")
        sys.stdout.flush()
        import traceback
        traceback.print_exc()
        break

print("\n✓ Test completed!")
sys.stdout.flush()
