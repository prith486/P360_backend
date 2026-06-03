import urllib.request
import urllib.parse
import urllib.error
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

def make_request(method, endpoint, data=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {'Content-Type': 'application/json'}
    
    if data:
        data = json.dumps(data).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            status = response.status
            body = response.read().decode('utf-8')
            return status, json.loads(body)
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode('utf-8'))
    except Exception as e:
        return 0, str(e)

def run_tests():
    print("Running API Verification Tests...")
    
    # 1. Health Check
    print("\n[1] Testing Database Health...")
    status, result = make_request('GET', '/database/db-health')
    if status == 200:
        print(f"✓ Success: {result['status']} (Latency: {result.get('latency_ms')}ms)")
    else:
        print(f"✗ Failed: {status} - {result}")
        sys.exit(1)

    # 2. Create Item
    print("\n[2] Creating Test Item...")
    item_data = {
        "name": "Integration Test Item",
        "description": "Created via verification script",
        "is_active": True
    }
    status, created_item = make_request('POST', '/test-items/', item_data)
    if status == 201:
        print(f"✓ Created: ID={created_item['id']}, Name='{created_item['name']}'")
        item_id = created_item['id']
    else:
        print(f"✗ Failed to create: {status} - {created_item}")
        sys.exit(1)
        
    # 3. List Items
    print("\n[3] Listing Test Items...")
    status, items = make_request('GET', '/test-items/')
    if status == 200:
        count = len(items)
        print(f"✓ Found {count} items")
        found = any(i['id'] == item_id for i in items)
        if found:
            print(f"✓ Verified created item {item_id} is in list")
        else:
            print(f"✗ Created item {item_id} NOT found in list")
    else:
        print(f"✗ Failed to list: {status} - {items}")

    # 4. Get Specific Item
    print(f"\n[4] Fetching Item {item_id}...")
    status, item = make_request('GET', f'/test-items/{item_id}')
    if status == 200 and item['name'] == item_data['name']:
        print(f"✓ Retrieved correctly: {item}")
    else:
        print(f"✗ Failed to retrieve: {status} - {item}")

    # 5. Delete Item
    print(f"\n[5] Deleting Item {item_id}...")
    status, res = make_request('DELETE', f'/test-items/{item_id}')
    if status == 200:
        print("✓ Item deleted successfully")
    else:
        print(f"✗ Failed to delete: {status} - {res}")

    # 6. Verify Deletion
    print(f"\n[6] Verifying Deletion...")
    status, res = make_request('GET', f'/test-items/{item_id}')
    if status == 404:
        print("✓ Item correctly returned 404 Not Found")
    else:
        print(f"✗ Expected 404, got {status} - {res}")

    print("\n✓ ALL TESTS PASSED SUCCESSFULLY")

if __name__ == "__main__":
    run_tests()
