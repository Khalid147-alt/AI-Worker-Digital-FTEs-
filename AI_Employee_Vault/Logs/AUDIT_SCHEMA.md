# Audit Log Schema

All AI actions are logged to `/Logs/YYYY-MM-DD.json` in JSON Lines format.

## Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | ISO8601 String | When the action occurred. |
| `action_type` | String | Category of action (see Allowed Types). |
| `actor` | String | Component name (e.g., `orchestrator`, `gmail_watcher`). |
| `target` | String | The object being acted upon (e.g., `invoice_123.pdf`, `client@co.com`). |
| `parameters` | Object | Contextual details (destination, amount, subject). |
| `status` | String | `success`, `failure`, `pending_approval`. |
| `result` | String | Outcome or error message. |

## Allowed Action Types

### Files
- `file_create`: Creating a new document.
- `file_move`: Moving a task (e.g., Pending -> Done).
- `file_delete`: Removing a file (rare, usually forbidden).

### Communications
- `email_read`: Processing an incoming email.
- `email_draft`: Creating a draft response.
- `email_send`: Sending an email (requires approval log).
- `whatsapp_read`: Parsing a message.
- `whatsapp_send`: Sending a reply.
- `social_post`: Posting to LinkedIn/Twitter.

### Finance (Golden Tier)
- `payment_initiated`: Creating a payment request.
- `odoo_query`: Reading financial data.
- `odoo_write`: Creating invoice/journal entry.

### System
- `claude_reasoning`: Major decision point by the AI.
- `system_alert`: Watchdog alert triggered.

## Retention Policy
Logs are retained for **90 Days** and then securely purged.
