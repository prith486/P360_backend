import sys
import os

# Set custom trace function
def trace_imports(frame, event, arg):
    if event == 'call':
        code = frame.f_code
        filename = code.co_filename
        if 'site-packages' not in filename and 'app' in filename:
            print(f"Importing: {filename}:{code.co_name}")
            sys.stdout.flush()
    return trace_imports

print("Starting Import Trace...")
sys.settrace(trace_imports)

try:
    from app.main import app
    print("SUCCESS: App imported fully!")
except Exception as e:
    print(f"FAILED: {e}")
finally:
    sys.settrace(None)
