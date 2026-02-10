from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents import function_tool
import logging
from typing import Dict, List
from config import settings

logger = logging.getLogger(__name__)

# Configure OpenRouter API key
open_router = settings.openrouter_api_key
if not open_router:
    logger.warning("OPENROUTER_API_KEY not found in environment variables")
    open_router = "sk-or-v1-dummy-key-for-testing"  # Use dummy key if not set

# Configure AsyncOpenAI for OpenRouter with required headers
client = AsyncOpenAI(
    api_key=open_router,
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": settings.app_url,
        "X-Title": settings.app_title
    }
)

# Configure the model to use with OpenRouter
model = OpenAIChatCompletionsModel(
    model='mistralai/mistral-small-3.1-24b-instruct:free',
    openai_client=client
)

# Import OpenAI Agents SDK compatible tools for task management
from task_agents.tools import add_task, list_tasks, complete_task, update_task, delete_task

# Create the main todo management agent
todo_agent = Agent(
    name="Todo Manager",
    instructions="""You are a helpful AI assistant that manages user tasks and todos.
    You can add, list, complete, update, and delete tasks.
    Always ensure that the user is authorized to perform operations on tasks.
    Only operate on tasks that belong to the current user.
    Use the available tools to perform task operations.""",
    tools=[add_task, list_tasks, complete_task, update_task, delete_task],
    model=model,
)

def process_todo_request(user_message: str, user_id: str):
    """Process a todo-related request using the agent with OpenRouter"""
    try:
        # Create a specific agent for this request with user context
        agent = Agent(
            name="Task Assistant",
            instructions=f"""You are a helpful assistant for task management. Use the task management tools to help the user.
            The current user ID is {user_id}. Always ensure operations are performed for the correct user.
            Use the available tools to perform task operations like adding, listing, completing, updating, or deleting tasks.
            Always verify that the user is authorized to perform operations on tasks.""",
            tools=[add_task, list_tasks, complete_task, update_task, delete_task],
            model=model,
        )

        # Run the agent with the user's message
        result = Runner.run_sync(agent, user_message)
        response = result.final_output if hasattr(result, 'final_output') and result.final_output else str(result)

        return response
    except Exception as e:
        logger.error(f"Todo agent failed: {e}")
        return f"Sorry, I'm unable to process your request at the moment. Error: {str(e)}"