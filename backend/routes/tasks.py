from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlmodel import Session
from models import TaskCreate, TaskUpdate, TaskResponse, ErrorResponse
from db import get_session
from auth import get_current_user_id
from sqlmodel import select
import logging


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter()


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskResponse:
    """
    Create a new task for the authenticated user.
    """
    from models import Task

    try:
        # Create task with the authenticated user's ID
        task = Task(
            title=task_data.title,
            description=task_data.description,
            status=task_data.status or 'todo',
            priority=task_data.priority or 'medium',
            due_date=task_data.due_date,
            user_id=user_id
        )

        session.add(task)
        session.commit()
        session.refresh(task)

        logger.info(f"Task created successfully: {task.id} for user: {user_id}")

        # Convert to response model
        if hasattr(TaskResponse, 'from_orm'):
            return TaskResponse.from_orm(task)
        else:
            return TaskResponse(**task.dict())
    except Exception as e:
        logger.error(f"Error creating task for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create task"
        )


@router.get("/tasks", response_model=List[TaskResponse])
def get_tasks(
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> List[TaskResponse]:
    """
    Retrieve all tasks for the authenticated user.
    """
    from models import Task

    try:
        statement = select(Task).where(Task.user_id == user_id)
        tasks = session.exec(statement).all()

        logger.info(f"Retrieved {len(tasks)} tasks for user: {user_id}")

        # Convert to response model
        if hasattr(TaskResponse, 'from_orm'):
            return [TaskResponse.from_orm(task) for task in tasks]
        else:
            return [TaskResponse(**task.dict()) for task in tasks]
    except Exception as e:
        logger.error(f"Error retrieving tasks for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve tasks"
        )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskResponse:
    """
    Retrieve a specific task by ID for the authenticated user.
    """
    from models import Task

    try:
        statement = select(Task).where(Task.id == task_id).where(Task.user_id == user_id)
        task = session.exec(statement).first()

        if not task:
            logger.warning(f"Task {task_id} not found for user: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or does not belong to the authenticated user"
            )

        logger.info(f"Task retrieved successfully: {task.id} for user: {user_id}")

        return TaskResponse.from_orm(task) if hasattr(TaskResponse, 'from_orm') else TaskResponse(**task.dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving task {task_id} for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve task"
        )


@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskResponse:
    """
    Update an existing task for the authenticated user.
    """
    from models import Task
    from datetime import datetime

    try:
        statement = select(Task).where(Task.id == task_id).where(Task.user_id == user_id)
        task = session.exec(statement).first()

        if not task:
            logger.warning(f"Task {task_id} not found for user: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or does not belong to the authenticated user"
            )

        # Update only the fields that were provided
        for field, value in task_update.dict(exclude_unset=True).items():
            setattr(task, field, value)

        # Always update the updated_at timestamp
        task.updated_at = datetime.now()

        session.add(task)
        session.commit()
        session.refresh(task)

        logger.info(f"Task updated successfully: {task.id} for user: {user_id}")

        return TaskResponse.from_orm(task) if hasattr(TaskResponse, 'from_orm') else TaskResponse(**task.dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id} for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update task"
        )


@router.patch("/tasks/{task_id}/complete", response_model=TaskResponse)
def toggle_task_completion(
    task_id: int,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskResponse:
    """
    Toggle the completion status of a task for the authenticated user.
    Cycles through: todo -> done -> todo
    """
    from models import Task
    from datetime import datetime

    try:
        statement = select(Task).where(Task.id == task_id).where(Task.user_id == user_id)
        task = session.exec(statement).first()

        if not task:
            logger.warning(f"Task {task_id} not found for user: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or does not belong to the authenticated user"
            )

        # Toggle between todo and done
        task.status = 'done' if task.status != 'done' else 'todo'
        task.updated_at = datetime.now()

        session.add(task)
        session.commit()
        session.refresh(task)

        logger.info(f"Task status toggled for task: {task.id} for user: {user_id}")

        return TaskResponse.from_orm(task) if hasattr(TaskResponse, 'from_orm') else TaskResponse(**task.dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling completion for task {task_id} for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle task completion"
        )


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """
    Delete a task for the authenticated user.
    """
    from models import Task

    try:
        statement = select(Task).where(Task.id == task_id).where(Task.user_id == user_id)
        task = session.exec(statement).first()

        if not task:
            logger.warning(f"Task {task_id} not found for user: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or does not belong to the authenticated user"
            )

        session.delete(task)
        session.commit()

        logger.info(f"Task deleted successfully: {task_id} for user: {user_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id} for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete task"
        )