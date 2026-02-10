"""
MCP Tools for task operations using FastMCP
These tools will be used by the AI agent to perform task operations
"""
from typing import Dict, Any, Optional
from sqlmodel import Session, select
from models import Task
from db import get_session
from fastapi import HTTPException, status
import logging
from datetime import datetime
from fastmcp import FastMCP

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP instance for our tools
mcp = FastMCP("Task Management MCP Server")

class MCPTaskTools:
    """MCP Tools for task operations compatible with FastMCP"""

    def __init__(self, db_session: Session, user_id: str):
        self.session = db_session
        self.user_id = user_id

    def add_task(self, title: str, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new task for the authenticated user.

        Args:
            title: Title of the task
            description: Optional description of the task

        Returns:
            Dictionary with task details
        """
        try:
            # Create task with the authenticated user's ID
            task = Task(
                title=title,
                description=description,
                completed=False,
                user_id=self.user_id
            )

            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)

            logger.info(f"Task created successfully: {task.id} for user: {self.user_id}")

            # Return task details
            return {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "user_id": task.user_id,
                "created_at": task.created_at.isoformat() if task.created_at else None
            }
        except Exception as e:
            logger.error(f"Error creating task for user {self.user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create task"
            )

    def list_tasks(self) -> list:
        """
        Retrieve all tasks for the authenticated user.

        Returns:
            List of task dictionaries
        """
        try:
            statement = select(Task).where(Task.user_id == self.user_id)
            tasks = self.session.exec(statement).all()

            logger.info(f"Retrieved {len(tasks)} tasks for user: {self.user_id}")

            # Convert to response model
            task_list = []
            for task in tasks:
                task_list.append({
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "user_id": task.user_id,
                    "created_at": task.created_at.isoformat() if task.created_at else None
                })

            return task_list
        except Exception as e:
            logger.error(f"Error retrieving tasks for user {self.user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve tasks"
            )

    def complete_task(self, task_id: int) -> Dict[str, Any]:
        """
        Mark a task as complete for the authenticated user.

        Args:
            task_id: ID of the task to complete

        Returns:
            Dictionary with updated task details
        """
        try:
            statement = select(Task).where(Task.id == task_id).where(Task.user_id == self.user_id)
            task = self.session.exec(statement).first()

            if not task:
                logger.warning(f"Task {task_id} not found for user: {self.user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found or does not belong to the authenticated user"
                )

            # Mark as complete
            task.completed = True

            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)

            logger.info(f"Task marked as complete: {task.id} for user: {self.user_id}")

            return {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "user_id": task.user_id,
                "created_at": task.created_at.isoformat() if task.created_at else None
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error completing task {task_id} for user {self.user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to complete task"
            )

    def update_task(self, task_id: int, title: Optional[str] = None,
                   description: Optional[str] = None, completed: Optional[bool] = None) -> Dict[str, Any]:
        """
        Update an existing task for the authenticated user.

        Args:
            task_id: ID of the task to update
            title: New title (optional)
            description: New description (optional)
            completed: New completion status (optional)

        Returns:
            Dictionary with updated task details
        """
        try:
            statement = select(Task).where(Task.id == task_id).where(Task.user_id == self.user_id)
            task = self.session.exec(statement).first()

            if not task:
                logger.warning(f"Task {task_id} not found for user: {self.user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found or does not belong to the authenticated user"
                )

            # Update only the fields that were provided
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if completed is not None:
                task.completed = completed

            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)

            logger.info(f"Task updated successfully: {task.id} for user: {self.user_id}")

            return {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "user_id": task.user_id,
                "created_at": task.created_at.isoformat() if task.created_at else None
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating task {task_id} for user {self.user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update task"
            )

    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task for the authenticated user.

        Args:
            task_id: ID of the task to delete

        Returns:
            Boolean indicating success
        """
        try:
            statement = select(Task).where(Task.id == task_id).where(Task.user_id == self.user_id)
            task = self.session.exec(statement).first()

            if not task:
                logger.warning(f"Task {task_id} not found for user: {self.user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Task not found or does not belong to the authenticated user"
                )

            self.session.delete(task)
            self.session.commit()

            logger.info(f"Task deleted successfully: {task_id} for user: {self.user_id}")

            return True
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting task {task_id} for user {self.user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete task"
            )

# Register MCP tools using decorators
@mcp.tool
def add_task(title: str, description: Optional[str] = None, user_id: str = None) -> Dict[str, Any]:
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
        return tools.add_task(title, description)
    finally:
        session.close()

@mcp.tool
def list_tasks(user_id: str) -> list:
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
        return tools.list_tasks()
    finally:
        session.close()

@mcp.tool
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
        return tools.complete_task(task_id)
    finally:
        session.close()

@mcp.tool
def update_task(task_id: int, title: Optional[str] = None,
               description: Optional[str] = None, completed: Optional[bool] = None,
               user_id: str = None) -> Dict[str, Any]:
    """
    Update an existing task for the user.

    Args:
        task_id: ID of the task to update
        title: New title (optional)
        description: New description (optional)
        completed: New completion status (optional)
        user_id: ID of the user requesting the action

    Returns:
        Dictionary with updated task details
    """
    session = next(get_session())
    try:
        tools = MCPTaskTools(session, user_id)
        return tools.update_task(task_id, title, description, completed)
    finally:
        session.close()

@mcp.tool
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
        return tools.delete_task(task_id)
    finally:
        session.close()

# Run the MCP server if this is the main module
if __name__ == "__main__":
    mcp.run()