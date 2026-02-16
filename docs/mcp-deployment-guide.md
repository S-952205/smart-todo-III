# MCP Integration Deployment Guide

## Overview

This guide explains how to deploy and test the proper MCP-based AI chatbot implementation.

## Architecture

### New Architecture (MCP-Based)

```
User Request
    ↓
FastAPI Endpoint (/api/chat)
    ↓
ChatService (chat_service_mcp.py)
    ↓
OpenAI Agents SDK (Runner.run())
    ↓
Agent with MCP Server Connection
    ↓
MCP Server (mcp_server.py via stdio)
    ↓
MCP Tools (@mcp.tool decorators)
    ↓
Database Operations
```

## Files Created/Modified

### New Files

1. **backend/mcp_server.py** - FastMCP server with task management tools
2. **backend/services/chat_service_mcp.py** - Chat service using OpenAI Agents SDK
3. **backend/routes/chat_mcp.py** - API routes for MCP-based chat
4. **docs/architecture-analysis.md** - Detailed architecture comparison
5. **docs/mcp-deployment-guide.md** - This file

### Files to Update

1. **backend/main.py** - Add MCP routes (optional, for testing)
2. **backend/config.py** - Ensure OpenRouter settings are correct

## Prerequisites

### Required Packages

All packages are already installed:
- `fastmcp==3.0.0b1`
- `openai-agents>=0.7.0`
- `openai>=2.16.0`

### Environment Variables

Ensure `.env` has:
```env
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini  # Use a proper model, not free tier
DATABASE_URL=your_neon_postgres_url
```

**CRITICAL**: Do NOT use free tier models like "openrouter/free" - they don't support function calling properly.

## Testing the MCP Server Independently

### Step 1: Test MCP Server Directly

```bash
cd backend
python mcp_server.py
```

This starts the MCP server in stdio mode. You should see:
```
FastMCP server started
```

### Step 2: Test with fastmcp CLI

Install fastmcp CLI if not already installed:
```bash
pip install fastmcp[cli]
```

List available tools:
```bash
fastmcp list mcp_server.py
```

Call a tool:
```bash
fastmcp call mcp_server.py list_tasks user_id=test_user_123
```

## Deployment Options

### Option 1: Side-by-Side Testing (Recommended)

Keep both implementations and test the new one:

1. **Update main.py** to include both routes:

```python
# Existing route
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

# New MCP-based route (for testing)
from routes import chat_mcp
app.include_router(chat_mcp.router, prefix="/api/chat-mcp", tags=["chat-mcp"])
```

2. **Test the new endpoint**:
```bash
curl -X POST http://localhost:8000/api/chat-mcp \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "add task buy groceries"}'
```

3. **Compare responses** between `/api/chat` and `/api/chat-mcp`

### Option 2: Full Replacement

Replace the old implementation completely:

1. **Backup old files**:
```bash
mv backend/services/chat_service.py backend/services/chat_service_old.py
mv backend/routes/chat.py backend/routes/chat_old.py
```

2. **Rename new files**:
```bash
mv backend/services/chat_service_mcp.py backend/services/chat_service.py
mv backend/routes/chat_mcp.py backend/routes/chat.py
```

3. **Restart the server**:
```bash
uvicorn main:app --reload
```

## Testing Workflow

### Test Case 1: Add Task

**Request**:
```bash
curl -X POST http://localhost:8000/api/chat-mcp \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "add task buy groceries"}'
```

**Expected Response**:
```json
{
  "response": "Task created successfully! 'buy groceries' has been added.",
  "conversation_id": "uuid-here"
}
```

**What Should Happen**:
1. Agent receives message
2. Agent calls `add_task(title="buy groceries", user_id="user_id_from_jwt")`
3. MCP server creates task in database
4. Agent receives result and formats response

### Test Case 2: List Tasks

**Request**:
```bash
curl -X POST http://localhost:8000/api/chat-mcp \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "show my tasks"}'
```

**Expected Response**:
```json
{
  "response": "You have 1 task:\n- 1: buy groceries (Status: todo, Priority: medium)",
  "conversation_id": "uuid-here"
}
```

### Test Case 3: Update Task by Title

**Request**:
```bash
curl -X POST http://localhost:8000/api/chat-mcp \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "set status of grocery task to in-progress and priority high"}'
```

**Expected Behavior**:
1. Agent calls `list_tasks(user_id="user_id")`
2. Agent finds task with "grocery" in title
3. Agent calls `update_task(task_id=1, user_id="user_id", status="in-progress", priority="high")`
4. Agent responds with confirmation

**Expected Response**:
```json
{
  "response": "Task updated successfully! 'buy groceries' is now in-progress with high priority.",
  "conversation_id": "uuid-here"
}
```

### Test Case 4: Complete Task

**Request**:
```bash
curl -X POST http://localhost:8000/api/chat-mcp \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "complete my grocery task"}'
```

**Expected Behavior**:
1. Agent calls `list_tasks(user_id="user_id")`
2. Agent finds task with "grocery" in title
3. Agent calls `complete_task(task_id=1, user_id="user_id")`
4. Agent responds with confirmation

