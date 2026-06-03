import sys
import time

class VerboseImport:
    def __init__(self):
        self.depth = 0
    
    def find_spec(self, fullname, path, target=None):
        print("  " * self.depth + f"Importing: {fullname}")
        self.depth += 1
        return None  # Continue with normal import

sys.meta_path.insert(0, VerboseImport())

print("STARTING HANG TRACE...")
try:
    import sqlalchemy
    print("SQLAlchemy OK")
    import app.main
    print("App OK")
except Exception as e:
    print(f"ERROR: {e}")
