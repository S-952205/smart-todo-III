"""
MCP Server for Task Management
This server exposes task management tools via the Model Context Protocol (MCP)
"""
import os
from typing import Optional, Dict, Any
from datetime import datetime
from fastmcp import FastMCP, Context
from sqlmodel import Session, select
from models import Task
from db import get_session
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP(
    name="Task Management Server",
    instructions="""
    This MCP server provides task management tools for a todo application.
    All operations are user-scoped and require authentication context.
    """
)

@mcp.tool()
async def add_task(
    title: str,
    user_id: str,
    description: Optional[str] = None,
    status: Optional[str] = "todo",
    priority: Optional[str] = "medium"
) -> Dict[str, Any]:
    """
    Create a new task for the authenticated user.

    Args:
        title: Title of the task (required)
        user_id: ID of the authenticated user (required, automatically provided by agent)
        description: Optional description of the task
        status: Task status ('todo', 'in-progress', 'done'), defaults to 'todo'
        priority: Task priority ('low', 'medium', 'high'), defaults to 'medium'

    Returns:
        Dictionary with created task details including id, title, status, priority
    """
    session = next(get_session())

    try:
        # Validate required fields
        if not title or not isinstance(title, str) or not title.strip():
            raise ValueError("Task title is required and must be a non-empty string")

        # Normalize status and priority
        valid_statuses = ['todo', 'in-progress', 'done']
        valid_priorities = ['low', 'medium', 'high']

        normalized_status = (status or 'todo').lower()
        if normalized_status not in valid_statuses:
            logger.warning(f"Invalid status '{status}', defaulting to 'todo'")
            normalized_status = 'todo'

        normalized_priority = (priority or 'medium').lower()
        if normalized_priority not in valid_priorities:
            logger.warning(f"Invalid priority '{priority}', defaulting to 'medium'")
            normalized_priority = 'medium'

        # Create task
        task = Task(
            title=title.strip(),
            description=description.strip() if description else None,
            status=normalized_status,
            priority=normalized_priority,
            user_id=user_id
        )

        session.add(task)
        session.commit()
        session.refresh(task)

        logger.info(f"Task created: {task.id} for user: {user_id}")

        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "user_id": task.user_id,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None
        }
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating task for user {user_id}: {str(e)}")
        raise
    finally:
        session.close()

@mcp.tool()
async def list_tasks(user_id: str) -> list:
    """
    List all tasks for the authenticated user.

    Args:
        user_id: ID of the authenticated user (required, automatically provided by agent)

    Returns:
        List of task dictionaries with id, title, description, status, priority
    """
    session = next(get_session())

    try:
        statement = select(Task).where(Task.user_id == user_id)
        tasks = session.exec(statement).all()

        logger.info(f"Retrieved {len(tasks)} tasks for user: {user_id}")

        task_list = []
        for task in tasks:
            task_list.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "user_id": task.user_id,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None
            })

        return task_list
    except Exception as e:
        logger.error(f"Error retrieving tasks for user {user_id}: {str(e)}")
        raise
    finally:
        session.close()

@mcp.tool()
async def update_task(
    task_id: int,
    user_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update an existing task for the authenticated user.

    Args:
        task_id: ID of the task to update (required)
        user_id: ID of the authenticated user (required, automatically provided by agent)
        title: New title (optional)
        description: New description (optional)
        status: New status ('todo', 'in-progress', 'done') (optional)
        priority: New priority ('low', 'medium', 'high') (optional)

    Returns:
        Dictionary with updated task details
    """
    session = next(get_session())

    try:
        statement = select(Task).where(Task.id == task_id).where(Task.user_id == user_id)
        task = session.exec(statement).first()

        if not task:
            raise ValueError(f"Task {task_id} not found or does not belong to user")

        # Update fields if provided
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if status is not None:
            task.status = status
        if priority is not None:
            task.priority = priority

        task.updated_at = datetime.now()

        session.add(task)
        session.commit()
        session.refresh(task)

        logger.info(f"Task updated: {task.id} for user: {user_id}")

        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "user_id": task.user_id,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None
        }
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating task {task_id} for user {user_id}: {str(e)}")
        raise
    finally:
        session.close()

@mcp.tool()
async def complete_task(task_id: int, user_id: str) -> Dict[str, Any]:
    """
    Mark a task as complete (status='done') for the authenticated user.

    Args:
        task_id: ID of the task to complete (required)
        user_id: ID of the authenticated user (required, automatically provided by agent)

    Returns:
        Dictionary with updated task details
    """
    session = next(get_session())

    try:
        statement = select(Task).where(Task.id == task_id).where(Task.user_id == user_id)
        task = session.exec(statement).first()

        if not task:
            raise ValueError(f"Task {task_id} not found or does not belong to user")

        task.status = 'done'
        task.updated_at = datetime.now()

        session.add(task)
        session.commit()
        session.refresh(task)

        logger.info(f"Task completed: {task.id} for user: {user_id}")

        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "user_id": task.user_id,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None
        }
    except Exception as e:
        session.rollback()
        logger.error(f"Error completing task {task_id} for user {user_id}: {str(e)}")
        raise
    finally:
        session.close()

@mcp.tool()
async def delete_task(task_id: int, user_id: str) -> Dict[str, str]:
    """
    Delete a task for the authenticated user.

    Args:
        task_id: ID of the task to delete (required)
        user_id: ID of the authenticated user (required, automatically provided by agent)

    Returns:
        Dictionary with success message
    """
    session = next(get_session())

    try:
        statement = select(Task).where(Task.id == task_id).where(Task.user_id == user_id)
        task = session.exec(statement).first()

        if not task:
            raise ValueError(f"Task {task_id} not found or does not belong to user")

        session.delete(task)
        session.commit()

        logger.info(f"Task deleted: {task_id} for user: {user_id}")

        return {"message": f"Task {task_id} deleted successfully"}
    except Exception as e:
        session.rollback()
        logger.error(f"Error deleting task {task_id} for user {user_id}: {str(e)}")
        raise
    finally:
        session.close()

# Run the MCP server
if __name__ == "__main__":
    mcp.run()
