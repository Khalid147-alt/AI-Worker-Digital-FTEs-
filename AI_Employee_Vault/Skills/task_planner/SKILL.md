---
name: task_planner
description: Decompose high-level goals into actionable plans.
---

# Task Planner Skill

## 1. Purpose
Takes a vague or complex user request and breaks it down into a structured Implementation Plan.

## 2. Trigger
-   Complex task labeled "Plan" in `/Needs_Action/`.
-   Invoked by `autonomous_task` when complexity > 3 steps.

## 3. Input
-   **Goal**: "Set up a new marketing campaign" or "Migrate database".
-   **Constraints**: Deadlines, budget, tools available.

## 4. Steps
1.  **Analyze Goal**: Identify the final deliverable.
2.  **Breakdown**: Split into phases (Research, Implementation, Verification).
3.  **Task Creation**: Define granular steps for each phase.
4.  **Dependency Check**: Ensure Step B follows Step A.
5.  **Write Plan**: Save as `implementation_plan.md` or specialized plan file.

## 5. Output
-   File: `/Plans/{TaskName}_PLAN.md` (Checklist format).

## 6. Approval Required
-   **YES**. The User should review the plan before execution starts (unless `autonomous_task` overrides).

## 7. Error Handling
-   If goal is too vague: Ask clarifying questions in `/Needs_Action/QUESTIONS_FOR_USER.md`.
