# Skill: Execute Planned Task

## Purpose
Take a task that is `status: in_progress` and execute the next step in its Plan.

## Trigger
Run this skill when there are files in /Needs_Action/ with `status: in_progress`.

## Instructions

1. **Read** files in /Needs_Action/ with `status: in_progress`.
2. **Find** the `## Plan` section.
3. **Identify** the first *unchecked* checkbox (the next step).
4. **Execute** that step:
   - If it says "Review...", read the content and add a summary.
   - If it says "Draft...", create a new file or draft content in the existing file.
   - If it says "Submit for approval", create a file named `APPROVAL_REQUIRED_<taskname>.md` and wait.
5. **Update** the file:
   - Check the box you just completed `[x]`.
   - Add a note/result below the item if needed.
6. **Log** the execution in /Logs/YYYY-MM-DD.md.

## Safe Mode
- If the step involves sending an email or external action, STOP and create an `APPROVAL_REQUIRED` request instead.
