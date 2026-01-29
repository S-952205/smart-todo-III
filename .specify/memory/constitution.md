<!-- SYNC IMPACT REPORT
Version change: 1.0.0 -> 1.1.0
Modified principles: Agentic Workflow (expanded), Security Requirements (updated), Development Workflow (enhanced)
Added sections: AI Chatbot Architecture, MCP Integration Standards, LLM Integration Requirements, Error Handling Standards
Removed sections: N/A
Templates requiring updates: ✅ updated / ⚠ pending
- .specify/templates/plan-template.md: Needs alignment with new principles
- .specify/templates/spec-template.md: Needs alignment with new constraints
- .specify/templates/tasks-template.md: Needs alignment with new workflow
Follow-up TODOs: None
-->
# AI-Native Full-Stack Todo Web App Constitution

## Core Principles

### Agentic Workflow
100% implementation via Claude Code with mandatory agentic AI workflow (OpenRouter + OpenAI Agents SDK + MCP). No manual edits allowed. All development tasks must be executed through Claude Code agents and MCP-enabled tools. Every chatbot action must be backed by MCP tools (add_task, list_tasks, complete_task, update_task, delete_task).

### Spec-First Development
Mandatory reading of `/specs` before any code generation. All implementation work must be based on documented specifications with clear acceptance criteria.

### Strict User Isolation
Task ownership must be verified via JWT on every request. No data leakage between users is acceptable under any circumstances. All API requests must be authenticated and user ownership enforced via JWT.

### Zero Hardcoding Policy
No sensitive data in source code. All secrets must be stored in `.env` files and accessed through environment variables including OPENROUTER_API_KEY for LLM integration.

### No Manual Coding Rule
All logic must be derived from specifications. Direct manual coding without following specifications is prohibited.

### Clean Code Standards
Implementation must be clean, type-safe, and well-documented across the entire technology stack.

## AI Chatbot Architecture

### Statelessness Requirement
Stateless architecture for chat endpoint and conversation history storage. The chat endpoint must not maintain session state between requests, relying on external storage for conversation history.

### MCP Integration Standards
Every chatbot action must be backed by MCP tools (add_task, list_tasks, complete_task, update_task, delete_task). All agent behaviors must be mapped to specific MCP tool functions with clear validation and error handling.

### Chat Interface Requirements
ChatKit frontend must integrate with FastAPI chat endpoint using JWT from Better Auth. The frontend must properly handle authentication tokens and maintain secure communication with backend services.

## Technology Stack

### Frontend Requirements
Next.js 16+ (App Router, TypeScript, Tailwind) - All frontend components must leverage modern Next.js features with proper TypeScript typing and responsive Tailwind styling.

### Backend Requirements
Python FastAPI + SQLModel (ORM) - All backend services must use FastAPI for API creation with SQLModel for database ORM operations.

### Database Standards
Neon Serverless PostgreSQL - All data persistence must use Neon's serverless PostgreSQL with proper connection pooling and transaction management.

### Authentication Requirements
Better Auth + JWT Plugin - All authentication must be handled through Better Auth with JWT tokens for secure API communication.

### LLM Integration Requirements
LLM integration must use OpenRouter with key stored in .env (OPENROUTER_API_KEY). All AI-powered features must be properly authenticated and secured with appropriate rate limiting and access controls.

## Development Workflow

### Monorepo Layout
Separate `/frontend` and `/backend` directories - Maintain clear separation between frontend and backend codebases within the monorepo structure.

### API Convention
Use `Authorization: Bearer <token>` for all protected routes - All authenticated API endpoints must validate JWT tokens in the Authorization header.

### Validation Standards
Use Pydantic models for request/response validation in FastAPI - All API inputs and outputs must be properly validated using Pydantic models.

### Testing Standards
Test coverage required for all MCP tool behaviors and agent decision mappings. All AI chatbot functionality must include comprehensive unit and integration tests verifying proper tool usage and error handling.

## Security Requirements

### Secret Management
Use `.env` files for all secrets (DATABASE_URL, BETTER_AUTH_SECRET, OPENROUTER_API_KEY) - No hardcoded credentials or secrets in the source code.

### API Security
All protected routes must validate JWT tokens - Every API endpoint that accesses user data must verify JWT token authenticity and user ownership. All AI chatbot endpoints must enforce the same authentication standards.

### Data Protection
Implement proper user isolation - Ensure that users can only access their own data through proper database queries and API validation. Conversation histories must be properly isolated between users.

## Error Handling Standards

### Agent & Tool Failures
Implement standardized error handling for agent & tool failures with clear user confirmations. All MCP tool failures must be gracefully handled with appropriate user-facing messages.

### Fallback Mechanisms
Provide fallback mechanisms for when AI services are unavailable. The application must continue to function with core features even when LLM services are down.

## Governance

All implementations must adhere to these constitutional principles. Any deviation from these principles requires explicit approval and documentation of the exception. The constitution serves as the ultimate authority for development practices in this project.

Amendments to this constitution must be documented with clear justification and approved by project stakeholders before implementation. All team members must acknowledge and comply with these principles before contributing to the project.

All PRs and reviews must verify constitutional compliance. Code that violates these principles will not be accepted.

**Version**: 1.1.0 | **Ratified**: 2026-01-10 | **Last Amended**: 2026-01-30