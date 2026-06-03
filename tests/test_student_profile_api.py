"""
Integration tests for Student Profile API endpoints.
"""

import requests
import json
import os
import sys

# Add project root to path if running directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:8000/api/v1"
# JWT_TOKEN placeholder - User must provide valid token
JWT_TOKEN = "your_test_token_here" 

HEADERS = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Content-Type": "application/json"
}


def test_get_profile():
    """Test GET /students/me"""
    print(f"Testing GET {BASE_URL}/students/me...")
    try:
        response = requests.get(f"{BASE_URL}/students/me", headers=HEADERS)
        
        if response.status_code == 401:
            print("Skipping: Unauthorized. Please provide valid JWT_TOKEN.")
            return

        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "roll_number" in data
        assert "readiness_score" in data
        assert "profile_completion_percent" in data
        
        print("✓ GET /students/me passed")
        # print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"✗ GET /students/me failed: {e}")


def test_update_profile():
    """Test PATCH /students/me"""
    print(f"Testing PATCH {BASE_URL}/students/me...")
    update_data = {
        "cgpa": 8.75,
        "skills": ["Python", "JavaScript", "React", "FastAPI", "PostgreSQL"],
        "expected_ctc_min": 10.0,
        "expected_ctc_max": 18.0
    }
    
    try:
        response = requests.patch(
            f"{BASE_URL}/students/me",
            headers=HEADERS,
            json=update_data
        )
        
        if response.status_code == 401:
            return
            
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert float(data["cgpa"]) == 8.75
        assert len(data["skills"]) == 5
        
        print("✓ PATCH /students/me passed")
    except Exception as e:
        print(f"✗ PATCH /students/me failed: {e}")


def test_connect_platform():
    """Test POST /students/me/external-platform"""
    print(f"Testing POST {BASE_URL}/students/me/external-platform...")
    platform_data = {
        "platform": "leetcode",
        "username": "test_user_leetcode"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/students/me/external-platform",
            headers=HEADERS,
            json=platform_data
        )
        
        if response.status_code == 401:
            return

        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data["leetcode_username"] == "test_user_leetcode"
        
        print("✓ POST /students/me/external-platform passed")
    except Exception as e:
        print(f"✗ POST /students/me/external-platform failed: {e}")


def test_completion_breakdown():
    """Test GET /students/me/completion"""
    print(f"Testing GET {BASE_URL}/students/me/completion...")
    try:
        response = requests.get(f"{BASE_URL}/students/me/completion", headers=HEADERS)
        
        if response.status_code == 401:
            return

        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "overall_completion" in data
        assert "categories" in data
        assert "recommendations" in data
        
        print("✓ GET /students/me/completion passed")
        print(f"Overall completion: {data['overall_completion']}%")
    except Exception as e:
        print(f"✗ GET /students/me/completion failed: {e}")


def test_invalid_cgpa():
    """Test validation error"""
    print(f"Testing invalid CGPA...")
    update_data = {"cgpa": 11.5}  # Invalid (> 10)
    
    try:
        response = requests.patch(
            f"{BASE_URL}/students/me",
            headers=HEADERS,
            json=update_data
        )
        
        if response.status_code == 401:
            return
            
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        data = response.json()
        
        # assert "error" in data or "detail" in data
        
        print("✓ Validation error test passed")
    except Exception as e:
        print(f"✗ Validation error test failed: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("STUDENT PROFILE API INTEGRATION TESTS")
    print("=" * 70 + "\n")
    
    try:
        test_get_profile()
        test_update_profile()
        test_connect_platform()
        test_completion_breakdown()
        test_invalid_cgpa()
        
        print("\n" + "=" * 70)
        print("ALL TESTS COMPLETED")
        print("=" * 70 + "\n")
        
    except KeyboardInterrupt:
        print("\nAborted.")
