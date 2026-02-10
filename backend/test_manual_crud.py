"""
Test manual CRUD operations on port 8001
This tests the regular API endpoints (not through the agent)
"""
import requests
import json

BASE_URL = "http://localhost:8001"

print("="*70)
print("TESTING MANUAL CRUD OPERATIONS ON PORT 8001")
print("="*70)

# Step 1: Create a test user (if needed)
print("\n1. Creating/checking test user...")
signup_data = {
    "email": "crud_test@example.com",
    "name": "CRUD Test User",
    "password": "testpass123"
}

signup_response = requests.post(
    f"{BASE_URL}/api/auth/signup",
    json=signup_data
)

if signup_response.status_code == 201:
    print("[SUCCESS] Test user created")
elif signup_response.status_code == 409:
    print("[INFO] Test user already exists")
else:
    print(f"[WARNING] Signup status: {signup_response.status_code}")

# Step 2: Login
print("\n2. Logging in...")
login_response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"email": "crud_test@example.com", "password": "testpass123"}
)

if login_response.status_code != 200:
    print(f"[FAILED] Login failed: {login_response.status_code}")
    print(f"Response: {login_response.text}")
    exit(1)

token = login_response.json()["access_token"]
user_id = login_response.json()["user"]["id"]
print(f"[SUCCESS] Logged in as user: {user_id}")

headers = {"Authorization": f"Bearer {token}"}

# Step 3: Create a task
print("\n3. Creating a task...")
task_data = {
    "title": "Manual CRUD Test Task",
    "description": "Testing if manual task creation works",
    "completed": False
}

create_response = requests.post(
    f"{BASE_URL}/api/v1/tasks",
    headers=headers,
    json=task_data
)

print(f"Create Status: {create_response.status_code}")
if create_response.status_code == 201:
    created_task = create_response.json()
    task_id = created_task["id"]
    print(f"[SUCCESS] Task created with ID: {task_id}")
    print(f"Task details: {json.dumps(created_task, indent=2)}")
else:
    print(f"[FAILED] Response: {create_response.text}")
    exit(1)

# Step 4: List tasks
print("\n4. Listing all tasks...")
list_response = requests.get(
    f"{BASE_URL}/api/v1/tasks",
    headers=headers
)

print(f"List Status: {list_response.status_code}")
if list_response.status_code == 200:
    tasks = list_response.json()
    print(f"[SUCCESS] Found {len(tasks)} task(s)")
    for task in tasks:
        print(f"  - Task {task['id']}: {task['title']} (completed: {task['completed']})")
else:
    print(f"[FAILED] Response: {list_response.text}")

# Step 5: Update the task
print("\n5. Updating the task...")
update_data = {
    "title": "Updated Manual CRUD Test Task",
    "completed": True
}

update_response = requests.put(
    f"{BASE_URL}/api/v1/tasks/{task_id}",
    headers=headers,
    json=update_data
)

print(f"Update Status: {update_response.status_code}")
if update_response.status_code == 200:
    updated_task = update_response.json()
    print(f"[SUCCESS] Task updated")
    print(f"Updated details: {json.dumps(updated_task, indent=2)}")
else:
    print(f"[FAILED] Response: {update_response.text}")

# Step 6: Verify in database
print("\n6. Verifying task in database...")
from sqlmodel import Session, select
from db import engine
from models import Task

with Session(engine) as session:
    statement = select(Task).where(Task.id == task_id)
    db_task = session.exec(statement).first()

    if db_task:
        print(f"[SUCCESS] Task found in database!")
        print(f"  ID: {db_task.id}")
        print(f"  Title: {db_task.title}")
        print(f"  Completed: {db_task.completed}")
        print(f"  User ID: {db_task.user_id}")
    else:
        print(f"[FAILED] Task NOT found in database!")

# Step 7: Delete the task
print("\n7. Deleting the task...")
delete_response = requests.delete(
    f"{BASE_URL}/api/v1/tasks/{task_id}",
    headers=headers
)

print(f"Delete Status: {delete_response.status_code}")
if delete_response.status_code == 204:
    print(f"[SUCCESS] Task deleted")
else:
    print(f"[FAILED] Response: {delete_response.text}")

print("\n" + "="*70)
print("MANUAL CRUD TEST COMPLETED")
print("="*70)
