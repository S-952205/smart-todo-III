"""
Chat Service using OpenAI Agents SDK with MCP Integration
This properly integrates MCP tools with the chat functionality
"""
from typing import Dict, Any, Optional, List
from sqlmodel import Session, select
from models import User
from models.chat_models import Conversation, Message
from db import get_session
from fastapi import HTTPException, status
import logging
from uuid import UUID
from datetime import datetime
from agents import Agent, Runner
from agents.mcp import MCPServerStdio
from config import settings
import os
import sys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatService:
    """Service class for handling chat interactions with MCP integration"""

    def __init__(self):
        pass

    def get_or_create_conversation(self, session: Session, user_id: str, conversation_id: Optional[UUID] = None) -> Conversation:
        """Get existing conversation or create a new one"""
        if conversation_id:
            conversation = session.exec(
                select(Conversation).where(Conversation.id == conversation_id).where(Conversation.user_id == user_id)
            ).first()
            if conversation:
                return conversation

        # Create new conversation
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        logger.info(f"Created new conversation: {conversation.id} for user: {user_id}")
        return conversation

    def save_message(self, session: Session, conversation_id: UUID, role: str, content: str, metadata: Optional[Dict] = None) -> Message:
        """Save a message to the conversation"""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            metadata_=metadata
        )

        session.add(message)
        session.commit()
        session.refresh(message)

        logger.info(f"Saved message for conversation {conversation_id}, role: {role}")
        return message

    async def process_chat_request(self, user_message: str, user_id: str, conversation_id: Optional[UUID] = None) -> Dict[str, Any]:
        """
        Process a chat request using OpenAI Agents SDK with MCP tools

        Args:
            user_message: Message from the user
            user_id: ID of the authenticated user
            conversation_id: Optional conversation ID to continue existing conversation

        Returns:
            Dictionary with response and conversation ID
        """
        session = next(get_session())

        try:
            # Get or create conversation
            conversation = self.get_or_create_conversation(session, user_id, conversation_id)
            conversation_id = conversation.id

            # Load conversation history
            message_statement = select(Message).where(
                Message.conversation_id == conversation_id
            ).order_by(Message.timestamp)
            history_messages = session.exec(message_statement).all()

            # Save user message
            self.save_message(session, conversation_id, "user", user_message)

            # Get the path to the MCP server script
            backend_dir = os.path.dirname(os.path.abspath(__file__))
            mcp_server_path = os.path.join(backend_dir, "..", "mcp_server.py")
            mcp_server_path = os.path.abspath(mcp_server_path)

            # Get Python executable path
            python_executable = sys.executable

            logger.info(f"Starting MCP server at: {mcp_server_path}")
            logger.info(f"Using Python: {python_executable}")

            # Connect to MCP server via stdio
            async with MCPServerStdio(
                name="Task Management Server",
                params={
                    "command": python_executable,
                    "args": [mcp_server_path],
                    "env": {
                        **os.environ,
                        "PYTHONPATH": os.path.dirname(backend_dir),
                    }
                },
            ) as mcp_server:
                # Build conversation history for agent
                agent_messages = []
                for msg in history_messages:
                    agent_messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })

                # Create agent with MCP server
                agent = Agent(
                    name="Task Assistant",
                    instructions=f"""You are a helpful AI assistant that manages tasks for users.
You have access to task management tools via MCP. Use them to help the user with their tasks.

CRITICAL: The current user ID is: {user_id}
You MUST include user_id="{user_id}" as a parameter in EVERY tool call.

TOOL CALLING RULES:
1. add_task: ALWAYS include user_id="{user_id}" along with title and optional description, status, priority
   Example: add_task(title="Buy groceries", user_id="{user_id}")

2. list_tasks: ALWAYS include user_id="{user_id}"
   Example: list_tasks(user_id="{user_id}")

3. update_task: ALWAYS include task_id AND user_id="{user_id}"
   Example: update_task(task_id=43, user_id="{user_id}", status="in-progress")

4. complete_task: ALWAYS include task_id AND user_id="{user_id}"
   Example: complete_task(task_id=43, user_id="{user_id}")

5. delete_task: ALWAYS include task_id AND user_id="{user_id}"
   Example: delete_task(task_id=43, user_id="{user_id}")

WORKFLOW INSTRUCTIONS:
1. When the user refers to a task by title (not ID), you MUST:
   - First call list_tasks(user_id="{user_id}") to get all tasks with their IDs
   - Find the matching task in the results
   - Use that task's ID for update_task, complete_task, or delete_task

2. When the user provides a specific task ID number, you can directly call the operation

3. Always provide clear, natural language responses after tool execution

4. If a tool fails, explain the error clearly to the user

EXAMPLES:
- User: "add task buy groceries"
  → Call add_task(title="buy groceries", user_id="{user_id}")

- User: "show my tasks"
  → Call list_tasks(user_id="{user_id}")

- User: "set status of grocery task to in-progress"
  → Call list_tasks(user_id="{user_id}") → Find task with "grocery" in title → Call update_task(task_id=X, user_id="{user_id}", status="in-progress")

- User: "complete my meeting task"
  → Call list_tasks(user_id="{user_id}") → Find task with "meeting" in title → Call complete_task(task_id=X, user_id="{user_id}")

- User: "update task 43 to high priority"
  → Directly call update_task(task_id=43, user_id="{user_id}", priority="high")

Valid status values: "todo", "in-progress", "done"
Valid priority values: "low", "medium", "high"
""",
                    mcp_servers=[mcp_server],
                    model=settings.openrouter_model,
                )

                # Run the agent with the user's message
                logger.info(f"Running agent for user {user_id} with message: {user_message[:50]}...")

                result = await Runner.run(
                    agent=agent,
                    input=user_message,
                )

                assistant_response = result.final_output

                logger.info(f"Agent completed successfully for user {user_id}")

            # Save assistant message
            self.save_message(session, conversation_id, "assistant", assistant_response)

            # Update conversation timestamp
            conversation.updated_at = datetime.now()
            session.add(conversation)
            session.commit()

            logger.info(f"Processed chat request for user {user_id}, conversation {conversation_id}")

            return {
                "response": assistant_response,
                "conversation_id": str(conversation_id)
            }

        except Exception as e:
            logger.error(f"Error processing chat request for user {user_id}: {str(e)}")
            import traceback
            traceback.print_exc()

            # Handle rate limit errors specifically
            error_message = str(e)
            if "429" in error_message or "rate" in error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="The AI service is temporarily rate-limited. Please try again in a few moments."
                )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process chat request: {str(e)}"
            )
        finally:
            session.close()

    def get_conversations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all conversations for a user"""
        session = next(get_session())

        try:
            statement = select(Conversation).where(Conversation.user_id == user_id)
            conversations = session.exec(statement).all()

            conversation_list = []
            for conv in conversations:
                conversation_list.append({
                    "id": str(conv.id),
                    "user_id": conv.user_id,
                    "title": conv.title,
                    "created_at": conv.created_at.isoformat() if conv.created_at else None,
                    "updated_at": conv.updated_at.isoformat() if conv.updated_at else None
                })

            logger.info(f"Retrieved {len(conversation_list)} conversations for user: {user_id}")
            return conversation_list

        except Exception as e:
            logger.error(f"Error retrieving conversations for user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve conversations"
            )
        finally:
            session.close()

    def get_conversation_with_messages(self, user_id: str, conversation_id: UUID) -> Dict[str, Any]:
        """Get a specific conversation with its messages"""
        session = next(get_session())

        try:
            statement = select(Conversation).where(Conversation.id == conversation_id).where(Conversation.user_id == user_id)
            conversation = session.exec(statement).first()

            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found or does not belong to the authenticated user"
                )

            message_statement = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.timestamp)
            messages = session.exec(message_statement).all()

            message_list = []
            for msg in messages:
                message_list.append({
                    "id": str(msg.id),
                    "conversation_id": str(msg.conversation_id),
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                    "metadata": msg.metadata_
                })

            result = {
                "conversation": {
                    "id": str(conversation.id),
                    "user_id": conversation.user_id,
                    "title": conversation.title,
                    "created_at": conversation.created_at.isoformat() if conversation.created_at else None,
                    "updated_at": conversation.updated_at.isoformat() if conversation.updated_at else None
                },
                "messages": message_list
            }

            logger.info(f"Retrieved conversation {conversation_id} with {len(message_list)} messages for user: {user_id}")
            return result

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error retrieving conversation {conversation_id} for user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve conversation"
            )
        finally:
            session.close()

    def delete_conversation(self, user_id: str, conversation_id: UUID) -> bool:
        """Delete a conversation"""
        session = next(get_session())

        try:
            statement = select(Conversation).where(Conversation.id == conversation_id).where(Conversation.user_id == user_id)
            conversation = session.exec(statement).first()

            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found or does not belong to the authenticated user"
                )

            # Delete all messages in this conversation first
            message_statement = select(Message).where(Message.conversation_id == conversation_id)
            messages = session.exec(message_statement).all()
            for msg in messages:
                session.delete(msg)

            # Delete the conversation
            session.delete(conversation)
            session.commit()

            logger.info(f"Deleted conversation {conversation_id} for user: {user_id}")
            return True

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting conversation {conversation_id} for user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete conversation"
            )
        finally:
            session.close()
