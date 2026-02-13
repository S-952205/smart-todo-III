"""
MCP Tools for task operations using FastMCP
These tools will be used by the AI agent to perform task operations
"""
from typing import Dict, Any, Optional
from sqlmodel import Session, select
from models import Task
from db import get_session
from fastapi import HTTPException
from fastapi import status as http_status
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

    def add_task(self, title: str, description: Optional[str] = None,
                 status: Optional[str] = 'todo', priority: Optional[str] = 'medium',
                 due_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Create a new task for the authenticated user.

        Args:
            title: Title of the task
            description: Optional description of the task
            status: Task status ('todo', 'in-progress', 'done'), defaults to 'todo'
            priority: Task priority ('low', 'medium', 'high'), defaults to 'medium'
            due_date: Optional due date for the task

        Returns:
            Dictionary with task details
        """
        try:
            # Create task with the authenticated user's ID
            task = Task(
                title=title,
                description=description,
                status=status or 'todo',
                priority=priority or 'medium',
                due_date=due_date,
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
                "status": task.status,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "user_id": task.user_id,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None
            }
        except Exception as e:
            logger.error(f"Error creating task for user {self.user_id}: {str(e)}")
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
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
                    "status": task.status,
                    "priority": task.priority,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "user_id": task.user_id,
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "updated_at": task.updated_at.isoformat() if task.updated_at else None
                })

            return task_list
        except Exception as e:
            logger.error(f"Error retrieving tasks for user {self.user_id}: {str(e)}")
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve tasks"
            )

    def complete_task(self, task_id: int) -> Dict[str, Any]:
        """
        Mark a task as complete (status='done') for the authenticated user.

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
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    detail="Task not found or does not belong to the authenticated user"
                )

            # Mark as complete by setting status to 'done'
            task.status = 'done'
            task.updated_at = datetime.now()

            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)

            logger.info(f"Task marked as complete: {task.id} for user: {self.user_id}")

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
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error completing task {task_id} for user {self.user_id}: {str(e)}")
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to complete task"
            )

    def update_task(self, task_id: int, title: Optional[str] = None,
                   description: Optional[str] = None, status: Optional[str] = None,
                   priority: Optional[str] = None, due_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Update an existing task for the authenticated user.

        Args:
            task_id: ID of the task to update
            title: New title (optional)
            description: New description (optional)
            status: New status ('todo', 'in-progress', 'done') (optional)
            priority: New priority ('low', 'medium', 'high') (optional)
            due_date: New due date (optional)

        Returns:
            Dictionary with updated task details
        """
        try:
            statement = select(Task).where(Task.id == task_id).where(Task.user_id == self.user_id)
            task = self.session.exec(statement).first()

            if not task:
                logger.warning(f"Task {task_id} not found for user: {self.user_id}")
                raise HTTPException(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    detail="Task not found or does not belong to the authenticated user"
                )

            # Update only the fields that were provided
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if status is not None:
                task.status = status
            if priority is not None:
                task.priority = priority
            if due_date is not None:
                task.due_date = due_date

            # Always update the updated_at timestamp
            task.updated_at = datetime.now()

            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)

            logger.info(f"Task updated successfully: {task.id} for user: {self.user_id}")

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
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating task {task_id} for user {self.user_id}: {str(e)}")
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
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
                    status_code=http_status.HTTP_404_NOT_FOUND,
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
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete task"
            )

# Register MCP tools using decorators
@mcp.tool
def add_task(title: str, description: Optional[str] = None, status: Optional[str] = 'todo',
             priority: Optional[str] = 'medium', due_date: Optional[str] = None,
             user_id: str = None) -> Dict[str, Any]:
    """
    Add a new task for the user.

    Args:
        title: Title of the task to create
        description: Optional description of the task
        status: Task status ('todo', 'in-progress', 'done'), defaults to 'todo'
        priority: Task priority ('low', 'medium', 'high'), defaults to 'medium'
        due_date: Optional due date in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
        user_id: ID of the user creating the task

    Returns:
        Dictionary with created task details
    """
    session = next(get_session())
    try:
        # Parse due_date string to datetime if provided
        due_date_obj = None
        if due_date:
            try:
                due_date_obj = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except ValueError:
                logger.warning(f"Invalid due_date format: {due_date}")

        tools = MCPTaskTools(session, user_id)
        return tools.add_task(title, description, status, priority, due_date_obj)
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
               description: Optional[str] = None, status: Optional[str] = None,
               priority: Optional[str] = None, due_date: Optional[str] = None,
               user_id: str = None) -> Dict[str, Any]:
    """
    Update an existing task for the user.

    Args:
        task_id: ID of the task to update
        title: New title (optional)
        description: New description (optional)
        status: New status ('todo', 'in-progress', 'done') (optional)
        priority: New priority ('low', 'medium', 'high') (optional)
        due_date: New due date in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS) (optional)
        user_id: ID of the user requesting the action

    Returns:
        Dictionary with updated task details
    """
    session = next(get_session())
    try:
        # Parse due_date string to datetime if provided
        due_date_obj = None
        if due_date:
            try:
                due_date_obj = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except ValueError:
                logger.warning(f"Invalid due_date format: {due_date}")

        tools = MCPTaskTools(session, user_id)
        return tools.update_task(task_id, title, description, status, priority, due_date_obj)
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