### Test Case 5: Delete Task

**Request**:
```bash
curl -X POST http://localhost:8000/api/chat-mcp \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "delete the grocery task"}'
```

**Expected Behavior**:
1. Agent calls `list_tasks(user_id="user_id")`
2. Agent finds task with "grocery" in title
3. Agent calls `delete_task(task_id=1, user_id="user_id")`
4. Agent responds with confirmation

## Troubleshooting

### Issue: MCP Server Not Starting

**Symptoms**: Error when starting chat service

**Solution**:
1. Check Python path: `which python` or `where python`
2. Verify mcp_server.py exists: `ls backend/mcp_server.py`
3. Test manually: `python backend/mcp_server.py`

### Issue: Tools Not Being Called

**Symptoms**: Agent responds but doesn't call tools

**Possible Causes**:
1. **Wrong model**: Using free tier models that don't support function calling
   - Solution: Use `openai/gpt-4o-mini` or `openai/gpt-3.5-turbo`

2. **MCP server not connected**: Check logs for connection errors
   - Solution: Verify MCP server path and Python executable

3. **Tool schemas invalid**: MCP tools not properly registered
   - Solution: Test MCP server independently with `fastmcp list`

### Issue: User ID Not Passed

**Symptoms**: Error "user_id not found" or "does not belong to user"

**Solution**:
1. Verify JWT token is valid
2. Check that user_id is extracted in chat service
3. Ensure agent instructions include user_id in tool calls

### Issue: Text-Based Tool Calls Still Appearing

**Symptoms**: Response contains `<tool_call>` text

**Possible Causes**:
1. **Still using old service**: Verify you're hitting `/api/chat-mcp` not `/api/chat`
2. **Wrong model**: Free tier models output text instead of calling tools
3. **MCP not connected**: Agent falling back to text generation

**Solution**:
1. Confirm endpoint: Check URL in request
2. Change model in `.env`: Use proper OpenAI model
3. Check logs: Look for "Starting MCP server" message

## Performance Considerations

### MCP Server Startup

Each chat request starts a new MCP server process via stdio. This adds ~500ms overhead.

**Optimization Options**:

1. **Use HTTP transport** instead of stdio:
   - Run MCP server as separate service
   - Connect via `MCPServerStreamableHttp`
   - Reduces per-request overhead

2. **Connection pooling**:
   - Keep MCP server running
   - Reuse connections across requests

3. **Caching**:
   - Cache tool schemas
   - Reduce MCP server restarts

## Monitoring

### Key Metrics to Track

1. **MCP Server Startup Time**: Should be <500ms
2. **Tool Call Success Rate**: Should be >95%
3. **Agent Response Time**: Should be <5s for simple operations
4. **Error Rate**: Should be <5%

### Logs to Monitor

```python
# In chat_service_mcp.py
logger.info(f"Starting MCP server at: {mcp_server_path}")
logger.info(f"Running agent for user {user_id}")
logger.info(f"Agent completed successfully for user {user_id}")
```

```python
# In mcp_server.py
logger.info(f"Task created: {task.id} for user: {user_id}")
logger.info(f"Retrieved {len(tasks)} tasks for user: {user_id}")
logger.info(f"Task updated: {task.id} for user: {user_id}")
```

## Rollback Plan

If issues occur:

1. **Immediate rollback**:
```bash
# Restore old files
mv backend/services/chat_service_old.py backend/services/chat_service.py
mv backend/routes/chat_old.py backend/routes/chat.py

# Restart server
pkill -f uvicorn
uvicorn main:app --reload
```

2. **Switch endpoint in frontend**:
```typescript
// Change from
const response = await fetch('/api/chat-mcp', ...)

// Back to
const response = await fetch('/api/chat', ...)
```

## Next Steps

1. **Test thoroughly** with all use cases
2. **Monitor performance** and error rates
3. **Optimize** MCP server connection if needed
4. **Update frontend** to use new endpoint
5. **Remove old implementation** once stable

## Comparison: Old vs New

| Aspect | Old (chat_service.py) | New (chat_service_mcp.py) |
|--------|----------------------|---------------------------|
| **Architecture** | Manual OpenAI API | OpenAI Agents SDK + MCP |
| **Tool Calling** | Manual JSON schemas | Automatic via MCP |
| **Tool Execution** | String-based routing | MCP protocol |
| **Reliability** | Low (text parsing) | High (protocol-based) |
| **Code Lines** | ~1070 lines | ~250 lines |
| **Fallback Parsers** | 400+ lines | None needed |
| **Maintenance** | High (manual schemas) | Low (auto-discovery) |

## Conclusion

The new MCP-based implementation is:
- **More reliable**: No text parsing needed
- **Easier to maintain**: Tools auto-discovered from MCP server
- **More scalable**: Can add tools without changing chat service
- **Standards-compliant**: Uses MCP protocol properly

The old implementation should be deprecated once the new one is stable.
