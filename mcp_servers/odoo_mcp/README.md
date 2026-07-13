# Odoo MCP Server

This MCP server connects Claude Code to a local Odoo Community instance via JSON-RPC.

## Prerequisites
- Node.js installed.
- Odoo 19 (or compatible) running locally.
- Docker is recommended for running Odoo.

## 1. Install & Run Odoo (Docker)

If you don't have Odoo installed, running it via Docker is the easiest way.

```bash
# Pull the latest Odoo image
docker pull odoo:latest

# Run Odoo with a PostgreSQL database
docker run -d -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD=odoo -e POSTGRES_DB=postgres --name db postgres:15
docker run -p 8069:8069 --name odoo --link db:db -t odoo:latest
```

Open [http://localhost:8069](http://localhost:8069) in your browser.
1.  **Create a database**:
    -   Master Password: (remember this!)
    -   Database Name: `odoo`
    -   Email: `admin`
    -   Password: `admin`
    -   **Check "Demo data"** (Useful for testing)

2.  **Install Accounting**:
    -   Go to **Apps**.
    -   Search for "Invoicing" (Community Edition doesn't have full "Accounting" by default, checking "Invoicing" is sufficient for basic AP/AR).
    -   Click **Activate**.

## 2. Configuration (`.env`)

Create a `.env` file in this directory:

```env
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USER=admin
ODOO_PASSWORD=admin
DRY_RUN=true  # Set to false to actually write data
```

## 3. Testing
You can test the server using `node index.js`, but since it uses Stdio transport, it won't output much to the console directly unless you use an MCP inspector.

To verify basic connectivity, you can modify `index.js` temporarily or create a test script.

## 4. Claude Code Config
Add this to your `mcp.json`:

```json
{
  "odoo": {
    "command": "node",
    "args": ["D:/Hackathon0/mcp_servers/odoo_mcp/index.js"],
    "env": {
      "ODOO_URL": "http://localhost:8069",
      "ODOO_DB": "odoo",
      "ODOO_USER": "admin",
      "ODOO_PASSWORD": "admin"
    }
  }
}
```
