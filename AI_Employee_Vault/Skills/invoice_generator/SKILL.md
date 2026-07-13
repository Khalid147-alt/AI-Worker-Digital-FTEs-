---
name: invoice_generator
description: Generate standard invoices in Odoo.
---

# Invoice Generator Skill

## 1. Purpose
Creates a draft invoice in Odoo for a specified client and amount.

## 2. Trigger
-   Task: "Send invoice to Client X for $Y".
-   WhatsApp request: "Bill them for the consultation".

## 3. Input
-   **Partner Name**: Client name matches Odoo "Res.Partner".
-   **Amount**: Numerical value.
-   **Description**: Service details.
-   **Due Date**: (Optional).

## 4. Steps
1.  **Validate Input**: Ensure partner name and amount are present.
2.  **Search Partner**: Use Odoo MCP `search_read` to find partner ID.
    -   If not found: Fail or ask to create.
3.  **Create Invoice**: Use Odoo MCP `create_invoice` (or `account.move` create).
    -   Status: `Draft` (Always start as draft).
4.  **Log**: Record action in Audit Log.

## 5. Output
-   Odoo Record: New Invoice (Draft).
-   File: `/Done/INVOICE_GENERATED_{Partner}_{ID}.md` (Confirmation).

## 6. Approval Required
-   **NO** for creation (Draft is safe).
-   **YES** for Posting/Sending (Human must click 'Post' in Odoo or approve a separate 'Send' task).

## 7. Error Handling
-   Partner not found: Create `/Needs_Action/ERROR_Partner_Missing.md`.
-   MCP Failure: Retry using `retry_handler`.
