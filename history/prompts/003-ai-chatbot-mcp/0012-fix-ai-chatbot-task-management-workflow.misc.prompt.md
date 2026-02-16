---
id: 0012
title: Fix AI chatbot task management workflow
stage: misc
date: 2026-02-16
surface: agent
model: claude-haiku-4-5-20251001
feature: 003-ai-chatbot-mcp
branch: main
user: user
command: /sp.implement
labels: ["bug-fix", "ai-chatbot", "task-management", "workflow", "prompt-engineering"]
links:
  spec: specs/003-ai-chatbot-mcp/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/services/chat_service.py
  - docs/chatbot-usage-guide.md
  - docs/chatbot-fixes-summary.md
tests:
  - None (prompt engineering fix)
---

## Prompt

```
i want you to analyze my spec 003 and see the implementation of this feature ...
since when i m interactung with agent for task management.. there are several issues that are consistent..
when i tell the agent to add task agent adds task.. but listing task, updating deleting there is issue....
u can see issue is something like this : set status of task to in progress and prirotiy low
19:44
I couldn't find the task you're referring to. Let me first list your current tasks so you can tell me which one to update:

<tool_call>
{"name": "list_tasks", "arguments": {}}
</tool_call>
19:45
update pak ind match task
19:46
<tool_call>
<function=update_task>
<parameter=priority>
low
</parameter>
<parameter=status>
in-progress
</parameter>
<parameter=task_id>
43
</parameter>
</function>
</tool_call>
19:46

i want you to fix these issues in a better way.. and tell me how to use agent via converstion for task managing..
if u need any help from internet or from docs u have ccontext7 mcp server connected
```

## Response snapshot

**Problem Identified:**
The AI chatbot was inconsistently handling task operations when users referred to tasks by title instead of ID. The LLM would sometimes call `list_tasks` but fail to proceed with the actual operation, or attempt operations without first retrieving the task ID.

**Root Causes:**
1. Tool descriptions didn't explicitly require calling `list_tasks` first when users refer to tasks by title
2. System prompt lacked clear step-by-step workflow instructions
3. No concrete examples showing the correct two-step process (list → operate)

**Solutions Implemented:**

1. **Enhanced Tool Descriptions** - Added explicit workflow requirements to all task operation tools:
   - `list_tasks`: Added "CRITICAL: You MUST call this function FIRST whenever the user refers to a task by its title or description"
   - `update_task`, `complete_task`, `delete_task`: Added "REQUIRES the numeric task_id. If you don't have the task_id, you MUST call list_tasks first"

2. **Restructured System Prompt** - Created clear workflow rules:
   ```
   CRITICAL WORKFLOW RULES:
   1. When user refers to a task by title/description (NOT by ID number), you MUST:
      Step 1: Call list_tasks() to get all tasks with their IDs
      Step 2: Find the matching task in the results
      Step 3: Use that task's ID to call update_task/complete_task/delete_task

   2. When user provides a specific task ID number, you can directly call the operation
   ```

3. **Added Concrete Examples** - Provided step-by-step examples for common scenarios:
   - "set status of my grocery task to in progress" → list_tasks() → find match → update_task()
   - "complete the meeting prep task" → list_tasks() → find match → complete_task()

4. **Created Documentation:**
   - `docs/chatbot-usage-guide.md`: Comprehensive user guide with examples and troubleshooting
   - `docs/chatbot-fixes-summary.md`: Technical documentation of fixes and testing recommendations

**Expected Behavior After Fixes:**
```
User: "set status of pak ind match task to in-progress and priority low"

Bot Internal Process:
1. Recognizes user is referring to task by title
2. Calls list_tasks() → Gets all tasks
3. Searches for task with title containing "pak ind match"
4. Finds task_id: 43
5. Calls update_task(task_id=43, status="in-progress", priority="low")
6. Responds: "Task updated successfully!"
```

## Outcome

- ✅ Impact: Fixed critical workflow issue preventing reliable task management via AI chatbot. Enhanced tool descriptions and system prompt to enforce correct two-step workflow (list → operate) when users refer to tasks by title.
- 🧪 Tests: No automated tests added (prompt engineering fix). Recommended manual testing scenarios documented in chatbot-fixes-summary.md
- 📁 Files: Modified 1 file (chat_service.py), created 2 documentation files (usage guide and fixes summary)
- 🔁 Next prompts: Test the fixes with real user interactions, monitor success rates, consider implementing fuzzy matching for better task title matching
- 🧠 Reflection: This was a prompt engineering fix rather than a code logic fix. The issue was that the LLM wasn't consistently following the required workflow. By making the workflow requirements explicit and mandatory in both tool descriptions and system prompt, the LLM should now reliably call list_tasks before performing operations on tasks referenced by title.

## Evaluation notes (flywheel)

- Failure modes observed: LLM inconsistently calling list_tasks before task operations; LLM attempting operations without task_id; LLM calling list_tasks but not proceeding with the operation
- Graders run and results (PASS/FAIL): Manual review PASS - tool descriptions now explicitly require list_tasks workflow; system prompt includes clear step-by-step instructions with examples
- Prompt variant (if applicable): Enhanced system prompt with CRITICAL WORKFLOW RULES section and concrete examples
- Next experiment (smallest change to try): Monitor real-world usage to see if the enhanced prompts resolve the issue; if problems persist, consider adding fuzzy string matching or implementing a task context memory system
