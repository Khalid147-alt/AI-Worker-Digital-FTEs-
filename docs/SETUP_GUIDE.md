# Setup Guide: Personal AI Employee

**Time Required**: ~45 Minutes
**Prerequisites**: Python 3.10+, Node.js 18+, Docker (for Odoo)

## 1. Environment Setup
1.  **Clone Repository**: `git clone <repo>`
2.  **Install Python Deps**: `pip install -r requirements.txt`
3.  **Install Node Deps**: `npm install` in the MCP server directories that need them.
4.  **Configure `.env`** by copying `.env.example` and setting the required runtime variables:

    VAULT_PATH=./AI_Employee_Vault
    SCRIPTS_DIR=./scripts
    WORKER_ID=orchestrator
    MAX_RALPH_WORKERS=3
    CLAUDE_TIMEOUT_SECONDS=300

## 2. Bootstrap and Validation
1.  **Validate the scheduler regression**:
    `python -m pytest -q tests/test_orchestrator.py`
2.  **Initialize the vault directories** if they are missing:
    `mkdir -p AI_Employee_Vault/{Needs_Action,Approved,In_Progress,Done,Blocked,Logs,Briefings}`

## 3. Start the System
1.  **Run Watchdog** (this starts the orchestrator and related service workers):
    `python scripts/watchdog.py`
2.  **Verify**: check the health endpoint at `http://localhost:8765/health`.

## 4. Runtime Expectations
-   `orchestrator.py` now claims tasks into the in-progress folder before it dispatches the Ralph loop.
-   Missing Claude CLI or missing Ralph loop assets should raise a startup or task-block failure instead of being silently marked as success.
-   Audit log activity is written into the vault logs directory for accountability.

## 5. Troubleshooting
-   **Logs**: inspect `AI_Employee_Vault/Logs`.
-   **Startup failure**: confirm that `.env` contains `VAULT_PATH` and `SCRIPTS_DIR` and that the referenced paths exist.
-   **Blocked tasks**: inspect `AI_Employee_Vault/Blocked` for tasks that failed due to prerequisites or runtime errors.
