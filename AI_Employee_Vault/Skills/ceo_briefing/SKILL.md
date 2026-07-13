---
name: ceo_briefing
description: Compile weekly business/accounting audit and briefing.
---

# CEO Briefing Skill

## 1. Purpose
Aggregates data from Odoo, Tasks, and System Health into a concise Markdown report for the CEO.

## 2. Trigger
-   Weekly Cron (Monday 8 AM).
-   Manual Task: "Generate Briefing".

## 3. Input
-   **Financials**: Revenue, Expenses, Cash flow (from Odoo MCP).
-   **Operations**: Completed tasks count, Bottlenecks (from `/Done` and Logs).
-   **Health**: System status (from watchdog).

## 4. Steps
1.  **Fetch Data**: Call `odoo_mcp.get_revenue_summary()`.
2.  **Analyze Tasks**: Scan `/Done` directory for last 7 days.
3.  **Audit Subscriptions**: Run `subscription_auditor` logic (or call it).
4.  **Draft Report**: Fill `Briefing_Template.md`.
5.  **Save**: Write to `/Briefings/`.
6.  **Notify**: Create `/Inbox/BRIEFING_READY.md`.

## 5. Output
-   Report: `/Briefings/{YYYY-MM-DD}_Monday_Briefing.md`.

## 6. Approval Required
-   **NO**. Read-only reporting.

## 7. Error Handling
-   Missing Component: Replace missing data with "N/A (Offline)". Do not fail the whole report.
