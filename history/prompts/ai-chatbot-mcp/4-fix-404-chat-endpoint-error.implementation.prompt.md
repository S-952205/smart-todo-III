---
id: 4
title: fix-404-chat-endpoint-error
stage: red
date_iso: 2026-02-07
surface: agent
model: haiku-4-5-20251001
feature: ai-chatbot-mcp
branch: main
user: Claude Haiku
command: /sp.implement
labels: ["bug-fix", "api-routing", "frontend-backend-integration"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - frontend/.env
  - frontend/src/app/api/chat/chatService.ts
tests_yaml:
  - backend/tests/test_chat.py
---

# Fix 404 Chat Endpoint Error

## Problem
When sending text to the AI agent on the UI, users were getting a "Failed to send message: Not Found" error. The backend logs showed:
- `POST /v1/chat HTTP/1.1" 404 Not Found`

## Root Cause
There was a mismatch between frontend API calls and backend API routes:
- Frontend was calling `/v1/chat` (after constructing URL with base URL)
- Backend had the route at `/api/v1/chat` (with router prefix `/api/v1`)

## Solution
1. Updated the `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_API_BASE_URL` environment variables in `.env` to include the `/api` part: `http://localhost:8000/api`
2. Updated the chat service constructor to use consistent environment variable pattern with other services
3. This ensures that when the chat service calls `${baseUrl}/v1/chat`, it resolves to `http://localhost:8000/api/v1/chat`, which matches the backend route

## Files Modified
- `frontend/.env`: Updated API URL environment variables to include `/api` suffix
- `frontend/src/app/api/chat/chatService.ts`: Updated constructor to use consistent env var pattern

## Validation
- All existing backend tests pass, including chat API tests
- The API routes now correctly match between frontend calls and backend expectations
- Both `/api/v1/chat` and related conversation endpoints should now work properly

## Outcome
The 404 error when sending messages to the AI chatbot should be resolved. The frontend will now correctly call the backend API endpoints with the proper path structure.

## Related Tasks
This addresses the core API integration issue that was preventing the AI chatbot from functioning properly in the UI.