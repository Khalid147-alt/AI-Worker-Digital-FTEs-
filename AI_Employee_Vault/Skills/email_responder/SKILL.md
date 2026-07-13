---
name: email_responder
description: Read emails, draft replies, and route for approval.
---

# Email Responder Skill

## 1. Purpose
Reads incoming emails from the `Needs_Action` queue, drafts appropriate responses based on `Company_Handbook.md`, and stages them for approval.

## 2. Trigger
-   New `.md` file in `/Needs_Action/` with `type: email` or `source: gmail_watcher`.
-   Manual request: "Draft a reply to this email."

## 3. Input
-   **Email Content**: Sender, Subject, Body (provided in the task file).
-   **Context**: `Company_Handbook.md` (tone), `Business_Goals.md` (priorities).

## 4. Steps
1.  **Analyze**: Read the email content. Identify the sender's intent/request.
2.  **Check Policy**: Consult `Company_Handbook.md` for tone (Professional/Friendly) and specific response rules (e.g., "Never promise dates without approval").
3.  **Draft**: Write the response.
    -   If missing info: Draft a "clarification request" or "holding reply".
    -   If standard request: Draft full answer.
4.  **Save**: Create a file in `/Pending_Approval/Email/`.
    -   Filename: `DRAFT_REPLY_{OriginalSender}_{Date}.md`
    -   Content: Validation metadata + Body.

## 5. Output
-   File: `/Pending_Approval/Email/DRAFT_REPLY_*.md`

## 6. Approval Required
-   **YES** (Always). No email is sent automatically unless explicitly whitelisted in `Company_Handbook.md`.

## 7. Error Handling
-   If sender is unknown/spam: Move original task to `/Rejected/` and log.
-   If context is missing: Create `/Needs_Action/HELP_NEEDED_Email_Context.md`.
