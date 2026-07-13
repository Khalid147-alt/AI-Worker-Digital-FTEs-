# ACTION REQUIRED: Odoo Setup

To enable your Gold Tier Accounting System, you need to set up Odoo locally.

## Step 1: Install Docker Desktop
If you haven't already, install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/).

## Step 2: Run Odoo
Open PowerShell and run these commands to start Odoo and its database:

```powershell
# 1. Start the Database
docker run -d -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD=odoo -e POSTGRES_DB=postgres --name db postgres:15

# 2. Start Odoo (Linking to DB)
docker run -p 8069:8069 --name odoo --link db:db -t odoo:latest
```

## Step 3: Initialize Database
1.  Go to [http://localhost:8069](http://localhost:8069).
2.  Fill in the setup form:
    -   **Master Password**: `admin` (or choose your own, but remember it!)
    -   **Database Name**: `odoo`
    -   **Email**: `admin`
    -   **Password**: `admin`
    -   **Demo Data**: [x] Check this box so you have data to play with.
3.  Click **Create Database**.

## Step 4: Install Invoicing App
1.  Once logged in, you will see a list of Apps.
2.  Search for **Invoicing**.
3.  Click the **Activate** button.
4.  Wait for it to install.

## Step 5: Verify
Once installed, try to create a dummy invoice manually in the web UI.

## Step 6: Notify Me
Once you have done this, tell me "Odoo is ready" and I will enable the MCP server connection in Claude Code.
