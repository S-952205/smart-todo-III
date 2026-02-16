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

    def _parse_tool_arguments(self, args_str: str) -> Dict[str, Any]:
        """
        Comprehensive parser for malformed tool arguments from LLM responses.
        Handles multiple malformation patterns with fallback strategies.
        """
        import json
        import re

        if not args_str or not isinstance(args_str, str):
            return {}

        args_str = args_str.strip()
        logger.info(f"Parsing tool arguments: {args_str[:100]}...")

        # Strategy 1: Try normal JSON parsing
        try:
            result = json.loads(args_str)
            logger.info(f"Successfully parsed with standard JSON parser")
            return result
        except json.JSONDecodeError as e:
            logger.warning(f"Standard JSON parsing failed: {str(e)}")

        # Strategy 2: Handle duplicated JSON objects like: {...}, "{...}"
        # Remove string-quoted JSON duplicates
        try:
            # Find the first valid JSON object
            first_brace = args_str.find('{')
            if first_brace != -1:
                # Try to find matching closing brace
                brace_count = 0
                end_pos = first_brace
                for i in range(first_brace, len(args_str)):
                    if args_str[i] == '{':
                        brace_count += 1
                    elif args_str[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_pos = i + 1
                            break

                # Extract first complete JSON object
                first_json = args_str[first_brace:end_pos]
                result = json.loads(first_json)
                logger.info(f"Successfully extracted first JSON object")
                return result
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"First JSON object extraction failed: {str(e)}")

        # Strategy 3: Fix incomplete JSON (missing braces/quotes)
        try:
            fixed_str = args_str

            # Add missing closing braces
            open_braces = fixed_str.count('{')
            close_braces = fixed_str.count('}')
            if open_braces > close_braces:
                fixed_str += '}' * (open_braces - close_braces)

            # Add missing closing quotes (if odd number of quotes)
            quote_count = fixed_str.count('"')
            if quote_count % 2 != 0:
                fixed_str += '"'
                # Recheck braces after adding quote
                if fixed_str.count('{') > fixed_str.count('}'):
                    fixed_str += '}' * (fixed_str.count('{') - fixed_str.count('}'))

            result = json.loads(fixed_str)
            logger.info(f"Successfully parsed after fixing incomplete JSON")
            return result
        except json.JSONDecodeError as e:
            logger.warning(f"Fixed JSON parsing failed: {str(e)}")

        # Strategy 4: Extract all JSON objects and use the most complete one
        try:
            json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
            json_objects = re.findall(json_pattern, args_str)

            best_result = {}
            max_keys = 0

            for json_str in json_objects:
                try:
                    parsed = json.loads(json_str)
                    if isinstance(parsed, dict) and len(parsed) > max_keys:
                        best_result = parsed
                        max_keys = len(parsed)
                except:
                    continue

            if best_result:
                logger.info(f"Successfully extracted best JSON object with {max_keys} keys")
                return best_result
        except Exception as e:
            logger.warning(f"Pattern extraction failed: {str(e)}")

        # Strategy 5: Manual key-value extraction as last resort
        try:
            result = {}

            # Extract common parameters
            patterns = {
                'task_id': r'"task_id"\s*:\s*(\d+)',
                'title': r'"title"\s*:\s*"([^"]*)"',
                'description': r'"description"\s*:\s*"([^"]*)"',
                'status': r'"status"\s*:\s*"([^"]*)"',
                'priority': r'"priority"\s*:\s*"([^"]*)"',
            }

            for key, pattern in patterns.items():
                match = re.search(pattern, args_str)
                if match:
                    value = match.group(1)
                    # Convert task_id to int
                    if key == 'task_id':
                        try:
                            result[key] = int(value)
                        except ValueError:
                            result[key] = value
                    else:
                        result[key] = value

            if result:
                logger.info(f"Successfully extracted parameters manually: {result}")
                return result
        except Exception as e:
            logger.error(f"Manual extraction failed: {str(e)}")

        # All strategies failed
        logger.error(f"All parsing strategies failed for: {args_str}")
        return {}

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
                        "description": "List all tasks for the user with their IDs, titles, status, and priority. CRITICAL: You MUST call this function FIRST whenever the user refers to a task by its title or description (e.g., 'update my grocery task', 'complete the meeting task'). This is the ONLY way to get task IDs needed for update_task, complete_task, and delete_task operations.",
                        "parameters": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "complete_task",
                        "description": "Mark a task as complete (sets status to 'done'). REQUIRES the numeric task_id. If you don't have the task_id, you MUST call list_tasks first to get it.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "task_id": {
                                    "type": "integer",
                                    "description": "REQUIRED: Numeric ID of the task to complete (get this from list_tasks if you don't have it)"
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
                        "description": "Update an existing task's properties. REQUIRES the numeric task_id. If you don't have the task_id, you MUST call list_tasks first to get it.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "task_id": {
                                    "type": "integer",
                                    "description": "REQUIRED: Numeric ID of the task to update (get this from list_tasks if you don't have it)"
                                },
                                "title": {
                                    "type": "string",
                                    "description": "New title for the task (optional)"
                                },
                                "description": {
                                    "type": "string",
                                    "description": "New description for the task (optional)"
                                },
                                "status": {
                                    "type": "string",
                                    "enum": ["todo", "in-progress", "done"],
                                    "description": "New status for the task: 'todo', 'in-progress', or 'done' (optional)"
                                },
                                "priority": {
                                    "type": "string",
                                    "enum": ["low", "medium", "high"],
                                    "description": "New priority for the task: 'low', 'medium', or 'high' (optional)"
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
                        "description": "Delete a task permanently. REQUIRES the numeric task_id. If you don't have the task_id, you MUST call list_tasks first to get it.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "task_id": {
                                    "type": "integer",
                                    "description": "REQUIRED: Numeric ID of the task to delete (get this from list_tasks if you don't have it)"
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
- ALWAYS provide complete arguments - never send empty objects {{}}
- If you're unsure about a parameter, ask the user for clarification instead of omitting it

TASK MANAGEMENT INSTRUCTIONS:

CRITICAL WORKFLOW RULES:
1. When user refers to a task by title/description (NOT by ID number), you MUST:
   Step 1: Call list_tasks() to get all tasks with their IDs
   Step 2: Find the matching task in the results
   Step 3: Use that task's ID to call update_task/complete_task/delete_task

2. When user provides a specific task ID number, you can directly call the operation

EXAMPLES OF CORRECT WORKFLOW:
- User: "set status of my grocery task to in progress"
  → Step 1: Call list_tasks()
  → Step 2: Find task with title containing "grocery"
  → Step 3: Call update_task(task_id=X, status="in-progress")

- User: "complete the meeting prep task"
  → Step 1: Call list_tasks()
  → Step 2: Find task with title containing "meeting prep"
  → Step 3: Call complete_task(task_id=X)

- User: "update task 43 to high priority"
  → Directly call update_task(task_id=43, priority="high")

TOOL USAGE GUIDELINES:
- add_task: Extract title from user message. Title is REQUIRED.
  Examples: "add task movie night" → title: "movie night"

- list_tasks: Call this FIRST when user refers to tasks by name/description
  Returns: List of tasks with id, title, status, priority

- update_task: Requires task_id (integer). Optional: title, description, status, priority
  Valid status: "todo", "in-progress", "done"
  Valid priority: "low", "medium", "high"

- complete_task: Requires task_id (integer). Sets status to "done"

- delete_task: Requires task_id (integer). Permanently removes the task

RESPONSE GUIDELINES:
- After tool execution, provide natural language confirmation
- If tool fails, explain the error clearly
- If you can't find a matching task, tell the user and show available tasks"""
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

            # Validate response structure
            if not response or not response.choices or len(response.choices) == 0:
                logger.error(f"Invalid API response: {response}")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="The AI service returned an invalid response. Please try again."
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
                        function_args = self._parse_tool_arguments(tool_call.function.arguments)
                    elif isinstance(tool_call.function.arguments, dict):
                        function_args = tool_call.function.arguments
                    else:
                        logger.warning(f"Unexpected arguments type: {type(tool_call.function.arguments)}")
                        function_args = {}

                    logger.info(f"Executing tool: {function_name} with args: {function_args}")

                    # Execute the appropriate MCP tool
                    try:
                        if function_name == "add_task":
                            # Validate required parameters
                            title = function_args.get("title")

                            # Fallback: Try to extract title from user message if missing
                            if not title:
                                logger.warning("Title missing from tool arguments, attempting to extract from user message")
                                # Try to extract task title from the last user message
                                import re
                                user_msg = user_message.lower()

                                # Common patterns for task creation
                                patterns = [
                                    r'(?:add|create|make|new)\s+(?:a\s+)?(?:task|todo|reminder)?\s*(?:to\s+|for\s+|:)?\s*(.+)',
                                    r'(?:remind me to|i need to|todo:)\s+(.+)',
                                    r'task:\s*(.+)',
                                ]

                                for pattern in patterns:
                                    match = re.search(pattern, user_msg, re.IGNORECASE)
                                    if match:
                                        title = match.group(1).strip()
                                        logger.info(f"Extracted title from user message: {title}")
                                        break

                            if not title:
                                raise ValueError("Missing required parameter 'title' for add_task. The LLM may have provided incomplete arguments and fallback extraction failed. Please try rephrasing your request more clearly.")

                            result = mcp_tools.add_task(
                                title=title,
                                description=function_args.get("description")
                            )
                        elif function_name == "list_tasks":
                            result = mcp_tools.list_tasks()
                        elif function_name == "complete_task":
                            # Validate required parameters
                            task_id = function_args.get("task_id")
                            if not task_id:
                                raise ValueError("Missing required parameter 'task_id' for complete_task")

                            result = mcp_tools.complete_task(task_id)
                        elif function_name == "update_task":
                            # Validate required parameters
                            task_id = function_args.get("task_id")
                            if not task_id:
                                raise ValueError("Missing required parameter 'task_id' for update_task")

                            result = mcp_tools.update_task(
                                task_id=task_id,
                                title=function_args.get("title"),
                                description=function_args.get("description"),
                                status=function_args.get("status"),
                                priority=function_args.get("priority")
                            )
                        elif function_name == "delete_task":
                            # Validate required parameters
                            task_id = function_args.get("task_id")
                            if not task_id:
                                raise ValueError("Missing required parameter 'task_id' for delete_task")

                            result = mcp_tools.delete_task(task_id)
                        else:
                            result = {"error": f"Unknown function: {function_name}"}

                        # Convert result to string for tool response
                        result_str = json.dumps(result) if isinstance(result, (dict, list)) else str(result)

                    except ValueError as val_error:
                        logger.error(f"Validation error for tool {function_name}: {str(val_error)}")
                        result_str = json.dumps({
                            "error": f"Invalid parameters: {str(val_error)}",
                            "hint": "The AI model may have provided incomplete information. Please try rephrasing your request."
                        })
                    except Exception as tool_error:
                        logger.error(f"Error executing tool {function_name}: {str(tool_error)}")
                        import traceback
                        traceback.print_exc()
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

                # Validate final response structure
                if not final_response or not final_response.choices or len(final_response.choices) == 0:
                    logger.error(f"Invalid final API response: {final_response}")
                    # Provide a fallback response instead of crashing
                    assistant_response = "I attempted to complete your request, but encountered an issue getting a response from the AI service. The operation may have been completed - please check your tasks."
                else:
                    assistant_response = final_response.choices[0].message.content

                    # Handle case where content is None
                    if not assistant_response:
                        assistant_response = "Task operation completed successfully."
            else:
                # No tool calls, use the direct response
                assistant_response = response_message.content

                # Check if the model outputted tool call syntax as text (common issue with some models)
                if assistant_response and ('<tool_call>' in assistant_response or '<function=' in assistant_response or '<|tool_call_start|>' in assistant_response or ('"name"' in assistant_response and '"arguments"' in assistant_response)):
                    logger.warning(f"Model outputted tool call syntax as text instead of using proper tool calling")

                    # Try to parse and execute the tool call from text
                    import re
                    try:
                        # Check for XML parameter format: <function=name><parameter=key>value</parameter></function>
                        xml_param_match = re.search(r'<function=(\w+)>(.*?)</function>', assistant_response, re.DOTALL)

                        if xml_param_match:
                            function_name = xml_param_match.group(1)
                            params_block = xml_param_match.group(2)

                            logger.info(f"Detected XML parameter format: {function_name}")

                            # Extract all parameters
                            function_args = {}
                            param_matches = re.findall(r'<parameter=(\w+)>(.*?)</parameter>', params_block, re.DOTALL)
                            for param_name, param_value in param_matches:
                                function_args[param_name] = param_value.strip()

                            logger.info(f"Parsed XML parameters: {function_name} with args: {function_args}")

                            # Execute the tool
                            if function_name == "add_task":
                                title = function_args.get('title')
                                if title:
                                    result = mcp_tools.add_task(
                                        title=title,
                                        description=function_args.get('description')
                                    )
                                    assistant_response = f"Task created successfully! '{result.get('title')}' has been added."
                                else:
                                    assistant_response = "I couldn't extract the task title. Please try again."

                            elif function_name == "list_tasks":
                                result = mcp_tools.list_tasks()
                                if result:
                                    task_list = "\n".join([f"- {t['id']}: {t['title']} (Status: {t['status']}, Priority: {t['priority']})" for t in result])
                                    assistant_response = f"You have {len(result)} tasks:\n{task_list}"
                                else:
                                    assistant_response = "You don't have any tasks yet."

                            elif function_name == "update_task":
                                task_id = function_args.get('task_id')
                                if task_id:
                                    try:
                                        task_id = int(task_id)
                                        result = mcp_tools.update_task(
                                            task_id=task_id,
                                            title=function_args.get('title'),
                                            description=function_args.get('description'),
                                            status=function_args.get('status'),
                                            priority=function_args.get('priority')
                                        )
                                        assistant_response = f"Task updated successfully! '{result.get('title', 'Task')}' has been updated."
                                    except ValueError:
                                        assistant_response = "Invalid task ID format. Please provide a valid task ID."
                                else:
                                    assistant_response = "I couldn't find the task ID. Please try again."

                            elif function_name == "complete_task":
                                task_id = function_args.get('task_id')
                                if task_id:
                                    try:
                                        task_id = int(task_id)
                                        result = mcp_tools.complete_task(task_id)
                                        assistant_response = f"Task '{result.get('title')}' marked as complete!"
                                    except ValueError:
                                        assistant_response = "Invalid task ID format. Please provide a valid task ID."
                                else:
                                    assistant_response = "I couldn't find the task ID. Please try again."

                            elif function_name == "delete_task":
                                task_id = function_args.get('task_id')
                                if task_id:
                                    try:
                                        task_id = int(task_id)
                                        mcp_tools.delete_task(task_id)
                                        assistant_response = "Task deleted successfully!"
                                    except ValueError:
                                        assistant_response = "Invalid task ID format. Please provide a valid task ID."
                                else:
                                    assistant_response = "I couldn't find the task ID. Please try again."
                            else:
                                assistant_response = f"Unknown function: {function_name}"

                        # Check for XML-style format: <tool_call><function=function_name>params</function></tool_call>
                        elif xml_func_match := re.search(r'<tool_call>\s*<function=(\w+)>\s*(.*?)\s*</function>\s*</tool_call>', assistant_response, re.DOTALL):
                            function_name = xml_func_match.group(1)
                            params_content = xml_func_match.group(2).strip()

                            logger.info(f"Detected XML-style tool call: {function_name}")

                            # Parse parameters if present (could be JSON or key=value pairs)
                            function_args = {}
                            if params_content:
                                # Try JSON first
                                try:
                                    function_args = json.loads(params_content)
                                except:
                                    # Try key=value pairs
                                    param_pattern = r'(\w+)=(["\'])(.*?)\2|(\w+)=(\d+)'
                                    for match in re.finditer(param_pattern, params_content):
                                        if match.group(1):
                                            function_args[match.group(1)] = match.group(3)
                                        else:
                                            function_args[match.group(4)] = int(match.group(5))

                            logger.info(f"Parsed XML tool call: {function_name} with args: {function_args}")

                            # Execute the tool
                            if function_name == "list_tasks":
                                result = mcp_tools.list_tasks()
                                if result:
                                    task_list = "\n".join([f"- {t['id']}: {t['title']} (Status: {t['status']}, Priority: {t['priority']})" for t in result])
                                    assistant_response = f"You have {len(result)} tasks:\n{task_list}"
                                else:
                                    assistant_response = "You don't have any tasks yet."

                            elif function_name == "add_task":
                                title = function_args.get('title')
                                if title:
                                    result = mcp_tools.add_task(
                                        title=title,
                                        description=function_args.get('description')
                                    )
                                    assistant_response = f"Task created successfully! '{result.get('title')}' has been added."
                                else:
                                    assistant_response = "I couldn't extract the task title. Please try again."

                            elif function_name == "update_task":
                                task_id = function_args.get('task_id')
                                if task_id:
                                    result = mcp_tools.update_task(
                                        task_id=task_id,
                                        title=function_args.get('title'),
                                        description=function_args.get('description'),
                                        status=function_args.get('status'),
                                        priority=function_args.get('priority')
                                    )
                                    assistant_response = f"Task updated successfully! '{result.get('title', 'Task')}' has been updated."
                                else:
                                    assistant_response = "I couldn't find the task ID. Please try again."

                            elif function_name == "complete_task":
                                task_id = function_args.get('task_id')
                                if task_id:
                                    result = mcp_tools.complete_task(task_id)
                                    assistant_response = f"Task '{result.get('title')}' marked as complete!"
                                else:
                                    assistant_response = "I couldn't find the task ID. Please try again."

                            elif function_name == "delete_task":
                                task_id = function_args.get('task_id')
                                if task_id:
                                    mcp_tools.delete_task(task_id)
                                    assistant_response = "Task deleted successfully!"
                                else:
                                    assistant_response = "I couldn't find the task ID. Please try again."
                            else:
                                assistant_response = f"Unknown function: {function_name}"

                        # Check for function call format: <|tool_call_start|>[function_name(param=value, ...)]<|tool_call_end|>
                        elif func_call_match := re.search(r'<\|tool_call_start\|\>\[(\w+)\((.*?)\)\]<\|tool_call_end\|\>', assistant_response, re.DOTALL):
                            function_name = func_call_match.group(1)
                            params_str = func_call_match.group(2)

                            logger.info(f"Detected function call format: {function_name}({params_str})")

                            # Parse parameters from function call syntax
                            function_args = {}
                            # Match param=value pairs, handling quoted strings
                            param_pattern = r'(\w+)=(["\'])(.*?)\2|(\w+)=(\d+)'
                            for match in re.finditer(param_pattern, params_str):
                                if match.group(1):  # String parameter
                                    param_name = match.group(1)
                                    param_value = match.group(3)
                                else:  # Numeric parameter
                                    param_name = match.group(4)
                                    param_value = int(match.group(5))

                                # Map common parameter name variations
                                if param_name == 'new_title':
                                    param_name = 'title'

                                function_args[param_name] = param_value

                            logger.info(f"Parsed function call: {function_name} with args: {function_args}")

                            # Execute the tool based on function name
                            if function_name == "update_task":
                                task_id = function_args.get('task_id')
                                if task_id:
                                    result = mcp_tools.update_task(
                                        task_id=task_id,
                                        title=function_args.get('title'),
                                        description=function_args.get('description'),
                                        status=function_args.get('status'),
                                        priority=function_args.get('priority'),
                                        due_date=None  # Not commonly passed in text format
                                    )
                                    assistant_response = f"Task updated successfully! '{result.get('title', 'Task')}' has been updated."
                                else:
                                    assistant_response = "I couldn't find the task ID. Please try again."

                            elif function_name == "add_task":
                                title = function_args.get('title')
                                if title:
                                    result = mcp_tools.add_task(
                                        title=title,
                                        description=function_args.get('description')
                                    )
                                    assistant_response = f"Task created successfully! '{result.get('title')}' has been added."
                                else:
                                    assistant_response = "I couldn't extract the task title. Please try again."

                            elif function_name == "list_tasks":
                                result = mcp_tools.list_tasks()
                                if result:
                                    task_list = "\n".join([f"- {t['id']}: {t['title']} (Status: {t['status']}, Priority: {t['priority']})" for t in result])
                                    assistant_response = f"You have {len(result)} tasks:\n{task_list}"
                                else:
                                    assistant_response = "You don't have any tasks yet."

                            elif function_name == "complete_task":
                                task_id = function_args.get('task_id')
                                if task_id:
                                    result = mcp_tools.complete_task(task_id)
                                    assistant_response = f"Task '{result.get('title')}' marked as complete!"
                                else:
                                    assistant_response = "I couldn't find the task ID. Please try again."

                            elif function_name == "delete_task":
                                task_id = function_args.get('task_id')
                                if task_id:
                                    mcp_tools.delete_task(task_id)
                                    assistant_response = "Task deleted successfully!"
                                else:
                                    assistant_response = "I couldn't find the task ID. Please try again."
                            else:
                                assistant_response = f"Unknown function: {function_name}"

                        else:
                            # Fallback to original JSON-based parsing
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
                                            status=function_args.get("status"),
                                            priority=function_args.get("priority")
                                        )
                                        assistant_response = f"Task updated successfully! '{result.get('title', 'Task')}' has been updated."
                                    else:
                                        assistant_response = "I couldn't find the task you're referring to. Please try listing your tasks first."

                                elif function_name == "list_tasks":
                                    result = mcp_tools.list_tasks()
                                    if result:
                                        task_list = "\n".join([f"- {t['id']}: {t['title']} (Status: {t['status']}, Priority: {t['priority']})" for t in result])
                                        assistant_response = f"You have {len(result)} tasks:\n{task_list}"
                                    else:
                                        assistant_response = "You don't have any tasks yet."

                                elif function_name == "add_task":
                                    title = function_args.get('title')
                                    if title:
                                        result = mcp_tools.add_task(
                                            title=title,
                                            description=function_args.get('description')
                                        )
                                        assistant_response = f"Task created successfully! '{result.get('title')}' has been added."
                                    else:
                                        assistant_response = "I couldn't extract the task title. Please try again."

                                elif function_name == "complete_task":
                                    task_id = function_args.get('task_id')
                                    if task_id:
                                        result = mcp_tools.complete_task(task_id)
                                        assistant_response = f"Task '{result.get('title')}' marked as complete!"
                                    else:
                                        assistant_response = "I couldn't find the task ID. Please try again."

                                elif function_name == "delete_task":
                                    task_id = function_args.get('task_id')
                                    if task_id:
                                        mcp_tools.delete_task(task_id)
                                        assistant_response = "Task deleted successfully!"
                                    else:
                                        assistant_response = "I couldn't find the task ID. Please try again."

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
