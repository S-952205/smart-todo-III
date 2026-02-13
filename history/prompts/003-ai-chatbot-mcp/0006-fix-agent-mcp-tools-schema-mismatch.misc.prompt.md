---
id: 0006
title: fix agent mcp tools schema mismatch
stage: misc
date: 2026-02-13
surface: agent
model: claude-haiku-4-5-20251001
feature: 003-ai-chatbot-mcp
branch: main
user: Syed Sufyan
command: /sp.implement
labels: ["agent", "mcp-tools", "schema-fix", "testing", "database"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/tools/mcp_tools.py
  - backend/task_agents/tools.py
  - backend/task_agents/agent.py
  - backend/tests/test_agent_tools.py
  - AGENT_MCP_TOOLS_FIX.md
tests:
  - test_add_task_with_all_fields
  - test_add_task_with_defaults
  - test_update_task_status
  - test_update_task_priority_and_due_date
  - test_update_task_multiple_fields
  - test_complete_task_sets_status_to_done
  - test_list_tasks_returns_all_fields
  - test_user_isolation
---

## Prompt

i want u to check if my agent accuratly calling mcp tools since when i m interacting with agent it is misbehaving.. agent adds task when i told him to update it doesn't update... plus i want my agent shold be able tw also imclude due date and priority when adding task or updating since these already exist in neon table..
first check and verify agent using mcp tools the way it should use/

## Response snapshot

Identified and fixed critical schema mismatch between MCP tools and database:

**Root Cause**: MCP tools used `completed` (boolean) field, but database Task model uses `status` ('todo', 'in-progress', 'done'). This caused update operations to fail, leading agent to create new tasks instead of updating existing ones.

**Changes Made**:
1. Updated MCPTaskTools class methods to use `status`, `priority`, `due_date` fields
2. Updated OpenAI Agents SDK wrapper functions with same fields
3. Enhanced agent instructions to clarify tool capabilities
4. Fixed variable shadowing issue (status parameter vs fastapi.status module)
5. Created comprehensive test suite (8 tests, all passing)

**Files Modified**:
- `backend/tools/mcp_tools.py`: Updated all CRUD methods to match database schema
- `backend/task_agents/tools.py`: Updated agent tool wrappers
- `backend/task_agents/agent.py`: Enhanced agent instructions

**Files Created**:
- `backend/tests/test_agent_tools.py`: Comprehensive test suite
- `AGENT_MCP_TOOLS_FIX.md`: Detailed documentation

**Test Results**: 8/8 tests passing, verifying:
- Task creation with all fields (status, priority, due_date)
- Task updates (individual and multiple fields)
- Status changes and completion
- User isolation and security
- Field presence in responses

## Outcome

- ✅ Impact: Fixed critical bug preventing agent from updating tasks; agent now supports priority and due_date fields
- 🧪 Tests: Created 8 comprehensive tests, all passing (100% success rate)
- 📁 Files: Modified 3 core files, created 2 new files (test suite + documentation)
- 🔁 Next prompts: Test agent in production environment; verify UI displays priority and due_date correctly
- 🧠 Reflection: Schema mismatches between layers are critical bugs that manifest as behavioral issues; comprehensive testing caught edge cases like variable shadowing

## Evaluation notes (flywheel)

- Failure modes observed: Variable shadowing (status parameter vs fastapi.status module) caught by test suite
- Graders run and results (PASS/FAIL): pytest 8/8 PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Monitor agent behavior in production; add integration tests with actual OpenRouter API calls
