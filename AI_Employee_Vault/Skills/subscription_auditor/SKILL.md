---
name: subscription_auditor
description: Analyze expenses to find unused or duplicate subscriptions.
---

# Subscription Auditor Skill

## 1. Purpose
Scans expense transactions to identify recurring payments that might be wasted spend.

## 2. Trigger
-   Monthly Schedule (via `ceo_briefing`).
-   Manual: "Check my subscriptions".

## 3. Input
-   **Data**: Odoo Expense records (Last 90 days).
-   **Usage Logs**: (Optional) System login logs if available.

## 4. Steps
1.  **Fetch Expenses**: Query Odoo for vendor bills/expenses.
2.  **Pattern Match**: Identify recurring same-amount transactions (e.g., Netflix, Adobe, AWS).
3.  **Analyze**:
    -   Is it Duplicate? (Two charges same vendor same month).
    -   Is it Zombie? (Paying for tool X but no logs of using tool X).
4.  **Flag**: Add to "Potential Savings" list.

## 5. Output
-   Section in `CEO_Briefing.md`.
-   Alert: `/Needs_Action/SUBSCRIPTION_ALERT_{Vendor}.md`.

## 6. Approval Required
-   **N/A** (Analysis only).

## 7. Error Handling
-   Pass silently if Odoo is offline (mark data as incomplete).
