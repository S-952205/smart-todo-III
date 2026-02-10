import requests
import json

BASE_URL = "http://localhost:8001"

# Step 1: Login to get token
print("Step 1: Logging in...")
login_response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"email": "sufyansyed157@gmail.com", "password": "testpassword123"}
)
print(f"Login status: {login_response.status_code}")

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    print(f"Token obtained: {token[:20]}...")

    # Step 2: Create a task
    print("\nStep 2: Creating a task...")
    headers = {"Authorization": f"Bearer {token}"}
    task_data = {
        "title": "Test Task from API",
        "description": "Testing if task creation works",
        "completed": False
    }

    create_response = requests.post(
        f"{BASE_URL}/api/tasks",
        headers=headers,
        json=task_data
    )
    print(f"Create task status: {create_response.status_code}")
    print(f"Response: {create_response.text}")

    # Step 3: List tasks
    print("\nStep 3: Listing tasks...")
    list_response = requests.get(
        f"{BASE_URL}/api/tasks",
        headers=headers
    )
    print(f"List tasks status: {list_response.status_code}")
    print(f"Tasks: {list_response.text}")
else:
    print(f"Login failed: {login_response.text}")
