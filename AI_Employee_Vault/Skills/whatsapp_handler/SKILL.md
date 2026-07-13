---
name: whatsapp_handler
description: Process WhatsApp messages and draft replies.
---

# WhatsApp Handler Skill

## 1. Purpose
Parses incoming WhatsApp messages, determines if they are actionable, and drafts replies for the user to approve.

## 2. Trigger
-   New file in `/Needs_Action/` with `type: whatsapp_message`.
-   Manual request via Dashboard.

## 3. Input
-   **Message**: Sender name, Group name (if any), Message text.
-   **Context**: previous chat history (if available in logs).

## 4. Steps
1.  **Filter**: Ignore system messages or non-actionable chatter (Example: "Ok", "Thumbs up").
2.  **Identify Intent**:
    -   *Task Request*: "Can you send the invoice?" -> Trigger `invoice_generator` skill.
    -   *Question*: "What is our revenue?" -> Draft answer.
    -   *Chat*: "Hello" -> Draft polite greeting.
3.  **Draft**: Create a reply draft.
4.  **Save/Action**:
    -   If simple chat: Save to `/Pending_Approval/WhatsApp/`.
    -   If task: create a new linked task in `/Needs_Action/`.

## 5. Output
-   File: `/Pending_Approval/WhatsApp/REPLY_{Sender}.md`
-   OR New Task: `/Needs_Action/TASK_FROM_{Sender}.md`

## 6. Approval Required
-   **YES**. All messages require approval.

## 7. Error Handling
-   If message is unreadable: Log warning in `dashboard.md`.
-   If sender is VIP (defined in Handbook) and processing fails: Trigger `SYSTEM_ALERT`.
