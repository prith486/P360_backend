import subprocess
import time
import sys

def manage_server():
    print("Stopping existing python processes...")
    subprocess.run(["powershell", "-Command", "Get-Process python | Stop-Process -Force"], capture_output=True)
    time.sleep(2)
    
    print("Starting server...")
    with open("server_full.log", "w") as f:
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
            stdout=f,
            stderr=subprocess.STDOUT,
            cwd="c:\\Users\\PRIHTVIRAJ\\Desktop\\P360_BACKEND\\placement360-backend"
        )
    
    print("Waiting for server to start...")
    time.sleep(10)
    
    print("Running tests...")
    test_result = subprocess.run(
        [sys.executable, "scripts/test_endpoints.py"],
        capture_output=True,
        text=True,
        cwd="c:\\Users\\PRIHTVIRAJ\\Desktop\\P360_BACKEND\\placement360-backend"
    )
    print(test_result.stdout)
    print(test_result.stderr)
    
    print("Stopping server...")
    process.terminate()
    process.wait()
    
    print("Server log (last 100 lines):")
    with open("server_full.log", "r") as f:
        lines = f.readlines()
        for line in lines[-100:]:
            print(line, end="")

if __name__ == "__main__":
    manage_server()
