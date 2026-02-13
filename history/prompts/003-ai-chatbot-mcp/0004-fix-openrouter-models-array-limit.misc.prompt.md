---
id: 0004
title: Fix OpenRouter models array limit
stage: misc
date: 2026-02-11
surface: agent
model: claude-haiku-4-5-20251001
feature: 003-ai-chatbot-mcp
branch: main
user: Syed Sufyan
command: /sp.implement
labels: ["bugfix", "openrouter", "api-limit", "configuration"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/services/chat_service.py
  - MODEL_CONFIGURATION_FIX.md
tests:
  - Direct API test with 3 models (Status 200)
---

## Prompt

now i m getting complete new errro: ERROR:services.chat_service:Error processing chat request for user 9b14cd2c-0a3a-441e-9f7d-aaae93f7345d: Error code: 400 - {'error': {'message': "'models' array must have 3 items or fewer.", 'code': 400}, 'user_id': 'user_39Uq7DGq0OLgoqMJ9f7k3IU17Jv'}

## Response snapshot

**Issue Identified**: OpenRouter API has a hard limit of 3 models maximum in the fallback array, but the previous fix added 4 models.

**Quick Fix Applied**:
- Reduced fallback models array from 4 to 3 items in both API call locations in `chat_service.py`
- Kept the most reliable models: `openrouter/free`, `upstage/solar-pro-3:free`, `nvidia/nemotron-3-nano-30b-a3b:free`
- Removed: `arcee-ai/trinity-large-preview:free`

**Testing**: Direct API test confirmed Status 200 with 3 models

**Documentation**: Updated MODEL_CONFIGURATION_FIX.md to include this OpenRouter limit

## Outcome

- ✅ Impact: Fixed 400 error, chatbot now works with proper fallback configuration
- 🧪 Tests: API test passed (Status 200, Valid: True)
- 📁 Files: Modified chat_service.py (2 locations), updated documentation
- 🔁 Next prompts: Restart backend server to apply changes
- 🧠 Reflection: OpenRouter API limits are strict - always check documentation for constraints

## Evaluation notes (flywheel)

- Failure modes observed: Exceeded OpenRouter's 3-model limit in fallback array
- Graders run and results (PASS/FAIL): API validation test PASS
- Prompt variant (if applicable): N/A - direct bugfix
- Next experiment (smallest change to try): Monitor if 3 models provide sufficient fallback coverage
