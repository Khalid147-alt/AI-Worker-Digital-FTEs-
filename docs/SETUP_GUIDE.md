# Setup Guide: Personal AI Employee (Gold Tier)

**Time Required**: ~45 Minutes
**Prerequisites**: Python 3.10+, Node.js 18+, Docker (for Odoo)

## 1. Environment Setup
1.  **Clone Repository**: `git clone <repo>`
2.  **Install Python Deps**: `pip install -r requirements.txt` (schedule, watchdog, playwright, requests)
3.  **Install Node Deps**: `npm install` (in mcp_servers directories)
4.  **Configure `.env`**:
    ```bash
    VAULT_PATH=./AI_Employee_Vault
    ODOO_URL=http://localhost:8069
    ODOO_DB=mydb
    ODOO_USER=admin
    ODOO_PASSWORD=admin
    ```

## 2. Infrastructure Launch
1.  **Start Odoo**:
    ```bash
    docker run -d -p 8069:8069 --name odoo --env POSTGRES_PASSWORD=mysecretpassword odoo:16
    ```
2.  **Initialize Vault**:
    Run `python scripts/init_vault.py` (if available) or manually creating folders:
    `mkdir AI_Employee_Vault/{Needs_Action,Pending_Approval,Approved,Done,Logs,Briefings}`

## 3. Start the System
1.  **Run Watchdog** (This starts everything else):
    ```bash
    python scripts/watchdog.py
    ```
2.  **Verify**: Check `AI_Employee_Vault/Logs/system_health.md`. You should see green lights.

## 4. Testing
1.  **Simple Test**: Create a file in `/Needs_Action` called `hello.md` with content "Say hi".
2.  **Wait**: 60 seconds.
3.  **Check**: Look in `/Pending_Approval` or `/Done`.

## 5. Troubleshooting
-   **Logs**: Check `/Logs/errors_YYYY-MM-DD.log`.
-   **Health**: Check `http://localhost:8765/health`.
-   **Recovery**: If stuck, delete the `_processing` files in `/Needs_Action`.
