# Error Playbook & Recovery Guide

## 1. Playbook Overview
This document defines how the Gold Tier AI Employee handles failures. 
**Philosophy**: "Fail loud, fail safe, keep running."

## 2. Error Categories

| Error Type | Definition | Automatic Action | Manual Recovery |
|------------|------------|------------------|-----------------|
| **TransientError** | Network glitches, timeouts (503, 504) | Retry with exponential backoff (up to 5x) | Check internet connection |
| **AuthError** | Expired tokens, 401/403 | Attempt token refresh (if implemented) -> Alert | Update `.env` or re-login |
| **LogicError** | Python exceptions, bugs | Log stack trace -> Watchdog restarts process | Fix code |
| **DataError** | Malformed JSON/Files | Move file to `/Rejected` -> Log error | Fix input file format |

## 3. Graceful Degradation Rules

### Gmail / Email Server Down
- **Detection**: `ConnectionRefused` or `Timeout` on SMTP/IMAP.
- **Auto-Action**: 
    1. Stop attempting to connect.
    2. Queue generated emails in `/Outbox_Queue/`.
    3. `watchdog` retries connection every 10 mins.
- **Impact**: Emails will be delayed but not lost.

### WhatsApp (Playwright) Usage
- **Detection**: Selector not found, Browser crash, Session invalid.
- **Auto-Action**:
    1. Restart Browser (max 3 times).
    2. If fails, create `SYSTEM_ALERT_WHATSAPP.md` in Inbox.
- **Impact**: No replies sent. Requires QR Scan.

### Odoo / Accounting
- **Detection**: JSON-RPC Error.
- **Auto-Action**: 
    1. Mark financial data as "ESTIMATED (OFFLINE)" in Dashboard.
    2. Skip billing generation tasks.

## 4. Watchdog System
The `scripts/watchdog.py` runs permanently.
- **Checks**: Every 30 seconds.
- **Monitors**: `orchestrator.py`, `filesystem_watcher.py`, `linkedin_watcher.py`.
- **Dashboard**: Updates "System Health" section every 5 mins.

## 5. Escalation
If a component crashes >5 times in 1 hour:
1.  **STOP** the component (prevent infinite loops).
2.  **ALERT** by creating `URGENT_HELP_NEEDED.md` in `/Needs_Action`.
