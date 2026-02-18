# Todo Backend API

A secure FastAPI backend for managing Todo tasks with Neon PostgreSQL database integration, JWT authentication, and AI-powered chatbot capabilities using OpenRouter and MCP tools.

## Features

- **JWT Authentication**: All endpoints require valid JWT tokens
- **User Isolation**: Users can only access their own tasks and conversations
- **Full CRUD Operations**: Create, Read, Update, Delete tasks
- **Task Management**: Title, description, status, priority, due dates, timestamps
- **AI Chatbot Integration**: Natural language task management via OpenRouter API
- **MCP Tools**: Machine Context Protocol tools for agent-driven task operations
- **Conversation History**: Persistent chat history stored in PostgreSQL
- **Secure API**: Proper validation and error handling across all endpoints

## API Endpoints

### Task Management (`/api/v1/tasks`)

- `POST /tasks` - Create a new task
- `GET /tasks` - Get all tasks for authenticated user
- `GET /tasks/{id}` - Get specific task
- `PUT /tasks/{id}` - Update task details
- `PATCH /tasks/{id}/complete` - Toggle completion status
- `DELETE /tasks/{id}` - Delete task

### AI Chat (`/api/v1/chat`)

- `POST /chat` - Send message to AI chatbot and get response
- `GET /chat/conversations` - Get all conversations for authenticated user
- `GET /chat/conversations/{id}` - Get specific conversation with message history
- `DELETE /chat/conversations/{id}` - Delete a conversation

### MCP Tools

The backend implements MCP (Model Context Protocol) tools that the AI agent uses to perform task operations:

- `add_task` - Create new tasks via natural language
- `list_tasks` - Retrieve user's tasks
- `complete_task` - Mark tasks as complete
- `update_task` - Modify task properties (title, description, status, priority, due date)
- `delete_task` - Remove tasks

All MCP tools enforce JWT authentication and user isolation.

## Requirements

- Python 3.13+
- uv package manager
- Neon PostgreSQL database
- OpenRouter API key (for AI chatbot features)

## Setup

1. **Create virtual environment and install dependencies:**
```bash
cd backend
uv venv --python 3.13
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv add fastapi sqlmodel psycopg2-binary python-jose uvicorn python-multipart pydantic pydantic-settings httpx pytest openai alembic
```

2. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

Required environment variables:
```env
# Database
DATABASE_URL=postgresql://user:password@host/database

# Authentication
BETTER_AUTH_SECRET=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Chatbot (OpenRouter)
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=qwen/qwen3-next-80b-a3b-instruct:free
APP_URL=http://localhost:3000
APP_TITLE=Todo App AI Chatbot
```

3. **Run database migrations:**
```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Run migrations to create tables
alembic upgrade head
```

4. **Run the application:**
```bash
uv run uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

## Database Schema

### Tables

- **users**: User accounts with authentication details
- **tasks**: Todo tasks with title, description, status, priority, due dates
- **conversations**: Chat conversation sessions
- **messages**: Individual chat messages (user and assistant)

All tables enforce user isolation via `user_id` foreign keys.

## Testing

Run the test suite:
```bash
uv run python -m pytest tests/ -v
```

Test coverage includes:
- Task CRUD operations with user isolation
- JWT authentication and authorization
- MCP tool functionality and agent decision mappings
- Chat service and conversation management
- Error handling for API and tool failures

## Architecture

### Project Structure

```
backend/
├── models/
│   ├── user.py              # User model
│   ├── task.py              # Task model
│   └── chat_models.py       # Conversation and Message models
├── routes/
│   ├── auth.py              # Authentication endpoints
│   ├── tasks.py             # Task management endpoints
│   └── chat.py              # AI chat endpoints
├── services/
│   ├── auth.py              # Authentication service
│   ├── tasks.py             # Task service
│   └── chat_service.py      # Chat service with OpenRouter integration
├── tools/
│   └── mcp_tools.py         # MCP tools for AI agent
├── alembic/
│   └── versions/            # Database migrations
├── config.py                # Application configuration
├── db.py                    # Database connection
├── auth.py                  # JWT authentication utilities
└── main.py                  # FastAPI application entry point
```

### AI Chatbot Flow

1. User sends message via `/api/v1/chat` endpoint
2. JWT token is validated and user_id extracted
3. Chat service loads conversation history from database
4. Message is sent to OpenRouter API with MCP tool definitions
5. AI agent decides which MCP tools to call (if any)
6. MCP tools execute with user_id validation
7. Tool results are sent back to AI agent
8. Final response is generated and saved to database
9. Response is returned to user

### MCP Tools Integration

MCP tools are implemented using the FastMCP framework and provide the AI agent with capabilities to:
- Perform task operations on behalf of the authenticated user
- Maintain strict user isolation (all operations validate user_id)
- Handle errors gracefully with clear user feedback
- Parse natural language requests into structured tool calls

## Security

- All endpoints require `Authorization: Bearer <token>` header
- User ID from JWT is validated against task/conversation ownership
- MCP tools enforce the same authentication as REST endpoints
- Input validation for all fields (title max 200 chars, valid status/priority values)
- Proper error responses with appropriate HTTP status codes
- OpenRouter API key stored securely in environment variables
- Conversation history isolated per user with database-level constraints