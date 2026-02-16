# Quick Fix Guide

## Problem Summary

You have TWO issues:

### Issue 1: Corrupted Data in Database
Tasks have invalid priority values like `'high, '` instead of `'high'`

### Issue 2: Still Using OLD Broken Implementation
You're using the old `chat_service.py` which has the text parsing issues I explained. The agent says it added a task but it's not actually calling the tool - it's just outputting text.

## Fix Steps

### Step 1: Clean Up Database

Run this command:
```bash
cd backend
python scripts/cleanup_task_data.py
```

This will fix all corrupted priority and status values.

### Step 2: Switch to NEW MCP Implementation

You have two options:

#### Option A: Test Side-by-Side (Recommended)

1. Update `backend/main.py`:
```python
# Add this import at the top
from routes import chat_mcp

# Add this route (keep the old one too)
app.include_router(chat_mcp.router, prefix="/api/v1/chat-mcp", tags=["chat-mcp"])
```

2. Update frontend to use new endpoint:
```typescript
// In your chat API service file
const response = await fetch('/api/v1/chat-mcp', {  // Changed from /api/v1/chat
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ message })
})
```

3. Restart backend:
```bash
uvicorn main:app --reload
```

#### Option B: Full Replacement

1. Backup old files:
```bash
cd backend
mv services/chat_service.py services/chat_service_old.py
mv routes/chat.py routes/chat_old.py
```

2. Rename new files:
```bash
mv services/chat_service_mcp.py services/chat_service.py
mv routes/chat_mcp.py routes/chat.py
```

3. Restart backend:
```bash
uvicorn main:app --reload
```

### Step 3: Update Environment

Make sure `.env` has:
```env
OPENROUTER_MODEL=openai/gpt-4o-mini
```

NOT:
```env
OPENROUTER_MODEL=openrouter/free
```

## Why This Matters

The OLD implementation (`chat_service.py`):
- ❌ Doesn't use MCP
- ❌ Has 400+ lines of unreliable text parsing
- ❌ Outputs `<tool_call>` as text instead of executing
- ❌ Tasks appear to be added but aren't actually created

The NEW implementation (`chat_service_mcp.py`):
- ✅ Uses proper MCP protocol
- ✅ Uses OpenAI Agents SDK
- ✅ Actually executes tools
- ✅ 75% less code
- ✅ No text parsing needed

## Quick Test

After switching, test with:
```bash
curl -X POST http://localhost:8000/api/v1/chat-mcp \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "add task test task"}'
```

Then check:
```bash
curl -X GET http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

You should see the task actually created in the database.
