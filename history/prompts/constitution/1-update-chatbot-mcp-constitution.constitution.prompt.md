---
id: 1
title: Update Chatbot MCP Constitution
stage: constitution
date: 2026-01-30
surface: agent
model: claude-haiku-4-5-20251001
feature: none
branch: main
user: user
command: sp.constitution update existing constitution.md in .specify/memory/
labels: [constitution,ai-chatbot,mcp,security]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

update existing constitution.md in .specify/memory/
Update the existing Todo Web App Constitution to include AI Chatbot & MCP principles.

Project: AI-Native Todo Full-Stack Chatbot

Additions and changes:
- Include agentic AI workflow (OpenRouter + OpenAI Agents SDK + MCP) as mandatory.
- Require stateless architecture for chat endpoint and conversation history storage.
- Enforce every chatbot action to be backed by MCP tools (add_task, list_tasks, complete_task, update_task, delete_task).
- LLM integration must use OpenRouter with key stored in .env (OPENROUTER_API_KEY).
- Test coverage required for all MCP tool behaviors and agent decision mappings.
- ChatKit frontend must integrate with FastAPI chat endpoint using JWT from Better Auth.
- Error handling standards for agent & tool failures with clear user confirmations.
- Validate that all API requests are authenticated and user ownership enforced via JWT.
- Maintain clear separation of frontend and backend in monorepo structure.
- Include versioning for Constitution as project evolves.

Success criteria:
-

## Response snapshot

The constitution.md file in .specify/memory/ has been successfully updated to include AI Chatbot & MCP principles. The key changes made include:

1. Updated the version from 1.0.0 to 1.1.0
2. Enhanced the Agentic Workflow principle to include mandatory agentic AI workflow (OpenRouter + OpenAI Agents SDK + MCP) and requirement that every chatbot action must be backed by MCP tools
3. Added a new "AI Chatbot Architecture" section with:
   - Statelessness Requirement for chat endpoints
   - MCP Integration Standards requiring all chatbot actions to use MCP tools
   - Chat Interface Requirements for ChatKit integration with JWT
4. Added a new "LLM Integration Requirements" subsection under Technology Stack
5. Enhanced Testing Standards to require coverage for MCP tool behaviors and agent decision mappings
6. Updated Secret Management to include OPENROUTER_API_KEY
7. Added Data Protection requirements for conversation histories
8. Added a new "Error Handling Standards" section with requirements for agent & tool failures
9. Updated the last amended date to 2026-01-30

## Outcome

- ✅ Impact: Updated constitution to include AI Chatbot & MCP principles
- 🧪 Tests: none
- 📁 Files: 1 file updated (.specify/memory/constitution.md)
- 🔁 Next prompts: None required
- 🧠 Reflection: Constitution now properly reflects the requirements for AI chatbot integration with MCP tools

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A