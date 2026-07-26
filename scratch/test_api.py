import urllib.request
import urllib.parse
import json

BASE_URL = "http://127.0.0.1:8000/api"

def make_request(url, method="GET", data=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    req_data = None
    if data:
        req_data = json.dumps(data).encode("utf-8")
        
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw_err = e.read().decode("utf-8")
        try:
            return e.code, json.loads(raw_err)
        except Exception:
            return e.code, raw_err

def test_flow():
    print("--- 1. Testing Registration ---")
    reg_payload = {
        "full_name": "Test User",
        "email": "test@pulsefit.com",
        "password": "password123",
        "confirm_password": "password123",
        "gender": "male",
        "age": 28,
        "height": 180.0,
        "weight": 80.0
    }
    status, res = make_request(f"{BASE_URL}/auth/register", "POST", reg_payload)
    print(f"Status: {status}, Response: {res}\n")
    if status != 200:
        print("Registration failed, trying login directly in case user exists...")

    print("--- 2. Testing Login ---")
    login_payload = {
        "email": "test@pulsefit.com",
        "password": "password123"
    }
    status, login_res = make_request(f"{BASE_URL}/auth/login", "POST", login_payload)
    print(f"Status: {status}, Response: {login_res}\n")
    assert status == 200, "Login failed"
    token = login_res["access_token"]

    print("--- 3. Testing Get Profile ---")
    status, profile_res = make_request(f"{BASE_URL}/auth/profile", "GET", token=token)
    print(f"Status: {status}, Response: {profile_res}\n")
    assert status == 200

    print("--- 4. Testing Step Logging (12,000 steps to unlock Step Champion) ---")
    step_payload = {
        "steps": 12000
    }
    status, step_res = make_request(f"{BASE_URL}/steps", "POST", step_payload, token=token)
    print(f"Status: {status}, Response: {step_res}\n")
    assert status == 200

    print("--- 5. Testing Achievements Retrieval (should show First Step and Step Champion unlocked) ---")
    status, ach_res = make_request(f"{BASE_URL}/achievements", "GET", token=token)
    print(f"Status: {status}")
    for badge in ach_res:
        if badge["unlocked"]:
            print(f"  [UNLOCKED] Badge: '{badge['name']}' - {badge['description']}")
        else:
            print(f"  [LOCKED]   Badge: '{badge['name']}' - {badge['description']}")
    print("")

    print("--- 6. Testing Notifications Retrieval ---")
    status, notif_res = make_request(f"{BASE_URL}/notifications", "GET", token=token)
    print(f"Status: {status}")
    for n in notif_res:
        msg_safe = n['message'].encode('ascii', 'ignore').decode('ascii')
        title_safe = n['title'].encode('ascii', 'ignore').decode('ascii')
        print(f"  - [{n['type']}] Title: '{title_safe}', Msg: '{msg_safe}'")
    print("")

if __name__ == "__main__":
    test_flow()
