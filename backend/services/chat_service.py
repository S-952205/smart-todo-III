"""
Chat Service using FastMCP's native sampling with OpenRouter
This properly integrates FastMCP tools with the chat functionality
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
from openai import AsyncOpenAI
from config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatService:
    """Service class for handling chat interactions with FastMCP integration"""

    def __init__(self):
        # Initialize OpenAI client for OpenRouter with required headers
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openrouter_api_key,
            default_headers={
                "HTTP-Referer": settings.app_url,
                "X-Title": settings.app_title
            }
        )

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
        Process a chat request using FastMCP tools via OpenRouter

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

            # Load conversation history BEFORE saving the new message
            message_statement = select(Message).where(
                Message.conversation_id == conversation_id
            ).order_by(Message.timestamp)
            history_messages = session.exec(message_statement).all()

            # Import MCP tools
            from tools.mcp_tools import MCPTaskTools

            # Create MCP tools instance for this user
            mcp_tools = MCPTaskTools(session, user_id)

            # Define tools in OpenAI function calling format
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "add_task",
                        "description": "Create a new task for the user",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "description": "Title of the task"
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Optional description of the task"
                                }
                            },
                            "required": ["title"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "list_tasks",
                        "description": "List all tasks for the user. Use this to find task IDs when the user refers to tasks by title.",
                        "parameters": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "complete_task",
                        "description": "Mark a task as complete",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "task_id": {
                                    "type": "integer",
                                    "description": "ID of the task to complete"
                                }
                            },
                            "required": ["task_id"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "update_task",
                        "description": "Update an existing task. Requires the task ID.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "task_id": {
                                    "type": "integer",
                                    "description": "ID of the task to update"
                                },
                                "title": {
                                    "type": "string",
                                    "description": "New title for the task"
                                },
                                "description": {
                                    "type": "string",
                                    "description": "New description for the task"
                                },
                                "completed": {
                                    "type": "boolean",
                                    "description": "New completion status"
                                }
                            },
                            "required": ["task_id"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "delete_task",
                        "description": "Delete a task. Requires the task ID.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "task_id": {
                                    "type": "integer",
                                    "description": "ID of the task to delete"
                                }
                            },
                            "required": ["task_id"]
                        }
                    }
                }
            ]

            # Prepare messages with conversation history
            messages = [
                {
                    "role": "system",
                    "content": f"""You are a helpful AI assistant that manages tasks for users.
You have access to task management tools. Use them to help the user with their tasks.
The current user ID is {user_id}. Always perform operations for this user only.

CRITICAL TOOL CALLING RULES:
- You MUST use the OpenAI function calling format to call tools
- NEVER write tool calls as text like <tool_call> or function_call()
- NEVER output JSON or XML representations of tool calls
- When you need to call a tool, use the native tool calling mechanism provided by the API
- The system will automatically execute your tool calls and return results

TASK MANAGEMENT INSTRUCTIONS:
- When the user asks you to create, list, update, complete, or delete tasks, use the appropriate tool
- When the user refers to a task by its title (e.g., "update my task buying new mobile"), you MUST:
  1. First call list_tasks to get all tasks
  2. Find the task with the matching title
  3. Use the task's ID to call update_task or delete_task
