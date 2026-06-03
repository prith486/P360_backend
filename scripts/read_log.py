import sys
with open(sys.argv[1], 'rb') as f:
    content = f.read().decode('utf-16-le', errors='ignore')
    lines = content.splitlines()
    for line in lines[-50:]:
        print(line)
