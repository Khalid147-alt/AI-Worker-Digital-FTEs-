---
name: audit_review
description: Summarize and flag issues in audit logs.
---

# Audit Review Skill

## 1. Purpose
Scans daily audit logs to ensure the AI is behaving correctly and within safety limits.

## 2. Trigger
-   Daily Cron.
-   Manual: "Review today's logs".

## 3. Input
-   **Logs**: Files in `/Logs/*.json`.
-   **Rules**: Thresholds (e.g., max $1000 transaction).

## 4. Steps
1.  **Load**: Read logs for the target period.
2.  **Aggregate**: Count actions by type (Email, File, Money).
3.  **Scan**: Check for "Warning" or "Failure" status.
4.  **Detect**: Look for anomalies (e.g., 50 emails in 1 minute).
5.  **Report**: Generate summary.

## 5. Output
-   File: `/Briefings/AUDIT_REPORT_{Date}.md`.

## 6. Approval Required
-   **NO**. Read-only.

## 7. Error Handling
-   Corrupt Log: Skip line/file and note in report.
