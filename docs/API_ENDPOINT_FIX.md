# API Endpoint Configuration Fix

## Issue
Frontend was making requests to `/api/api/auth/login` (double `/api` prefix), resulting in 404 errors.

## Root Cause
The environment variable `NEXT_PUBLIC_API_URL` included `/api` suffix, and the frontend code was also adding `/api` prefix to all routes.

## Solution

### Before (Incorrect)
```bash
# frontend/.env
NEXT_PUBLIC_API_URL=http://localhost:8001/api  # ❌ Has /api suffix
```

Frontend code:
```typescript
fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`)
// Results in: http://localhost:8001/api/api/auth/login ❌
```

### After (Correct)
```bash
# frontend/.env
NEXT_PUBLIC_API_URL=http://localhost:8001  # ✅ No /api suffix
```

Frontend code:
```typescript
fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`)
// Results in: http://localhost:8001/api/auth/login ✅
```

## Backend Routes
The backend FastAPI application has routes configured as:
- Auth routes: `/api/auth/*` (e.g., `/api/auth/login`, `/api/auth/signup`)
- Task routes: `/api/v1/tasks/*`
- Chat routes: `/api/v1/chat/*`

## Environment Variable Configuration

### Frontend (.env)
```bash
# Backend API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_API_BASE_URL=http://localhost:8001
NEXT_PUBLIC_BASE_URL=http://localhost:3000
```

### Backend (.env)
```bash
# Database Configuration
DATABASE_URL=postgresql://...

# Auth Configuration
BETTER_AUTH_SECRET=...
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenRouter API Configuration
OPENROUTER_API_KEY=sk-or-v1-...
```

## Testing
After making this change, you must restart the Next.js development server:

```bash
# Stop the current server (Ctrl+C or kill process)
# Then restart:
cd frontend
npm run dev
```

## Important Notes
1. **Always restart Next.js** after changing `NEXT_PUBLIC_*` environment variables
2. **Do not include `/api` in the base URL** - let the frontend code add route prefixes
3. **Backend runs on port 8001** (port 8000 is reserved for other work)
4. **Frontend runs on port 3000**

## Verification
Check backend logs for correct endpoint calls:
```
✅ INFO: 127.0.0.1:xxxxx - "POST /api/auth/login HTTP/1.1" 200 OK
❌ INFO: 127.0.0.1:xxxxx - "POST /api/api/auth/login HTTP/1.1" 404 Not Found
```
