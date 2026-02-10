from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
import json
from sqlalchemy import JSON
from pydantic import field_validator


class ConversationBase(SQLModel):
    user_id: str = Field(index=True)  # Links to User.id
    title: Optional[str] = Field(default=None, max_length=200)


class Conversation(ConversationBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class MessageBase(SQLModel):
    conversation_id: UUID = Field(index=True)  # Links to Conversation.id
    role: str = Field(min_length=1, max_length=20)  # Either "user" or "assistant"
    content: str = Field(min_length=1)

    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        if v not in ('user', 'assistant'):
            raise ValueError('Role must be either "user" or "assistant"')
        return v


class Message(MessageBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata_: Optional[dict] = Field(default=None, sa_type=JSON)  # Use metadata_ to avoid conflict with SQLModel