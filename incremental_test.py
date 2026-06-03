import sys
import os

print("--- DEBUG START ---")

# Mocking modules that might hang if needed
# sys.modules['sqlalchemy'] = MagicMock() 

print("Importing app.core.config...")
import app.core.config
print("DONE config")

print("Importing app.core.database...")
import app.core.database
print("DONE database")

print("Importing app.main...")
import app.main
print("DONE main")
