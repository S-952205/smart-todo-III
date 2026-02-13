from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional, Literal
from pydantic import field_validator
import re


class UserBase(SQLModel):
    """Base model for User with shared attributes."""
    email: str = Field(unique=True, nullable=False)
    name: str = Field(max_length=100)
    password: str = Field(exclude=True)  # Exclude from responses


class User(UserBase, table=True):
    """User model representing the database table."""
    id: str = Field(primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserCreate(SQLModel):
    """Model for creating a new user."""
    email: str = Field(regex=r'^[^@]+@[^@]+\.[^@]+$')  # Basic email validation
    name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8, max_length=64)  # Minimum 8, maximum 64 characters to avoid bcrypt limits


class UserResponse(SQLModel):
    """Model for returning user data in API responses."""
    id: str
    email: str
    name: str
    created_at: datetime
    updated_at: datetime


class TokenResponse(SQLModel):
    """Model for JWT token response."""
    access_token: str
    token_type: str
    user: UserResponse


class TaskBase(SQLModel):
    """Base model for Task with shared attributes."""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: Literal['todo', 'in-progress', 'done'] = Field(default='todo')
    priority: Optional[Literal['low', 'medium', 'high']] = Field(default='medium')
    due_date: Optional[datetime] = Field(default=None)


class Task(TaskBase, table=True):
    """Task model representing the database table."""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # Indexed for performance
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskCreate(TaskBase):
    """Model for creating a new task."""
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: Optional[Literal['todo', 'in-progress', 'done']] = Field(default='todo')
    priority: Optional[Literal['low', 'medium', 'high']] = Field(default='medium')
    due_date: Optional[datetime] = Field(default=None)


class TaskUpdate(SQLModel):
    """Model for updating an existing task."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: Optional[Literal['todo', 'in-progress', 'done']] = Field(default=None)
    priority: Optional[Literal['low', 'medium', 'high']] = Field(default=None)
    due_date: Optional[datetime] = Field(default=None)


class TaskResponse(TaskBase):
    """Model for returning task data in API responses."""
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime


class ErrorResponse(SQLModel):
    """Model for error responses."""
    detail: str