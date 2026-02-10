"""
Diagnostic script to verify task creation flow
This will help identify where the issue is occurring
"""
import requests
import json

BASE_URL = "http://localhost:8001"

print("="*70)
print("DIAGNOSTIC: TASK CREATION FLOW")
print("="*70)

# Step 1: Check backend health
print("\n1. Checking backend health...")
try:
    health_response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {health_response.status_code}")
    print(f"   Response: {health_response.json()}")
except Exception as e:
    print(f"   [ERROR] {e}")
    exit(1)

# Step 2: Login
print("\n2. Attempting login...")
login_response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"email": "crud_test@example.com", "password": "testpass123"}
)

if login_response.status_code != 200:
    print(f"   [FAILED] Status: {login_response.status_code}")
    print(f"   Response: {login_response.text}")
    exit(1)

token = login_response.json()["access_token"]
user_id = login_response.json()["user"]["id"]
print(f"   [SUCCESS] Logged in as user: {user_id}")

headers = {"Authorization": f"Bearer {token}"}

# Step 3: Check current tasks in database
print("\n3. Checking current tasks in database...")
from sqlmodel import Session, select
from db import engine
from models import Task

with Session(engine) as session:
    statement = select(Task).where(Task.user_id == user_id)
    db_tasks_before = session.exec(statement).all()
    print(f"   Tasks in database BEFORE: {len(db_tasks_before)}")
    for task in db_tasks_before:
        print(f"     - Task {task.id}: {task.title}")

# Step 4: Get tasks via API
print("\n4. Getting tasks via API...")
api_response = requests.get(f"{BASE_URL}/api/v1/tasks", headers=headers)
print(f"   Status: {api_response.status_code}")
if api_response.status_code == 200:
    api_tasks = api_response.json()
    print(f"   Tasks from API: {len(api_tasks)}")
    for task in api_tasks:
        print(f"     - Task {task['id']}: {task['title']}")
else:
    print(f"   [ERROR] {api_response.text}")

# Step 5: Create a new task via API
print("\n5. Creating a new task via API...")
task_data = {
    "title": "Diagnostic Test Task",
    "description": "Testing task creation flow",
    "completed": False
}

create_response = requests.post(
    f"{BASE_URL}/api/v1/tasks",
    headers=headers,
    json=task_data
)

print(f"   Status: {create_response.status_code}")
if create_response.status_code == 201:
    created_task = create_response.json()
    print(f"   [SUCCESS] Task created via API")
    print(f"   Task ID: {created_task['id']}")
    print(f"   Task Title: {created_task['title']}")
else:
    print(f"   [FAILED] {create_response.text}")
    exit(1)

# Step 6: Verify task in database
print("\n6. Verifying task in database...")
with Session(engine) as session:
    statement = select(Task).where(Task.user_id == user_id)
    db_tasks_after = session.exec(statement).all()
    print(f"   Tasks in database AFTER: {len(db_tasks_after)}")
    for task in db_tasks_after:
        print(f"     - Task {task.id}: {task.title}")

    # Check if the new task is in the database
    new_task_in_db = any(task.id == created_task['id'] for task in db_tasks_after)
    if new_task_in_db:
        print(f"\n   [SUCCESS] New task IS in the database!")
    else:
        print(f"\n   [FAILED] New task is NOT in the database!")

# Step 7: Check database connection
print("\n7. Checking database connection...")
from db import engine
print(f"   Database URL: {engine.url}")
print(f"   Database name: {engine.url.database}")

print("\n" + "="*70)
print("DIAGNOSTIC COMPLETE")
print("="*70)
