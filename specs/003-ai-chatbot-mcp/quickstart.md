# Quickstart Guide: AI Chatbot & MCP Integration

## Prerequisites

- Python 3.13+ with uv installed
- Node.js 18+ with npm/yarn
- Access to OpenRouter API (get API key from https://openrouter.ai/keys)
- Existing project dependencies installed

## Setup Steps

### 1. Backend Setup

#### Install New Dependencies with uv
```bash
cd backend
uv add openai python-dotenv httpx
```

#### Environment Variables
Add to your `.env` file:
```bash
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

#### Initialize Alembic (if not already set up)
```bash
cd backend
uv add alembic
alembic init alembic
```

#### Update Alembic Configuration
Edit `backend/alembic/env.py`:
```python
from sqlalchemy import engine_from_config, pool
from models import SQLModel  # Import your SQLModel
from alembic import context

# Set target metadata to SQLModel's metadata
target_metadata = SQLModel.metadata

def run_migrations_online():
    # ... existing code ...
```

#### Generate and Apply Migrations
```bash
cd backend
# Generate migration for new models
alembic revision --autogenerate -m "Add conversation and message tables"

# Apply the migration
alembic upgrade head
```

### 2. Add New Models

Create `backend/models/chat_models.py`:
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

class ConversationBase(SQLModel):
    user_id: str = Field(index=True)  # Links to User.id
    title: Optional[str] = Field(default=None, max_length=200)

class Conversation(ConversationBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class MessageBase(SQLModel):
    conversation_id: UUID = Field(index=True)  # Links to Conversation.id
    role: str = Field(regex="^(user|assistant)$")  # Either "user" or "assistant"
    content: str = Field(min_length=1)

class Message(MessageBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata_: Optional[dict] = Field(default=None)  # Use metadata_ to avoid conflict with SQLModel
```

### 3. Frontend Setup

#### Install Chat Components Dependencies
```bash
cd frontend
npm install react-markdown remark-gfm
```

#### Environment Variables
Add to your `.env.local` file:
```bash
NEXT_PUBLIC_OPENROUTER_API_KEY=your_openrouter_api_key_here
```

## Running the Application

### Start Backend Services
```bash
cd backend
# Make sure database is migrated
alembic upgrade head

# Run the backend
uv run uvicorn main:app --reload --port 8000
```

### Start Frontend
```bash
cd frontend
npm run dev
```

## Testing the Chat Feature

1. Navigate to your dashboard page (should now include chat interface)
2. Authenticate with your existing account
3. Open the chat interface (likely in a sidebar or dedicated chat page)
4. Send a message to test the conversation functionality
5. Verify that conversation history is persisted in the database

## API Endpoints

### Chat Endpoints
- `POST /api/v1/chat` - Send a message and get AI response
- `GET /api/v1/chat/conversations` - Get list of user's conversations
- `GET /api/v1/chat/conversations/{conversation_id}` - Get specific conversation
- `DELETE /api/v1/chat/conversations/{conversation_id}` - Delete conversation

### Authentication
All chat endpoints require valid JWT in `Authorization: Bearer <token>` header.

## MCP Tool Integration

The system includes the following MCP tools accessible to the AI agent:
- `add_task`: Create new tasks
- `list_tasks`: View user's tasks
- `complete_task`: Mark tasks as complete
- `update_task`: Modify existing tasks
- `delete_task`: Remove tasks

These tools are automatically registered with the OpenRouter agent and enforce JWT-based user validation.