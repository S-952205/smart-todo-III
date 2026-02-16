# AI Chatbot Task Management Fixes

**Date:** 2026-02-16
**Issue:** Inconsistent task operations when users refer to tasks by title instead of ID
**Status:** Fixed

## Problem Analysis

### Root Causes Identified

1. **Unclear Tool Descriptions**: The function descriptions for `update_task`, `complete_task`, and `delete_task` didn't explicitly state that `list_tasks` must be called first when users refer to tasks by title.

2. **Insufficient System Prompt**: The system prompt lacked clear step-by-step workflow instructions for the LLM to follow when processing task operations.

3. **Missing Workflow Examples**: No concrete examples showing the correct two-step process (list → operate).

### Symptoms

Users experienced these issues:
```
User: "set status of task to in progress and priority low"
Bot: "I couldn't find the task you're referring to. Let me first list your current tasks..."
[Then calls list_tasks but doesn't proceed with the update]

User: "update pak ind match task"
Bot: [Calls update_task without task_id, causing error]
```

## Solutions Implemented

### 1. Enhanced Tool Descriptions

**Before:**
```javascript
"name": "list_tasks",
"description": "List all tasks for the user. Use this to find task IDs when the user refers to tasks by title."
```

**After:**
```javascript
"name": "list_tasks",
"description": "List all tasks for the user with their IDs, titles, status, and priority. CRITICAL: You MUST call this function FIRST whenever the user refers to a task by its title or description (e.g., 'update my grocery task', 'complete the meeting task'). This is the ONLY way to get task IDs needed for update_task, complete_task, and delete_task operations."
```

**Changes Applied to All Tools:**
- `list_tasks`: Added CRITICAL workflow requirement
- `update_task`: Added "REQUIRES the numeric task_id. If you don't have the task_id, you MUST call list_tasks first"
- `complete_task`: Same requirement added
- `delete_task`: Same requirement added

### 2. Restructured System Prompt

**New Structure:**
```
CRITICAL WORKFLOW RULES:
1. When user refers to a task by title/description (NOT by ID number), you MUST:
   Step 1: Call list_tasks() to get all tasks with their IDs
   Step 2: Find the matching task in the results
   Step 3: Use that task's ID to call update_task/complete_task/delete_task

2. When user provides a specific task ID number, you can directly call the operation
```

**Added Concrete Examples:**
```
User: "set status of my grocery task to in progress"
→ Step 1: Call list_tasks()
→ Step 2: Find task with title containing "grocery"
→ Step 3: Call update_task(task_id=X, status="in-progress")
```

### 3. Improved Parameter Descriptions

**Before:**
```javascript
"task_id": {
    "type": "integer",
    "description": "ID of the task to update"
}
```

**After:**
```javascript
"task_id": {
    "type": "integer",
    "description": "REQUIRED: Numeric ID of the task to update (get this from list_tasks if you don't have it)"
}
```

## Files Modified

### backend/services/chat_service.py
- Lines 254-263: Enhanced `list_tasks` tool description
- Lines 265-281: Enhanced `complete_task` tool description
- Lines 283-316: Enhanced `update_task` tool description
- Lines 317-333: Enhanced `delete_task` tool description
- Lines 340-383: Completely restructured system prompt with workflow rules and examples

## Testing Recommendations

### Test Cases to Verify

1. **Task Reference by Title:**
   ```
   User: "set status of grocery task to in-progress"
   Expected: Bot calls list_tasks(), finds task, then calls update_task()
   ```

2. **Task Reference by ID:**
   ```
   User: "update task 43 to high priority"
   Expected: Bot directly calls update_task(task_id=43, priority="high")
   ```

3. **Ambiguous Task Reference:**
   ```
   User: "complete my task"
   Expected: Bot calls list_tasks() and asks for clarification
   ```

4. **Multiple Operations:**
   ```
   User: "set my meeting task to in-progress and high priority"
   Expected: Bot calls list_tasks(), then update_task() with both parameters
   ```

5. **Non-existent Task:**
   ```
   User: "delete my xyz task"
   Expected: Bot calls list_tasks(), doesn't find match, informs user
   ```

## Additional Improvements

### Created Documentation
- **docs/chatbot-usage-guide.md**: Comprehensive user guide with examples and troubleshooting

