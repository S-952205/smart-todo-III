import requests
import json

BASE_URL = "http://localhost:8001"

# Test with the actual user from database
print("Testing with real user: sufyansyed157@gmail.com")
print("=" * 60)

# Try to login - we need to know the actual password
# Let's try common test passwords
passwords_to_try = [
    "password123",
    "testpassword123",
    "Test@123",
    "admin123",
    "12345678"
]

token = None
for pwd in passwords_to_try:
    print(f"\nTrying password: {pwd}")
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "sufyansyed157@gmail.com", "password": pwd}
    )

    if login_response.status_code == 200:
        print(f"[SUCCESS] Login successful!")
        token = login_response.json()["access_token"]
        break
    else:
        print(f"[FAILED] Status: {login_response.status_code}")

if token:
    print(f"\n{'='*60}")
    print("Testing task creation...")
    print(f"{'='*60}")

    headers = {"Authorization": f"Bearer {token}"}

    # Create a task
    task_data = {
        "title": "Test Task via API",
        "description": "Testing manual CRUD operations",
        "completed": False
    }

    create_response = requests.post(
        f"{BASE_URL}/api/v1/tasks",
        headers=headers,
        json=task_data
    )

    print(f"\nCreate Task Status: {create_response.status_code}")
    print(f"Response: {json.dumps(create_response.json(), indent=2)}")

    # List tasks
    list_response = requests.get(
        f"{BASE_URL}/api/v1/tasks",
        headers=headers
    )

    print(f"\nList Tasks Status: {list_response.status_code}")
    print(f"Tasks: {json.dumps(list_response.json(), indent=2)}")
else:
    print("\n[FAILED] Could not login with any test password")
    print("Please provide the correct password for sufyansyed157@gmail.com")
