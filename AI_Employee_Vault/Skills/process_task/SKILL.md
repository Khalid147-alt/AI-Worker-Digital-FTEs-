# Skill: Process Incoming Task

## Purpose
Read the /Needs_Action folder, understand each task, create a plan, and update the Dashboard.

## Trigger
Run this skill when new .md files appear in /Needs_Action/

## Instructions

1. **Read** all .md files in /Needs_Action/ that have `status: pending`
2. **Understand** the task type (email, file_drop, etc.)
3. **Classify** priority: high / medium / low based on content
4. **Create** a Plan entry in the file:
   - Add a `## Plan` section with checkboxes for next steps
   - Change `status: pending` → `status: in_progress`
5. **Update** Dashboard.md:
   - Increment "Pending Tasks" count
   - Add a one-line entry to "Recent Activity"
6. **Log** the action in /Logs/YYYY-MM-DD.md:
   ```
   [HH:MM] Processed task: <filename> | Type: <type> | Priority: <priority>
   ```

## Completion Criteria
All files in /Needs_Action have been read, planned, and logged.
Dashboard.md is up to date.
