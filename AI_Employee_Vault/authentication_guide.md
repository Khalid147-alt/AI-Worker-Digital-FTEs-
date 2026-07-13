# 🔐 Authentication Guide

For your Silver Tier AI Employee to work, you need to connect your accounts. Here is the step-by-step guide for each service.

## 1. LinkedIn & WhatsApp (One-Time Login)

These services use browser automation (Selenium/Playwright). You need to log in manually once, and the system will save your session cookies.

**Steps:**
1.  Open your terminal in `d:/Hackathon0`.
2.  Run the helper script:
    ```bash
    python start_services.py
    ```
    *(Alternatively, run `python whatsapp_watcher.py` and `python linkedin_watcher.py` in separate terminals).*

3.  **For WhatsApp**:
    -   A Chromium browser window will open loading WhatsApp Web.
    -   **Scan the QR code** with your phone (Settings > Linked Devices).
    -   Wait until you see your chat list.
    -   The script will save your session to the `whatsapp_session/` folder.

4.  **For LinkedIn**:
    -   A Chrome browser window will open loading LinkedIn.
    -   **Log in** with your username and password.
    -   Complete any 2FA verification if asked.
    -   Wait until you see your LinkedIn feed.
    -   The script will save your session to the `linkedin_session/` folder.

> [!NOTE]
> Once logged in, you don't need to do this again unless your session expires (usually weeks). The watchers will run in the background using these saved sessions.

---

## 2. Gmail (MCP Server)

Gmail is connected via the Model Context Protocol (MCP), allowing Claude to send emails directly. This requires an App Password, NOT your regular password.

**Steps:**
1.  **Generate App Password**:
    -   Go to [Google Account Security](https://myaccount.google.com/security).
    -   Ensure **2-Step Verification** is ON.
    -   Search for "**App passwords**" in the search bar at the top.
    -   Create a new app password (name it "AI Employee").
    -   **Copy the 16-character code** (e.g., `abcd efgh ijkl mnop`).

2.  **Configure Claude Code**:
    -   Locate your MCP config file. On Windows, it is usually at:
        `%APPDATA%\Claude Code\mcp.json` or `~/.config/claude-code/mcp.json`.
    -   Open it and update the `email` server section:

    ```json
    {
      "mcpServers": {
        "email": {
          "command": "node",
          "args": ["D:/Hackathon0/mcp_servers/email_server/index.js"],
          "env": {
            "GMAIL_USER": "your.email@gmail.com",
            "GMAIL_APP_PASSWORD": "your-16-char-app-password"
          }
        }
      }
    }
    ```
    *(Note: The exact format depends on your `mcp.json` structure. If inside `servers` array, use that format).*

3.  **Restart**:
    -   Restart Claude Code or the terminal session for changes to take effect.

---

## Troubleshooting

-   **Browser closes immediately**: The script might be crashing. Check the terminal for errors. Ensure you have `playwright` and `selenium` installed (`pip install playwright selenium`).
-   **Email fails to send**: Double-check your App Password. Regular passwords do NOT work.
