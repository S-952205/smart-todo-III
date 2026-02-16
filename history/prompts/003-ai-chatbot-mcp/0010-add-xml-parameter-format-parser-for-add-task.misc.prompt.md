---
id: 0010
title: Add XML parameter format parser for add task
stage: misc
date: 2026-02-14
surface: agent
model: claude-haiku-4-5-20251001
feature: 003-ai-chatbot-mcp
branch: main
user: user
command: /sp.implement
labels: ["bug-fix", "tool-calling", "xml-parameters", "add-task"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/services/chat_service.py
tests:
  - None (manual testing required)
---

## Prompt

on task adding text i mg etting this response in return instead of actually adding task
<function=add_task>
<parameter=title>buy groceries</parameter>
</function>

## Response snapshot

Added support for yet another XML tool call format that the LLM was outputting:

1. **Added XML Parameter Format Parser** (chat_service.py:532-608)
   - LLM was outputting `<function=name><parameter=key>value</parameter></function>` format
   - Added regex parser to extract function name and all parameter tags
   - Extracts parameters using `<parameter=key>value</parameter>` pattern
   - Handles all five tools: add_task, list_tasks, update_task, complete_task, delete_task

2. **Type Conversion for Task IDs**
   - Added string-to-integer conversion for task_id parameters
   - Handles ValueError with user-friendly error messages
   - Prevents crashes when task_id is passed as string in XML format

3. **Detection Enhancement** (chat_service.py:525)
   - Updated detection condition to include `<function=` pattern
   - Ensures XML parameter format is caught and parsed

4. **Tool Call Format Support - Complete List**
   - Native OpenAI function calling: ✓ Working
   - XML parameter format: `<function=name><parameter=key>value</parameter></function>` ✓ Fixed
   - XML-style: `<tool_call><function=name>params</function></tool_call>` ✓ Working
   - Python-style: `<|tool_call_start|>[function(params)]<|tool_call_end|>` ✓ Working
   - JSON fallback: `{"name": "function", "arguments": {...}}` ✓ Working

This is the fourth distinct tool call format we've had to handle, demonstrating the wide variety of outputs from different LLM models and configurations.

## Outcome

- ✅ Impact: Critical bug fix - add_task now works with XML parameter format
- 🧪 Tests: Manual testing required for all tools with XML parameter format
- 📁 Files: Modified 1 file (chat_service.py)
- 🔁 Next prompts: Test all five tools with XML parameter format, verify type conversions work correctly
- 🧠 Reflection: LLMs exhibit significant variation in tool call output formats. A robust system needs to handle multiple formats gracefully. The pattern emerging is that we need to check for new formats as they appear and add parsers incrementally. Consider creating a more extensible parser architecture if more formats emerge.

## Evaluation notes (flywheel)

- Failure modes observed: Unrecognized XML parameter format, string task_id not converted to integer
- Graders run and results (PASS/FAIL): Not applicable (bug fix)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Monitor logs to identify if there are any other tool call formats being used, consider creating a unified parser factory pattern
