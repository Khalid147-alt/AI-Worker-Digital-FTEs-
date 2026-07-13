# Email MCP Server Configuration Guide

To enable the Email MCP server in Claude Code, follow these steps:

## 1. Prerequisites
- **Node.js**: Ensure Node.js is installed.
- **Gmail Account**: You need a Gmail account.
- **App Password**: You MUST generate an App Password for Gmail.
    1. Go to [Google Account Security](https://myaccount.google.com/security).
    2. Enable 2-Step Verification if not already enabled.
    3. Search for "App passwords".
    4. Create a new app password (name it "Claude MCP").
    5. Copy the 16-character password.

## 2. Configure Claude Code
You need to add the server configuration to your Claude Code config file.

**File Path:** `~/.config/claude-code/mcp.json` (or `%APPDATA%\claude-code\mcp.json` on Windows)

**Configuration to Add:**
```json
{
  "servers": [
    {
      "name": "email",
      "command": "node",
      "args": ["D:/Hackathon0/mcp_servers/email_server/index.js"],
      "env": {
        "GMAIL_USER": "your-email@gmail.com",
        "GMAIL_APP_PASSWORD": "your-16-char-app-password"
      }
    }
  ]
}
```

> [!IMPORTANT]
> Replace `your-email@gmail.com` and `your-16-char-app-password` with your actual credentials.
> Ensure the path `D:/Hackathon0/mcp_servers/email_server/index.js` is correct.

## 3. Verify
After saving the config file, restart Claude Code. You should see the `email` tool available.
