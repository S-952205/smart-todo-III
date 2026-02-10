"""
Test script to check if the agent can be imported from task_agents
"""
import sys
sys.path.insert(0, '/c/Projects/todo-full-app-III/backend')

print("Testing task_agents import and initialization...")

try:
    from task_agents.agent import process_todo_request
    print("[SUCCESS] Agent imported successfully from task_agents")

    # Try to process a simple request
    print("\nTesting agent with a simple request...")
    result = process_todo_request("List my tasks", "test-user-id")
    print(f"[SUCCESS] Agent response: {result}")

except ImportError as e:
    print(f"[FAILED] Import error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"[FAILED] Error: {e}")
    import traceback
    traceback.print_exc()
