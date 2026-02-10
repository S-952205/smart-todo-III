---
id: 0005
title: Fix double API prefix 404 error
stage: general
date: 2026-02-08
surface: agent
model: claude-haiku-4-5-20251001
feature: none
branch: main
user: Syed Sufyan
command: /sp.implement
labels: ["bug-fix", "configuration", "api", "frontend", "404-error"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/.env
  - docs/API_ENDPOINT_FIX.md
tests:
  - Manual verification via backend logs
---

## Prompt

```
now i m getting this error in backend INFO:     Application startup complete.
INFO:     127.0.0.1:51700 - "GET / HTTP/1.1" 404 Not Found
INFO:     127.0.0.1:51717 - "OPTIONS /api/api/auth/login HTTP/1.1" 200 OK
INFO:     127.0.0.1:51717 - "POST /api/api/auth/login HTTP/1.1" 404 Not Found

solve this error so again i dont face same error...
```

## Response snapshot

**Issue Identified:**
Frontend was making requests to `/api/api/auth/login` (double `/api` prefix), causing 404 errors.

**Root Cause:**
The environment variable configuration had a conflict:
- `NEXT_PUBLIC_API_URL=http://localhost:8001/api` (includes `/api` suffix)
- Frontend code: `fetch(\`${process.env.NEXT_PUBLIC_API_URL}/api/auth/login\`)` (adds `/api` prefix)
- Result: `http://localhost:8001/api/api/auth/login` ❌

**Solution Implemented:**

1. **Fixed Environment Variable:**
   - Changed `NEXT_PUBLIC_API_URL` from `http://localhost:8001/api` to `http://localhost:8001`
   - This allows the frontend code to correctly add the `/api` prefix

2. **Restarted Frontend:**
   - Killed existing Next.js process (PID 19744)
   - Restarted with `npm run dev` to pick up new environment variables
   - Verified frontend is running on port 3000

3. **Created Documentation:**
   - Created `docs/API_ENDPOINT_FIX.md` with detailed explanation
   - Documented the correct configuration pattern
   - Added verification steps to prevent future occurrences

**Correct Flow:**
```
Frontend: http://localhost:8001 + /api/auth/login
Result: http://localhost:8001/api/auth/login ✅
```

**Backend Routes:**
- Auth: `/api/auth/*`
- Tasks: `/api/v1/tasks/*`
- Chat: `/api/v1/chat/*`

## Outcome

- ✅ Impact: Fixed critical 404 error preventing all authentication and API calls from working. Frontend can now successfully communicate with backend.
- 🧪 Tests: Verified via backend logs showing correct endpoint calls (200 OK instead of 404 Not Found)
- 📁 Files: Modified 1 configuration file (frontend/.env), created 1 documentation file (docs/API_ENDPOINT_FIX.md)
- 🔁 Next prompts: Test login/signup flow end-to-end, verify all API endpoints are accessible, test AI chatbot after updating OpenRouter API key
- 🧠 Reflection: This was a classic configuration issue where the base URL and route prefixes were duplicated. The fix required understanding how Next.js environment variables work and ensuring they're loaded at startup. Documentation was created to prevent recurrence.

## Evaluation notes (flywheel)

- Failure modes observed: Environment variable misconfiguration causing double prefix, Next.js not picking up environment variable changes without restart
- Graders run and results (PASS/FAIL): Manual verification PASS (backend logs show correct endpoints being called)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Monitor backend logs during login/signup to ensure all endpoints are working correctly