### User Guide Highlights
- Clear examples for all operations
- Explanation of how the chatbot works internally
- Troubleshooting section for common issues
- Tips for best results

## Expected Behavior After Fixes

### Scenario 1: Update by Title
```
User: "set status of pak ind match task to in-progress and priority low"

Bot Internal Process:
1. Recognizes user is referring to task by title
2. Calls list_tasks() → Gets all tasks
3. Searches for task with title containing "pak ind match"
4. Finds task_id: 43
5. Calls update_task(task_id=43, status="in-progress", priority="low")
6. Responds: "Task updated successfully! 'Pak Ind Match' is now in-progress with low priority."
```

### Scenario 2: Complete by Title
```
User: "complete the meeting prep task"

Bot Internal Process:
1. Calls list_tasks()
2. Finds task with title containing "meeting prep"
3. Calls complete_task(task_id=X)
4. Responds: "Task 'Meeting Prep' marked as complete!"
```

### Scenario 3: Delete by Title
```
User: "delete my old shopping task"

Bot Internal Process:
1. Calls list_tasks()
2. Searches for task with title containing "shopping"
3. Calls delete_task(task_id=X)
4. Responds: "Task deleted successfully!"
```

## Monitoring and Validation

### Metrics to Track
- Success rate of task operations (target: >95%)
- Frequency of "task not found" errors (target: <5%)
- Number of list_tasks calls before operations (should be ~100% when using titles)
- User satisfaction with task management via chat

### Logs to Monitor
```python
logger.info(f"Executing tool: {function_name} with args: {function_args}")
logger.info(f"Parsed XML parameters: {function_name} with args: {function_args}")
logger.warning(f"Model outputted tool call syntax as text instead of using proper tool calling")
```

## Known Limitations

1. **LLM Model Variability**: Different models on OpenRouter may interpret instructions differently. The free tier models may still occasionally fail to follow the workflow.

2. **Fuzzy Matching**: The system doesn't implement fuzzy string matching. Users must use reasonably accurate task titles.

3. **Multiple Matches**: If multiple tasks have similar titles, the bot may pick the first match. Users should use more specific descriptions.

## Future Enhancements

### Recommended Improvements

1. **Implement Fuzzy Matching**: Use libraries like `fuzzywuzzy` to better match task titles
   ```python
   from fuzzywuzzy import process
   best_match = process.extractOne(user_query, task_titles)
   ```

2. **Add Confirmation for Ambiguous Matches**: When multiple tasks match, ask user to confirm
   ```
   Bot: "I found 2 tasks matching 'meeting':
        1. Meeting Prep (ID: 43)
        2. Team Meeting (ID: 44)
        Which one did you mean?"
   ```

3. **Implement Task Context Memory**: Store recently mentioned tasks in conversation context
   ```python
   conversation_context = {
       "last_mentioned_task_id": 43,
       "last_operation": "update"
   }
   ```

4. **Add Batch Operations**: Support operations on multiple tasks
   ```
   User: "mark all my todo tasks as in-progress"
   Bot: [Lists tasks, filters by status='todo', updates all]
   ```

5. **Natural Language Date Parsing**: Support phrases like "tomorrow", "next week"
   ```python
   from dateutil.parser import parse
   due_date = parse("tomorrow", fuzzy=True)
   ```

## Rollback Plan

If issues persist after deployment:

1. **Immediate Rollback**: Revert chat_service.py to previous version
   ```bash
   git checkout HEAD~1 backend/services/chat_service.py
   ```

2. **Fallback Mode**: Add a flag to disable AI task management and use direct API calls
   ```python
   if settings.disable_ai_task_management:
       return {"error": "AI task management temporarily disabled"}
   ```

3. **Manual Override**: Allow users to use task IDs directly as a workaround

## Conclusion

The fixes address the core workflow issues by making the LLM's responsibilities crystal clear:
- **When to call list_tasks**: Always when user refers to tasks by title
- **How to use the results**: Extract task_id and use it in subsequent operations
- **What to do on failure**: Inform user clearly and suggest alternatives

These changes should significantly improve the reliability of task management through the AI chatbot.

---

**Implemented by:** Claude Code (Haiku 4.5)
**Reviewed by:** [Pending]
**Deployed to:** [Pending]
