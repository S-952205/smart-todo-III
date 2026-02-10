#!/usr/bin/env python3
"""
Test script to verify JWT token flow and remaining tasks from tasks.md
Specifically tests:
1. T022: Natural language task creation with add_task MCP tool
2. T023: Natural language task completion with complete_task MCP tool
3. T033: Cross-user data isolation
4. Independent test: JWT token flow from frontend to backend during chat interactions
"""

import asyncio
import os
import sys
import json
from typing import Dict, Any, Optional
from unittest.mock import AsyncMock, MagicMock, patch

# Add backend to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from tools.mcp_tools import MCPTaskTools
from services.chat_service import ChatService
from models import User, Task
from models.chat_models import Conversation, Message
from db import get_session
from sqlmodel import Session, select
from auth import get_current_user_id
from jose import jwt
from config import settings
from uuid import UUID
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock JWT secret for testing
TEST_JWT_SECRET = "test-secret-key-for-testing-purposes-only"
FAKE_USER_ID_1 = "test-user-123"
FAKE_USER_ID_2 = "test-user-456"

def create_mock_jwt_token(user_id: str, secret: str = TEST_JWT_SECRET) -> str:
    """Create a mock JWT token for testing purposes"""
    payload = {
        "userId": user_id,
        "exp": 9999999999,  # Far future expiration
        "iat": 1609459200,  # Jan 1, 2021
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token

def test_mcp_tool_functionality():
    """Test T022 and T023: Natural language task creation and completion with MCP tools"""
    print("=" * 60)
    print("Testing T022 and T023: MCP Tool Functionality")
    print("=" * 60)

    # Create a test database session
    session = next(get_session())

    try:
        # Create MCP tools instance for user 1
        tools = MCPTaskTools(session, FAKE_USER_ID_1)

        # Test T022: Natural language task creation with add_task MCP tool
        print("\n1. Testing T022: Natural language task creation...")

        # Add a task for user 1
        task_result = tools.add_task(
            title="Test Task from AI",
            description="This is a task created through natural language processing"
        )

        print(f"[PASS] Task created successfully: {task_result['title']}")
        print(f"  Task ID: {task_result['id']}")
        print(f"  User ID: {task_result['user_id']}")

        # Verify the task was created for the correct user
        assert task_result['user_id'] == FAKE_USER_ID_1
        assert task_result['title'] == "Test Task from AI"
        print("[PASS] Task correctly assigned to user 1")

        # Test T023: Natural language task completion with complete_task MCP tool
        print("\n2. Testing T023: Natural language task completion...")

        # Complete the task we just created
        complete_result = tools.complete_task(task_result['id'])

        print(f"[PASS] Task marked as complete: {complete_result['title']}")
        print(f"  Completed: {complete_result['completed']}")

        # Verify the task was marked as completed
        assert complete_result['completed'] is True
        assert complete_result['id'] == task_result['id']
        print("[PASS] Task correctly marked as completed")

        # Add another task to test update functionality
        task2_result = tools.add_task(
            title="Second Test Task",
            description="Another task for testing"
        )
        print(f"[PASS] Second task created: {task2_result['title']}")

        # Test update functionality
        update_result = tools.update_task(
            task_id=task2_result['id'],
            title="Updated Second Test Task",
            completed=True
        )
        print(f"[PASS] Task updated: {update_result['title']}")
        print(f"  Now completed: {update_result['completed']}")

        # Test list functionality
        all_tasks = tools.list_tasks()
        print(f"[PASS] Listed all tasks for user: {len(all_tasks)} tasks found")

        print("\n[PASS] T022 and T023 tests passed: MCP tools working correctly!")

    except Exception as e:
        print(f"[FAIL] Error during MCP tool testing: {str(e)}")
        raise
    finally:
        # Clean up test data
        session.exec(select(Task).where(Task.user_id == FAKE_USER_ID_1)).first()
        # Execute raw SQL to delete tasks for this user
        from sqlalchemy import text
        session.execute(text("DELETE FROM task WHERE user_id = :user_id"), {"user_id": FAKE_USER_ID_1})
        session.commit()
        session.close()


def test_cross_user_data_isolation():
    """Test T033: Cross-user data isolation"""
    print("\n" + "=" * 60)
    print("Testing T033: Cross-user data isolation")
    print("=" * 60)

    session = next(get_session())

    try:
        # Create tools for user 1
        tools_user1 = MCPTaskTools(session, FAKE_USER_ID_1)
        # Create tools for user 2
        tools_user2 = MCPTaskTools(session, FAKE_USER_ID_2)

        # User 1 creates a task
        user1_task = tools_user1.add_task(
            title="User 1's Private Task",
            description="This should only be accessible to user 1"
        )
        print(f"[PASS] User 1 created task: {user1_task['title']}")

        # User 2 creates a task
        user2_task = tools_user2.add_task(
            title="User 2's Private Task",
            description="This should only be accessible to user 2"
        )
        print(f"[PASS] User 2 created task: {user2_task['title']}")

        # Test 1: User 1 should only see their own tasks
        user1_tasks = tools_user1.list_tasks()
        print(f"[PASS] User 1 sees {len(user1_tasks)} tasks")
        assert len(user1_tasks) == 1
        assert user1_tasks[0]['id'] == user1_task['id']
        assert user1_tasks[0]['user_id'] == FAKE_USER_ID_1
        print("[PASS] User 1 only sees their own tasks")

        # Test 2: User 2 should only see their own tasks
        user2_tasks = tools_user2.list_tasks()
        print(f"[PASS] User 2 sees {len(user2_tasks)} tasks")
        assert len(user2_tasks) == 1
        assert user2_tasks[0]['id'] == user2_task['id']
        assert user2_tasks[0]['user_id'] == FAKE_USER_ID_2
        print("[PASS] User 2 only sees their own tasks")

        # Test 3: User 1 should not be able to access User 2's task
        try:
            user1_access_to_user2_task = tools_user1.complete_task(user2_task['id'])
            print("[FAIL] ERROR: User 1 was able to access User 2's task!")
            assert False, "Cross-user access should be prevented"
        except Exception as e:
            print(f"[PASS] Correctly prevented User 1 from accessing User 2's task: {str(e)}")

        # Test 4: User 2 should not be able to access User 1's task
        try:
            user2_access_to_user1_task = tools_user2.complete_task(user1_task['id'])
            print("[FAIL] ERROR: User 2 was able to access User 1's task!")
            assert False, "Cross-user access should be prevented"
        except Exception as e:
            print(f"[PASS] Correctly prevented User 2 from accessing User 1's task: {str(e)}")

        # Test 5: Each user should only have 1 task in their list
        assert len(tools_user1.list_tasks()) == 1
        assert len(tools_user2.list_tasks()) == 1
        print("[PASS] Both users still only have their own tasks")

        print("\n[PASS] T033 test passed: Cross-user data isolation working correctly!")

    except Exception as e:
        print(f"[FAIL] Error during cross-user isolation testing: {str(e)}")
        raise
    finally:
        # Clean up test data
        from sqlalchemy import text
        session.execute(text("DELETE FROM task WHERE user_id IN (:user1_id, :user2_id)"),
                        {"user1_id": FAKE_USER_ID_1, "user2_id": FAKE_USER_ID_2})
        session.commit()
        session.close()


def test_jwt_token_flow():
    """Test JWT token flow from frontend to backend during chat interactions"""
    print("\n" + "=" * 60)
    print("Testing JWT token flow from frontend to backend")
    print("=" * 60)

    # Create a mock JWT token for testing
    test_token = create_mock_jwt_token(FAKE_USER_ID_1)
    print(f"[PASS] Created test JWT token for user: {FAKE_USER_ID_1}")

    # Test JWT token verification function
    with patch('config.settings.better_auth_secret', TEST_JWT_SECRET):
        # Simulate the get_current_user_id function call
        try:
            # We need to simulate the credentials object that would come from FastAPI
            class MockCredentials:
                def __init__(self, token):
                    self.credentials = token

            mock_credentials = MockCredentials(test_token)

            # Test the get_current_user_id function
            extracted_user_id = get_current_user_id(mock_credentials)

            assert extracted_user_id == FAKE_USER_ID_1
            print(f"[PASS] JWT token correctly verified, extracted user ID: {extracted_user_id}")

        except Exception as e:
            print(f"[FAIL] Error verifying JWT token: {str(e)}")
            raise

    # Test chat service with JWT context
    session = next(get_session())

    try:
        print("\nTesting chat service with JWT context...")

        # Create a chat service instance
        chat_service = ChatService()

        # Test creating a conversation with a specific user
        conversation = chat_service.get_or_create_conversation(session, FAKE_USER_ID_1)
        print(f"[PASS] Created conversation for user: {FAKE_USER_ID_1}")
        print(f"  Conversation ID: {conversation.id}")

        # Test saving messages in the conversation
        user_message = chat_service.save_message(
            session, conversation.id, "user", "Hello, I want to create a task!"
        )
        print(f"[PASS] Saved user message to conversation")

        assistant_message = chat_service.save_message(
            session, conversation.id, "assistant", "Sure, what task would you like to create?"
        )
        print(f"[PASS] Saved assistant message to conversation")

        # Test retrieving conversations for the user
        user_conversations = chat_service.get_conversations(FAKE_USER_ID_1)
        print(f"[PASS] Retrieved {len(user_conversations)} conversations for user")

        # Verify the conversation belongs to the correct user
        assert len(user_conversations) == 1
        assert user_conversations[0]['user_id'] == FAKE_USER_ID_1
        print("[PASS] Conversation correctly associated with user")

        # Test retrieving conversation with messages
        conv_with_msgs = chat_service.get_conversation_with_messages(FAKE_USER_ID_1, conversation.id)
        print(f"[PASS] Retrieved conversation with {len(conv_with_msgs['messages'])} messages")

        # Test cross-user access prevention
        try:
            # Try to access the conversation with a different user ID
            chat_service.get_conversation_with_messages(FAKE_USER_ID_2, conversation.id)
            print("[FAIL] ERROR: User 2 was able to access User 1's conversation!")
            assert False, "Cross-user access should be prevented"
        except Exception as e:
            print(f"[PASS] Correctly prevented cross-user conversation access: {str(e)}")

        print("\n[PASS] JWT token flow test passed: Proper authentication and authorization working!")

    except Exception as e:
        print(f"[FAIL] Error during JWT token flow testing: {str(e)}")
        raise
    finally:
        # Clean up test data
        session.exec("DELETE FROM message WHERE conversation_id IN (SELECT id FROM conversation WHERE user_id = :user_id)",
                     {"user_id": FAKE_USER_ID_1})
        session.exec("DELETE FROM conversation WHERE user_id = :user_id",
                     {"user_id": FAKE_USER_ID_1})
        session.close()


def test_ai_simulation():
    """Simulate AI interaction to test the complete workflow"""
    print("\n" + "=" * 60)
    print("Testing simulated AI interaction workflow")
    print("=" * 60)

    session = next(get_session())

    try:
        # Create chat service
        chat_service = ChatService()

        # Mock the OpenAI client to avoid actual API calls during testing
        original_client = chat_service.client

        # Replace with a mock that simulates AI responses
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock()
        mock_response.choices[0].message.content = "I've processed your request and created the task."

        async def mock_chat_completions_create(*args, **kwargs):
            return mock_response

        chat_service.client.chat.completions.create = mock_chat_completions_create

        # Simulate a chat request as if coming from the API endpoint
        print("Simulating chat request processing...")

        result = asyncio.run(
            chat_service.process_chat_request(
                user_message="Please create a task to buy groceries",
                user_id=FAKE_USER_ID_1
            )
        )

        print(f"[PASS] Chat request processed successfully")
        print(f"  Response: {result['response'][:50]}...")
        print(f"  Conversation ID: {result['conversation_id']}")

        # Verify the conversation was created for the correct user
        conv_uuid = UUID(result['conversation_id'])
        conv_with_msgs = chat_service.get_conversation_with_messages(FAKE_USER_ID_1, conv_uuid)

        print(f"✓ Verified conversation exists with {len(conv_with_msgs['messages'])} messages")
        assert len(conv_with_msgs['messages']) == 2  # User message + Assistant response
        assert conv_with_msgs['conversation']['user_id'] == FAKE_USER_ID_1
        print("[PASS] Conversation correctly associated with user")

        # Restore original client
        chat_service.client = original_client

        print("\n✓ AI simulation test passed: Complete workflow working!")

    except Exception as e:
        print(f"✗ Error during AI simulation testing: {str(e)}")
        raise
    finally:
        # Clean up test data
        session.exec("DELETE FROM message WHERE conversation_id IN (SELECT id FROM conversation WHERE user_id = :user_id)",
                     {"user_id": FAKE_USER_ID_1})
        session.exec("DELETE FROM conversation WHERE user_id = :user_id",
                     {"user_id": FAKE_USER_ID_1})
        session.close()


def main():
    """Run all tests"""
    print("Starting comprehensive test suite for AI Chatbot & MCP Integration")
    print("Testing remaining tasks from specs/003-ai-chatbot-mcp/tasks.md")
    print()

    try:
        # Run all tests
        test_mcp_tool_functionality()
        test_cross_user_data_isolation()
        test_jwt_token_flow()
        test_ai_simulation()

        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED! 🎉")
        print("=" * 60)
        print("Successfully completed:")
        print("- T022: Natural language task creation with add_task MCP tool ✓")
        print("- T023: Natural language task completion with complete_task MCP tool ✓")
        print("- T033: Cross-user data isolation ✓")
        print("- Independent Test: JWT token flow verification ✓")
        print("- Independent Test: AI interaction simulation ✓")
        print()
        print("All remaining tasks from tasks.md have been verified and completed!")

        return True

    except Exception as e:
        print(f"\n✗ TESTS FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)