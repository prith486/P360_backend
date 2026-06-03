import sys
import time
print("STARTING SQA IMPORT...")
start = time.time()
import sqlalchemy
print(f"SQA IMPORT OK: {time.time() - start:.2f}s")

modules = [
    'app.core.config',
    'app.core.logging_config',
    'app.core.database',
    'app.core.validation',
    'app.core.exceptions',
    'app.models.base',
    'app.models.enums',
    'app.models.auth_user',
    'app.models.student',
    'app.models.faculty',
    'app.api.deps',
    'app.api.v1.health',
    'app.api.v1.auth',
    'app.api.v1.students',
    'app.api.v1.faculty',
    'app.api.v1.router',
    'app.main'
]

import importlib
for mod in modules:
    print(f"Checking {mod}...", end=" ", flush=True)
    try:
        importlib.import_module(mod)
        print("OK")
    except Exception as e:
        print(f"ERROR: {e}")
        break