- Always use the proper tool functions: add_task, list_tasks, complete_task, update_task, delete_task
- After a tool is executed, provide a natural language response to the user about what was done"""
                }
            ]

            # Add conversation history
            for msg in history_messages:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

            # Add the current user message
            messages.append({
                "role": "user",
                "content": user_message
            })

            # Save user message after building the messages array
            self.save_message(session, conversation_id, "user", user_message)

            # Make initial API call with OpenRouter's native fallback
            response = await self.client.chat.completions.create(
                model=settings.openrouter_model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                extra_body={
                    "models": [
                        "openrouter/free",
                        "upstage/solar-pro-3:free",
                        "nvidia/nemotron-3-nano-30b-a3b:free"
                    ]
                }
            )

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            # If the model wants to call tools
            if tool_calls:
                # Add assistant's response to messages in the correct format
                messages.append({
                    "role": "assistant",
                    "content": response_message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        } for tc in tool_calls
                    ]
                })

                # Execute each tool call
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    import json
                    import re

                    # Parse function arguments - handle both string and dict formats
                    if isinstance(tool_call.function.arguments, str):
                        try:
                            # Try to parse normally first
                            function_args = json.loads(tool_call.function.arguments)
                        except json.JSONDecodeError as e:
                            # Handle malformed format like: {}{"title": "value"}
                            # Extract all JSON objects and use the non-empty one
                            logger.warning(f"Malformed tool arguments detected: {tool_call.function.arguments}")

                            # Find all JSON objects in the string
                            json_objects = re.findall(r'\{[^{}]*\}', tool_call.function.arguments)
                            function_args = {}

                            for json_str in json_objects:
                                try:
                                    parsed = json.loads(json_str)
                                    # Use the first non-empty object
                                    if parsed:
                                        function_args = parsed
                                        break
                                except:
                                    continue

                            if not function_args:
                                logger.error(f"Could not extract valid arguments from: {tool_call.function.arguments}")
                                function_args = {}
                    elif isinstance(tool_call.function.arguments, dict):
                        function_args = tool_call.function.arguments
                    else:
                        logger.warning(f"Unexpected arguments type: {type(tool_call.function.arguments)}")
                        function_args = {}

                    logger.info(f"Executing tool: {function_name} with args: {function_args}")

                    # Execute the appropriate MCP tool
                    try:
                        if function_name == "add_task":
                            result = mcp_tools.add_task(
                                title=function_args.get("title"),
                                description=function_args.get("description")
                            )
                        elif function_name == "list_tasks":
                            result = mcp_tools.list_tasks()
                        elif function_name == "complete_task":
                            result = mcp_tools.complete_task(function_args.get("task_id"))
                        elif function_name == "update_task":
                            result = mcp_tools.update_task(
                                task_id=function_args.get("task_id"),
                                title=function_args.get("title"),
                                description=function_args.get("description"),
                                completed=function_args.get("completed")
                            )
                        elif function_name == "delete_task":
                            result = mcp_tools.delete_task(function_args.get("task_id"))
                        else:
                            result = {"error": f"Unknown function: {function_name}"}

                        # Convert result to string for tool response
                        result_str = json.dumps(result) if isinstance(result, (dict, list)) else str(result)

                    except Exception as tool_error:
                        logger.error(f"Error executing tool {function_name}: {str(tool_error)}")
                        result_str = json.dumps({"error": f"Tool execution failed: {str(tool_error)}"})

                        # Rollback the session if there was a database error
                        try:
                            session.rollback()
                        except:
                            pass

                    # Add tool response to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": result_str
                    })

                # Get final response from the model with OpenRouter's native fallback
                final_response = await self.client.chat.completions.create(
                    model=settings.openrouter_model,
                    messages=messages,
                    extra_body={
                        "models": [
                            "openrouter/free",
                            "upstage/solar-pro-3:free",
                            "nvidia/nemotron-3-nano-30b-a3b:free"
                        ]
                    }
                )

                assistant_response = final_response.choices[0].message.content
            else:
                # No tool calls, use the direct response
                assistant_response = response_message.content

                # Check if the model outputted tool call syntax as text (common issue with some models)
                if assistant_response and ('<tool_call>' in assistant_response or ('"name"' in assistant_response and '"arguments"' in assistant_response)):
                    logger.warning(f"Model outputted tool call syntax as text instead of using proper tool calling")

                    # Try to parse and execute the tool call from text
                    import re
                    try:
                        # Remove XML-like tags if present
                        cleaned_response = re.sub(r'</?tool_call>', '', assistant_response).strip()

                        # Try to find JSON object
                        json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
                        if json_match:
                            tool_call_data = json.loads(json_match.group())
                            function_name = tool_call_data.get('name')
                            function_args = tool_call_data.get('arguments', {})

                            # If arguments is a string, parse it
                            if isinstance(function_args, str):
                                function_args = json.loads(function_args)

                            logger.info(f"Parsed text-based tool call: {function_name} with args: {function_args}")

                            # Execute the tool
                            if function_name == "update_task":
                                # Handle both 'id' and 'task_id' parameter names
                                if 'id' in function_args and 'task_id' not in function_args:
                                    function_args['task_id'] = function_args.pop('id')

                                # If no task_id provided, try to find by title
                                if not function_args.get('task_id') and function_args.get('title'):
                                    tasks = mcp_tools.list_tasks()
                                    matching_task = next((t for t in tasks if t['title'].lower() == function_args['title'].lower()), None)
                                    if matching_task:
                                        function_args['task_id'] = matching_task['id']

                                if function_args.get('task_id'):
                                    result = mcp_tools.update_task(
                                        task_id=function_args.get("task_id"),
                                        title=function_args.get("title"),
                                        description=function_args.get("description"),
                                        completed=function_args.get("completed")
                                    )
                                    assistant_response = f"Task updated successfully! '{result.get('title', 'Task')}' now has the description: {result.get('description', 'N/A')}"
                                else:
                                    assistant_response = "I couldn't find the task you're referring to. Please try listing your tasks first."

                            elif function_name == "list_tasks":
                                result = mcp_tools.list_tasks()
                                if result:
                                    task_list = "\n".join([f"- {t['id']}: {t['title']}" for t in result])
                                    assistant_response = f"You have {len(result)} tasks:\n{task_list}"
                                else:
                                    assistant_response = "You don't have any tasks yet."
                            else:
                                assistant_response = "I apologize, but I encountered an issue processing your request. Could you please try again?"
                    except Exception as parse_error:
                        logger.error(f"Failed to parse text-based tool call: {parse_error}")
                        import traceback
                        traceback.print_exc()
                        assistant_response = "I apologize, but I encountered an issue processing your request. Could you please rephrase what you'd like me to do?"

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
                    detail="The AI service is temporarily rate-limited. Please try again in a few moments, or consider upgrading to a paid API key for higher limits."
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
