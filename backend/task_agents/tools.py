"""
OpenAI Agents SDK compatible tools for task management
These tools wrap the MCP task operations for use with the OpenAI Agents SDK
"""
from agents import function_tool
from typing import Optional, Dict, Any, List
from tools.mcp_tools import MCPTaskTools
from db import get_session
import logging

logger = logging.getLogger(__name__)


@function_tool
def add_task(title: str, description: Optional[str], user_id: str) -> Dict[str, Any]:
    """
    Add a new task for the user.

    Args:
        title: Title of the task to create
        description: Optional description of the task
        user_id: ID of the user creating the task

    Returns:
        Dictionary with created task details
    """
    session = next(get_session())
    try:
        tools = MCPTaskTools(session, user_id)
        result = tools.add_task(title, description)
        logger.info(f"Agent created task: {result['id']} for user: {user_id}")
        return result
    finally:
        session.close()


@function_tool
def list_tasks(user_id: str) -> List[Dict[str, Any]]:
    """
    List all tasks for the user.

    Args:
        user_id: ID of the user whose tasks to retrieve

    Returns:
        List of task dictionaries
    """
    session = next(get_session())
    try:
        tools = MCPTaskTools(session, user_id)
        result = tools.list_tasks()
        logger.info(f"Agent listed {len(result)} tasks for user: {user_id}")
        return result
    finally:
        session.close()


@function_tool
def complete_task(task_id: int, user_id: str) -> Dict[str, Any]:
    """
    Mark a task as complete for the user.

    Args:
        task_id: ID of the task to mark as complete
        user_id: ID of the user requesting the action

    Returns:
        Dictionary with updated task details
    """
    session = next(get_session())
    try:
        tools = MCPTaskTools(session, user_id)
        result = tools.complete_task(task_id)
        logger.info(f"Agent completed task: {task_id} for user: {user_id}")
        return result
    finally:
        session.close()


@function_tool
def update_task(
    task_id: int,
    user_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    completed: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Update an existing task for the user.

    Args:
        task_id: ID of the task to update
        user_id: ID of the user requesting the action
        title: New title (optional)
        description: New description (optional)
        completed: New completion status (optional)

    Returns:
        Dictionary with updated task details
    """
    session = next(get_session())
    try:
        tools = MCPTaskTools(session, user_id)
        result = tools.update_task(task_id, title, description, completed)
        logger.info(f"Agent updated task: {task_id} for user: {user_id}")
        return result
    finally:
        session.close()


@function_tool
def delete_task(task_id: int, user_id: str) -> bool:
    """
    Delete a task for the user.

    Args:
        task_id: ID of the task to delete
        user_id: ID of the user requesting the action

    Returns:
        Boolean indicating success
    """
    session = next(get_session())
    try:
        tools = MCPTaskTools(session, user_id)
        result = tools.delete_task(task_id)
        logger.info(f"Agent deleted task: {task_id} for user: {user_id}")
        return result
    finally:
        session.close()
