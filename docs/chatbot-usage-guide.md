# AI Chatbot Task Management Guide

## Overview
The AI chatbot helps you manage tasks through natural language conversation. It uses intelligent tool calling to perform operations on your tasks while maintaining security through JWT authentication.

## How to Use the Chatbot

### 1. Adding Tasks

**Simple Format:**
```
add task [task name]
create task [task name]
remind me to [task name]
```

**Examples:**
- "add task buy groceries"
- "create a task to call mom"
- "remind me to finish the report"
- "add task movie night with friends"

**With Description:**
- "add task buy groceries with description get milk, eggs, and bread"

### 2. Listing Tasks

**Commands:**
```
list my tasks
show all tasks
what are my tasks?
show me my todo list
```

**What You'll See:**
The chatbot will display all your tasks with:
- Task ID (number)
- Title
- Status (todo, in-progress, done)
- Priority (low, medium, high)

### 3. Updating Tasks

**By Task Title (Recommended):**
```
set status of [task name] to [status]
change priority of [task name] to [priority]
update [task name] status to [status]
```

**Examples:**
- "set status of grocery task to in-progress"
- "change priority of meeting prep to high"
- "update pak ind match task to done"
- "set my report task priority to low"

**By Task ID (If You Know It):**
- "update task 43 to high priority"
- "set task 25 status to in-progress"

**Valid Values:**
- Status: `todo`, `in-progress`, `done`
- Priority: `low`, `medium`, `high`

### 4. Completing Tasks

**By Task Title:**
```
complete [task name]
mark [task name] as complete
finish [task name]
```

**Examples:**
- "complete my grocery task"
- "mark meeting prep as complete"
- "finish the report task"

**By Task ID:**
- "complete task 43"
- "mark task 25 as done"

### 5. Deleting Tasks

**By Task Title:**
```
delete [task name]
remove [task name]
delete my [task name] task
```

**Examples:**
- "delete grocery task"
- "remove the meeting prep task"
- "delete my old shopping task"

**By Task ID:**
- "delete task 43"
- "remove task 25"

## How the Chatbot Works Behind the Scenes

### Intelligent Workflow
When you refer to a task by its title (not ID), the chatbot automatically:

1. **Calls list_tasks()** - Retrieves all your tasks with their IDs
2. **Finds the matching task** - Searches for tasks with titles matching your description
3. **Performs the operation** - Uses the task ID to update/complete/delete

**Example Flow:**
```
You: "set status of grocery task to in-progress"

Chatbot internally:
1. Calls list_tasks() → Gets all tasks
2. Finds task with title containing "grocery" → task_id: 43
3. Calls update_task(task_id=43, status="in-progress")
4. Responds: "Task updated successfully! 'Buy groceries' is now in-progress."
```

### Security Features
- All operations are authenticated with your JWT token
- You can only access and modify your own tasks
- User isolation is enforced at the database level

## Tips for Best Results

### ✅ DO:
- Use clear, descriptive task titles
- Be specific when referring to tasks (e.g., "grocery task" not just "task")
- Use natural language - the AI understands context
- Ask to list tasks if you're unsure what you have

### ❌ DON'T:
- Don't use ambiguous references like "that task" or "the one I mentioned"
- Don't expect the chatbot to remember tasks from previous conversations without listing them first
- Don't use special characters or emojis in task titles (they may cause parsing issues)

## Common Scenarios

### Scenario 1: Quick Task Creation
```
You: add task prepare presentation
Bot: Task created successfully! 'prepare presentation' has been added.
```

### Scenario 2: Updating Task Status
```
You: set status of presentation task to in-progress
Bot: [Internally lists tasks, finds the match]
     Task updated successfully! 'prepare presentation' is now in-progress.
```

### Scenario 3: Checking Progress
```
You: show my tasks
Bot: You have 3 tasks:
     - 43: Buy groceries (Status: todo, Priority: medium)
     - 44: Prepare presentation (Status: in-progress, Priority: high)
     - 45: Call mom (Status: todo, Priority: low)
```

### Scenario 4: Completing Multiple Tasks
```
You: complete grocery task
Bot: Task 'Buy groceries' marked as complete!

You: also complete the call mom task
Bot: Task 'Call mom' marked as complete!
```

## Troubleshooting

### "I couldn't find the task you're referring to"
**Cause:** The chatbot couldn't match your description to any task title.

**Solution:**
1. Ask to list all tasks: "show my tasks"
2. Use the exact task title or task ID
3. Be more specific in your description

### "Missing required parameter 'task_id'"
**Cause:** The chatbot tried to perform an operation without getting the task ID first.

**Solution:** This should be rare with the improved system. If it happens:
1. List your tasks first: "list my tasks"
2. Use the task ID directly: "update task 43 to high priority"

### Tool Call Syntax Appears as Text
**Cause:** Some AI models output tool calls as text instead of using proper function calling.

**Solution:** The system has fallback parsers that handle this automatically. If you see raw XML or JSON in responses, report it as a bug.

## Advanced Usage

### Batch Operations
```
You: list my tasks, then mark all todo tasks as in-progress
Bot: [Lists tasks, then updates each one]
```

### Filtering by Status
```
You: show me only my in-progress tasks
Bot: [Lists and filters tasks with status='in-progress']
```

### Task Search
```
You: do I have any tasks related to meetings?
Bot: [Searches task titles for "meeting" keyword]
```

## API Integration (For Developers)

### Endpoint
```
POST /api/chat
```

### Request Format
```json
{
  "message": "add task buy groceries",
  "conversation_id": "optional-uuid"
}
```

### Response Format
```json
{
  "response": "Task created successfully! 'buy groceries' has been added.",
  "conversation_id": "uuid-of-conversation"
}
```

### Authentication
Include JWT token in Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Support

If you encounter issues:
1. Check this guide for common solutions
2. Try rephrasing your request
3. Use task IDs directly if title matching fails
4. Report persistent issues to the development team

---

**Last Updated:** 2026-02-16
**Version:** 1.0
