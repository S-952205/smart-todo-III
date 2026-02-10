"""
Test the AI chatbot endpoint to see if it can actually perform task operations
"""
import requests
import json

BASE_URL = "http://localhost:8001"

print("="*70)
print("TESTING AI CHATBOT WITH MCP TOOLS")
print("="*70)

# Step 1: Login
print("\n1. Logging in as test user...")
login_response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"email": "crud_test@example.com", "password": "testpass123"}
)

if login_response.status_code != 200:
    print(f"[FAILED] Login failed: {login_response.status_code}")
    exit(1)

token = login_response.json()["access_token"]
user_id = login_response.json()["user"]["id"]
print(f"[SUCCESS] Logged in as user: {user_id}")

headers = {"Authorization": f"Bearer {token}"}

# Step 2: Send a chat message asking to create a task
print("\n2. Asking AI to create a task...")
chat_request = {
    "message": "Please create a task with title 'AI Created Task' and description 'This task was created by the AI agent'"
}

chat_response = requests.post(
    f"{BASE_URL}/api/v1/chat",
    headers=headers,
    json=chat_request
)

print(f"Chat Status: {chat_response.status_code}")
if chat_response.status_code == 200:
    chat_data = chat_response.json()
    print(f"[SUCCESS] AI Response:")
    print(f"{chat_data['response']}")
    print(f"\nConversation ID: {chat_data['conversation_id']}")
else:
    print(f"[FAILED] Response: {chat_response.text}")
    exit(1)

# Step 3: Check if task was actually created in database
print("\n3. Checking if task was actually created in database...")
from sqlmodel import Session, select
from db import engine
from models import Task

with Session(engine) as session:
    statement = select(Task).where(Task.user_id == user_id).where(Task.title == "AI Created Task")
    ai_task = session.exec(statement).first()

    if ai_task:
        print(f"[SUCCESS] Task was actually created by AI!")
        print(f"  ID: {ai_task.id}")
        print(f"  Title: {ai_task.title}")
        print(f"  Description: {ai_task.description}")
    else:
        print(f"[FAILED] Task was NOT created in database!")
        print(f"[INFO] The AI only responded with text but didn't execute the MCP tool")

# Step 4: List tasks via API to verify
print("\n4. Listing tasks via API...")
list_response = requests.get(
    f"{BASE_URL}/api/v1/tasks",
    headers=headers
)

if list_response.status_code == 200:
    tasks = list_response.json()
    print(f"[INFO] Total tasks in database: {len(tasks)}")
    for task in tasks:
        print(f"  - Task {task['id']}: {task['title']}")

print("\n" + "="*70)
print("AI CHATBOT TEST COMPLETED")
print("="*70)
