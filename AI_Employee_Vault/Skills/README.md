# Agent Skills Index

This directory contains the "Job Descriptions" for the AI Employee.
Each folder contains a `SKILL.md` defining how to perform that capability.

| Skill Name | Description | Trigger |
|------------|-------------|---------|
| **[audit_review](./audit_review/SKILL.md)** | Analyzes logs for compliance and anomalies. | Daily/Manual |
| **[autonomous_task](./autonomous_task/SKILL.md)** | Executes complex multi-step loops (Ralph Pattern). | Orchestrator |
| **[ceo_briefing](./ceo_briefing/SKILL.md)** | Generates weekly business and financial reports. | Weekly Cron |
| **[email_responder](./email_responder/SKILL.md)** | Drafts replies to emails based on handbook. | New Email |
| **[invoice_generator](./invoice_generator/SKILL.md)** | Creates draft invoices in Odoo. | Task/Request |
| **[social_media_poster](./social_media_poster/SKILL.md)** | Creates and posts social content. | Schedule |
| **[subscription_auditor](./subscription_auditor/SKILL.md)** | Finds unused subscriptions in expenses. | Monthly/Manual |
| **[task_planner](./task_planner/SKILL.md)** | Breaks down goals into implementation plans. | Complex Request |
| **[whatsapp_handler](./whatsapp_handler/SKILL.md)** | Processes and replies to WhatsApp messages. | New Message |

## How to Add a Skill
1.  Create a folder `skills/new_skill_name/`.
2.  Create `SKILL.md` with: Purpose, Trigger, Input, Steps, Output, Approval, Error Handling.
3.  Add to this README.
