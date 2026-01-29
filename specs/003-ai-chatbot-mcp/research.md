# Research Summary: AI Chatbot & MCP Integration

## Architecture Overview

### Current System Components
- **Frontend**: Next.js 16+ application with React 18, TypeScript, Tailwind CSS
- **Backend**: Python 3.13 + FastAPI + SQLModel with Neon PostgreSQL
- **Authentication**: Better Auth with JWT tokens
- **Existing Models**: User and Task models with proper user isolation
- **Existing Routes**: Auth and Tasks API endpoints with JWT validation

### New Architecture Components
- **ChatKit UI**: Frontend chat interface component
- **FastAPI Backend**: New chat endpoints with MCP tool integration
- **OpenAI Agents SDK**: Agent framework using OpenRouter API
- **MCP Server**: Machine Control Protocol server for tool integration
- **Stateless Chat**: Conversation history stored in database with external storage

## Database Migration Strategy

### Current Alembic Setup
- Need to initialize Alembic for the existing SQLModel setup
- Target metadata should be set to `SQLModel.metadata` to detect models properly
- Existing tables (users, tasks) should remain unaffected
- New tables (conversations, messages) will be added via Alembic migrations

### Migration Steps
1. Initialize Alembic in the backend directory
2. Configure `target_metadata = SQLModel.metadata` in alembic/env.py
3. Generate migration for new conversation and message models
4. Apply migration without affecting existing tables

## Key Decisions Requiring Documentation

### 1. Alembic with SQLModel Integration
- **Decision**: Use Alembic with `target_metadata = SQLModel.metadata` to properly detect model changes
- **Rationale**: This ensures Alembic can detect both existing and new models without duplication
- **Alternatives considered**: Manual SQL scripts vs Alembic automation
- **Chosen approach**: Alembic automation for maintainability

### 2. Stateless Chat Architecture
- **Decision**: Implement stateless chat endpoint with conversation history stored in database
- **Rationale**: Maintains scalability and allows conversation persistence across sessions
- **Alternatives considered**: In-memory storage vs database storage vs external service
- **Chosen approach**: Database storage for consistency with existing data model

### 3. JWT Authentication Enforcement
- **Decision**: Validate JWT tokens on every chat endpoint to enforce user isolation
- **Rationale**: Maintains security standards consistent with existing API
- **Alternatives considered**: Session-based vs token-based authentication
- **Chosen approach**: JWT tokens for consistency with existing auth system

## MCP Tool Integration

### Required Tools
- `add_task`: Create new tasks via chat
- `list_tasks`: Retrieve user's tasks via chat
- `complete_task`: Mark tasks as complete via chat
- `update_task`: Modify existing tasks via chat
- `delete_task`: Remove tasks via chat

### Implementation Approach
- Create MCP tools that wrap existing task operations
- Each tool validates JWT and enforces user isolation
- Tools return structured responses for agent consumption

## OpenRouter Configuration

### Setup Requirements
- Store OPENROUTER_API_KEY in .env file
- Configure agent to use OpenRouter's API endpoints
- Handle rate limiting and error responses appropriately
- Implement fallback mechanisms for API failures

## Quality Validation Strategy

### Testing Areas
1. MCP tool behaviors - Verify each tool operates correctly with proper authentication
2. Chat endpoint responses - Test various conversation flows and edge cases
3. Conversation history persistence - Validate storage and retrieval of chat history
4. Error handling - Test graceful degradation when services are unavailable

### Test Types
- Unit tests for individual MCP tools
- Integration tests for chat endpoint with authentication
- End-to-end tests for complete chat-to-task-operation flows
- Error scenario tests for API failures and invalid inputs