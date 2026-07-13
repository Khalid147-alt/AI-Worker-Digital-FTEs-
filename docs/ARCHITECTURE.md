# Gold Tier Architecture: Personal AI Employee

## 1. System Overview

The Gold Tier AI Employee is a resilient, event-driven system designed to automate personal business operations. It follows the **Ralph Wiggum Pattern** (Autonomous Loops) and uses **MCP Servers** for external tool access.

```ascii
+-----------------------+       +-------------------------+
|      USER INPUT       |       |    EXTERNAL WORLD       |
| (Files, Tasks, Chat)  |       | (Email, WhatsApp, Web)  |
+-----------+-----------+       +------------+------------+
            |                                |
            v                                v
+-----------------------+       +-------------------------+
|     WATCHERS          |       |      MCP SERVERS        |
| (FS, LinkedIn, Email) |       | (Odoo, Social, Email)   |
+-----------+-----------+       +------------+------------+
            |                                |
            v                                v
+---------------------------------------------------------+
|                 ORCHESTRATOR (Python)                   |
|          Routes Tasks -> Agents -> Action               |
+---------------------------------------------------------+
            |             |               |
            v             v               v
+----------------+  +--------------+  +-------------------+
| RALPH LOOP     |  | AGENT SKILLS |  |  VAULT (Storage)  |
| (Autonomy)     |  | (Markdown)   |  | (Logs, Plans)     |
+----------------+  +--------------+  +-------------------+
```

## 2. Core Components

### A. Watchers & Triggers
-   **`filesystem_watcher.py`**: Monitors `/Needs_Action` for new task files.
-   **`orchestrator.py`**: The central brain. Runs every 60s to process pending tasks.
-   **`watchdog.py`**: Ensures system health and restarts crashed processes.
-   **`ceo_briefing_generator.py`**: Automated weekly reporting cron job.

### B. Agent Skills (`/Skills/*`)
Standardized capability definitions for Claude.
-   **Communication**: `email_responder`, `whatsapp_handler`, `social_media_poster`
-   **Operations**: `task_planner`, `autonomous_task`
-   **Finance**: `invoice_generator`, `ceo_briefing`, `subscription_auditor`
-   **Safety**: `audit_review`

### C. MCP Servers (`/mcp_servers/*`)
-   **`odoo_mcp`**: Accounting, Invoicing, Revenue tracking (JSON-RPC).
-   **`social_media_mcp`**: Twitter/X, Facebook, Instagram posting.
-   **`email_server`**: (External/Silver Tier) Gmail operations.

### D. The Vault (`/AI_Employee_Vault/`)
The file-based database and UI.
-   `/Needs_Action`: Incoming tasks.
-   `/Pending_Approval`: Drafts waiting for human review.
-   `/Approved`: Tasks authorized for execution.
-   `/Done`: Completed task archive.
-   `/Logs`: Audit logs and error reports.
-   `/Briefings`: Generated reports.

## 3. Data Flows

### Email Workflow
1.  **Ingest**: `email_watcher` (or similar) detects email -> creates `.md` in `/Needs_Action`.
2.  **Process**: `orchestrator` sees file -> calls `email_responder` skill.
3.  **Draft**: Agent drafts reply using Handbook rules -> saves to `/Pending_Approval/Email`.
4.  **Review**: User moves file to `/Approved`.
5.  **Send**: `orchestrator` sees approved file -> calls `email_server` to send.
6.  **Log**: Action logged to `/Logs/YYYY-MM-DD.json`.

### Autonomous Task (Ralph Loop)
1.  **Start**: Complex task dropped in `/Needs_Action`.
2.  **Routing**: Orchestrator detects complexity -> calls `run_ralph_loop(task_id)`.
3.  **Loop**:
    -   Step 1: Agent reads `SKILL.md`.
    -   Step 2: Agent creates `PLAN.md`.
    -   Step 3: Agent executes Step 1 of plan.
    -   Step 4: Agent verifies result.
    -   Repeat until `<promise>TASK_COMPLETE</promise>`.
4.  **Finish**: Orchestrator moves task to `/Done`.

## 4. Tech Stack

| Component | Technology | Purpose | Version |
|-----------|------------|---------|---------|
| **Core** | Python 3.10+ | Orchestration, Scripts | Latest |
| **Logic** | Claude Code | Intelligence, Code Gen | - |
| **Data** | Markdown/JSON | Storage, Config | - |
| **Integration** | Node.js (MCP) | Connection to SaaS | 18+ |
| **Accounting** | Odoo (Docker) | ERP, Finance | 19+ |
| **Browser** | Playwright | WhatsApp/LinkedIn Auto | Latest |

## 5. Security Model

-   **Credentials**: Stored in `.env` only. Never in code/logs.
-   **Approval**: WRITE actions (Email, Post, Pay) require file move to `/Approved` by default.
-   **Audit**: All actions logged immutably.
-   **Isolation**: Skills rely on specific inputs/outputs; no unchecked global access.
