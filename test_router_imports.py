#!/usr/bin/env python
"""Test which router import causes the hang."""
import sys

routers_to_test = [
    "health",
    "auth",
    "students",
    "faculty",
    "questions",
    "assessments",
    "submissions",
    "external_platforms",
    "analytics",
    "companies",
    "ai",
    "database",
    "test_items",
]

print("Testing router imports...")
sys.stdout.flush()

for router_name in routers_to_test:
    try:
        print(f"Importing {router_name}...", end=" ")
        sys.stdout.flush()
        
        module = __import__(f"app.api.v1.{router_name}", fromlist=[router_name])
        print("✓")
        sys.stdout.flush()
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.stdout.flush()
        break

print("\n✓ All imports completed successfully!")
