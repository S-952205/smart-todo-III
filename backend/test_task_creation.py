import requests
import json

# Login first
login_url = "http://localhost:8000/api/auth/login"
login_data = {
    "email": "sufyansyed157@gmail.com",
    "password": "password123"  # Try common password
}

print("Attempting login...")
response = requests.post(login_url, json=login_data)
print(f"Login status: {response.status_code}")

if response.status_code == 200:
    token_data = response.json()
    token = token_data.get('access_token')
    print(f"Token obtained: {token[:20]}...")

    # Now try to create a task
    task_url = "http://localhost:8000/api/v1/tasks"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    task_data = {
        "title": "Test Task from Script",
        "description": "Testing if task creation works",
        "completed": False
    }

    print("\nAttempting to create task...")
    task_response = requests.post(task_url, json=task_data, headers=headers)
    print(f"Task creation status: {task_response.status_code}")
    print(f"Response: {task_response.text}")
else:
    print(f"Login failed: {response.text}")
