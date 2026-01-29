# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

The AI Chatbot & MCP Integration feature implements a stateless chat interface that connects user conversations to backend task management through MCP (Machine Control Protocol) tools. The system uses OpenRouter API for AI capabilities, maintains JWT-based user isolation, and stores conversation history in the existing Neon PostgreSQL database. The architecture extends the current Next.js/FastAPI stack with new chat endpoints, MCP tool integration, and ChatKit UI components while preserving all existing functionality.

## Technical Context

**Language/Version**: Python 3.13, TypeScript 5.0+, JavaScript ES2022
**Primary Dependencies**: FastAPI, SQLModel, Alembic, OpenAI Agents SDK, OpenRouter API, Better Auth, Next.js 16+, React 18, ChatKit UI
**Storage**: Neon Serverless PostgreSQL with Alembic for migrations
**Testing**: pytest for backend, Jest/React Testing Library for frontend
**Target Platform**: Web application (Linux server + browser)
**Project Type**: Web (monorepo with frontend and backend)
**Performance Goals**: <5s p95 response time for AI chat interactions, 1000 concurrent users
**Constraints**: <200ms p95 for non-AI API calls, stateless chat architecture, JWT authentication enforcement
**Scale/Scope**: 10k users, persistent conversation history, MCP tool integration

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

1. **Agentic Workflow Compliance**: All development tasks must be executed through Claude Code agents and MCP-enabled tools. Every chatbot action must be backed by MCP tools (add_task, list_tasks, complete_task, update_task, delete_task). ✓ IMPLEMENTED: MCP tools will be created for all task operations and integrated with OpenRouter agent.

2. **Spec-First Development**: Mandatory reading of `/specs` before any code generation. All implementation work must be based on documented specifications with clear acceptance criteria. ✓ IMPLEMENTED: Following the spec created in the previous step.

3. **Strict User Isolation**: Task ownership must be verified via JWT on every request. All API requests must be authenticated and user ownership enforced via JWT. ✓ IMPLEMENTED: All chat endpoints will validate JWT and enforce user isolation for conversations and tasks.

4. **Zero Hardcoding Policy**: All secrets must be stored in `.env` files including OPENROUTER_API_KEY for LLM integration. ✓ IMPLEMENTED: OpenRouter API key will be stored in environment variables.

5. **Clean Code Standards**: Implementation must be clean, type-safe, and well-documented across the entire technology stack. ✓ IMPLEMENTED: Following existing code patterns and standards.

6. **Statelessness Requirement**: Chat endpoint must not maintain session state between requests, relying on external storage for conversation history. ✓ IMPLEMENTED: Conversation history stored in database, not in server memory.

7. **MCP Integration Standards**: All agent behaviors must be mapped to specific MCP tool functions with clear validation and error handling. ✓ IMPLEMENTED: MCP tools for task operations will validate JWT and enforce user isolation.

8. **LLM Integration Requirements**: Must use OpenRouter with key stored in .env (OPENROUTER_API_KEY). ✓ IMPLEMENTED: Configured to use OpenRouter API with environment-based key.

9. **Testing Standards**: Test coverage required for all MCP tool behaviors and agent decision mappings. ✓ IMPLEMENTED: Test suite will include tests for MCP tool functionality.

10. **Data Protection**: Conversation histories must be properly isolated between users. ✓ IMPLEMENTED: Conversation access controlled by user_id with JWT validation.

11. **Error Handling Standards**: Implement standardized error handling for agent & tool failures with clear user confirmations. ✓ IMPLEMENTED: Will include proper error handling for OpenRouter API failures and tool execution errors.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── task.py
│   └── chat_models.py               # New: Conversation and Message entities
├── services/
│   ├── __init__.py
│   ├── auth.py
│   ├── tasks.py
│   └── chat_service.py              # New: Chat service with MCP integration
├── routes/
│   ├── __init__.py
│   ├── auth.py
│   ├── tasks.py
│   └── chat.py                      # New: Chat API endpoints
├── tools/
│   ├── __init__.py
│   └── mcp_tools.py                 # New: MCP tools for agent integration
├── agents/
│   └── openrouter_agent.py          # New: OpenRouter agent integration
├── alembic/
│   ├── versions/
│   │   └── 001_add_conversation_message_tables.py  # New: Migration for new tables
│   ├── env.py
│   ├── script.py.mako
│   └── alembic.ini
├── config.py
├── main.py
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md

frontend/
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   └── chat/
│   │   │       └── chatService.ts   # New: Chat API service
│   │   ├── components/
│   │   │   ├── ChatKit/
│   │   │   │   ├── ChatInterface.tsx  # New: Main chat interface
│   │   │   │   ├── Message.tsx        # New: Message display component
│   │   │   │   └── MessageInput.tsx   # New: Message input component
│   │   │   └── dashboard/
│   │   │       └── DashboardWithChat.tsx  # Updated: Dashboard with integrated chat
│   │   └── dashboard/
│   │       └── page.tsx
│   ├── lib/
│   │   ├── auth/
│   │   └── utils/
│   └── types/
│       └── chat.ts                   # New: Chat-related TypeScript definitions
├── package.json
├── tsconfig.json
├── .env.example
└── README.md
```

**Structure Decision**: Web application structure chosen as the existing project is already a web application with separate frontend and backend. The new AI Chatbot feature will extend the existing architecture by adding conversation/message models to the backend, chat API endpoints, MCP tools integration, and ChatKit UI components to the frontend. Alembic will be used for database migrations to add the new conversation and message tables without affecting existing tables. This approach preserves all existing functionality while cleanly extending the system.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
