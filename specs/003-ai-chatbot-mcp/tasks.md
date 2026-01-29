# Tasks: AI Chatbot & MCP Integration

## Phase 1: Setup
Initialize project structure and dependencies for AI Chatbot feature.

- [ ] T001 Create backend models for conversation and message in backend/models/chat_models.py
- [ ] T002 Set up Alembic for database migrations in backend/alembic/
- [ ] T003 [P] Add OpenRouter dependencies to backend with uv add openai python-dotenv httpx
- [ ] T004 [P] Update backend/pyproject.toml with new dependencies

## Phase 2: Foundational
Core infrastructure needed for all user stories.

- [ ] T010 Create MCP tools for task operations in backend/tools/mcp_tools.py
- [ ] T011 Implement chat service with MCP integration in backend/services/chat_service.py
- [ ] T012 Create chat API endpoints in backend/routes/chat.py
- [ ] T013 [P] Update main.py to include chat routes

## Phase 3: [US1] AI-Powered Task Management
Enable users to manage tasks through natural language chat interactions.

- [ ] T020 [US1] Create OpenRouter agent integration in backend/agents/openrouter_agent.py
- [ ] T021 [US1] Connect agent to MCP tools for task operations
- [ ] T022 [US1] Test natural language task creation with add_task MCP tool
- [ ] T023 [US1] Test natural language task completion with complete_task MCP tool

**Independent Test**: Send natural language requests to chat endpoint and verify MCP tools are called with proper authentication.

## Phase 4: [US2] MCP-Integrated Chat Operations
Ensure all AI actions are properly authenticated and maintain user isolation.

- [ ] T030 [US2] Implement JWT validation in chat endpoints
- [ ] T031 [US2] Add user isolation checks for conversation access
- [ ] T032 [US2] Verify all MCP operations enforce user ownership
- [ ] T033 [US2] Test cross-user data isolation

**Independent Test**: Verify all AI-driven operations pass through MCP tools with proper authentication checks.

## Phase 5: [US3] AI Chat Interface with JWT Authentication
Integrate frontend ChatKit with secure JWT authentication.

- [ ] T040 [US3] Create chat API service in frontend/src/app/api/chat/chatService.ts
- [ ] T041 [US3] Build ChatInterface component in frontend/src/app/components/ChatKit/ChatInterface.tsx
- [ ] T042 [US3] Add Message display component in frontend/src/app/components/ChatKit/Message.tsx
- [ ] T043 [US3] Integrate chat with dashboard in frontend/src/app/components/dashboard/DashboardWithChat.tsx

**Independent Test**: Verify JWT token flow from frontend to backend during chat interactions.

## Phase 6: Polish & Cross-Cutting Concerns
Final touches and quality improvements.

- [ ] T050 Add error handling for agent and tool failures
- [ ] T051 Implement fallback mechanisms for OpenRouter API issues
- [ ] T052 Add TypeScript types for chat in frontend/src/types/chat.ts
- [ ] T053 Update documentation and environment examples

## Dependencies

- User Story 1 (T020-T023) requires foundational tasks (T010-T013) to be completed
- User Story 2 (T030-T033) requires foundational tasks (T010-T013) to be completed
- User Story 3 (T040-T043) requires foundational tasks (T010-T013) to be completed

## Parallel Execution Opportunities

- T003 and T004 can run in parallel with other setup tasks
- US1, US2, and US3 phases can be developed in parallel after foundational phase

## Implementation Strategy

**MVP Scope**: Complete Phase 1, Phase 2, and Phase 3 (User Story 1) for basic AI-powered task management functionality.