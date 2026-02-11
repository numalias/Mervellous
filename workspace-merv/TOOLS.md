# Tools Reference — Merv (Orchestrator)

## Primary Tools

### sessions_spawn
Spawn a sub-agent to execute a task. This is your main tool.

**Usage:**
- Provide a complete brief with OBJECTIVE, CONTEXT, CONSTRAINTS, DELIVERABLE, PRIORITY
- Agent runs in isolation — no shared context
- Results are returned when the agent completes

### sessions_list
List all active agent sessions. Use to monitor running tasks.

### sessions_history
View the conversation history of a specific session. Use to debug or review agent work.

### sessions_send
Send a follow-up message to an active session. Use to provide clarification or additional instructions.

### memory_read / memory_write
Read and write to long-term memory. Use to persist important context across sessions.

### message
Send messages to the user via the active channel.

### read / write
Read and write files in your workspace. Use for notes, logs, and coordination files.

## Orchestration Patterns

### Parallel Spawn
When tasks are independent, spawn multiple agents simultaneously:
- Research + Code → spawn finch AND linus in parallel
- Analyze + Document → spawn nova AND iris in parallel

### Sequential Chain
When tasks depend on each other:
1. Spawn finch (research) → get results
2. Pass results to linus (implementation)
3. Pass code to forge (deployment)

### Review Loop
For quality-critical tasks:
1. Spawn linus (first implementation)
2. Review output
3. If issues found → spawn linus again with corrections
4. Deliver final result
