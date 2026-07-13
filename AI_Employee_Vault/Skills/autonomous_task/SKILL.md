---
name: autonomous_task
description: Execute multi-step tasks using the Ralph Wiggum Pattern.
---

# Autonomous Task Skill

## 1. Purpose
Allows the Agent to perform a task that requires multiple steps, verification, and error correction without stopping for human input at every step.

## 2. Trigger
-   Complex tasks in `/Needs_Action/` (e.g., "Install and configure X").
-   Orchestrator decision.

## 3. Input
-   **Goal**: The desired end state (e.g., "Odoo is running").
-   **Context**: `ralph_loop.py` provides previous iteration output.

## 4. Steps
1.  **Plan**: Check/Create `/Plans/{TaskID}_PLAN.md`.
2.  **Execute**: Perform *one* step from the plan.
3.  **Verify**: Check if the step worked (e.g., file exists, process running).
4.  **Update Plan**: Mark step as `[x]`.
5.  **Loop**: Return control to `ralph_loop.py` to repeat.
6.  **Finish**: Output `<promise>TASK_COMPLETE</promise>` when all steps done.

## 5. Output
-   Updated Plan: `/Plans/...`
-   System Changes (Files, Processes, etc.)
-   Logs in `/Logs/`.

## 6. Approval Required
-   **NO** for steps within the approved high-level task.
-   **YES** if the agent gets stuck (escalates to human).

## 7. Error Handling
-   Step Failure: Retry 3 times.
-   Total Failure: Create `/Needs_Action/HELP_NEEDED_{TaskID}.md`.
