# 🧠 What is this App?

## 1. What problem does it solve?
You have too many tasks (documents to read, emails to draft, plans to make) and not enough time. Usually, you have to do them all manually or paste them into ChatGPT one by one.
**This app gives you a "Digital Employee"** that lives on your computer. It can:
- 📂 **Monitor a folder** for work (like an Inbox tray).
- 🧠 **Think autonomously** about what needs to be done.
- 📝 **Create plans** and **Draft content** for you.
- 🔒 **Keep everything private** on your own hard drive (in the `AI_Employee_Vault`).

## 2. How does it work?
It connects three things:
1.  **The Watcher** (`filesystem_watcher.py`): A script that never sleeps. It watches the `Drop_Folder` like a hawk. When a file lands there, it grabs it.
2.  **The Memory** (`AI_Employee_Vault`): A structured set of folders (`Inbox`, `Needs_Action`, `Done`) that organizes your work, just like a real office filing system.
3.  **The Brain** (Claude Code): The AI intelligence that reads the files in `Needs_Action`, follows the instructions in `Skills/`, and updates your `Dashboard.md`.

## 3. How do I use it?
It's a simple 3-step loop:

### Step 1: Delegate (The Drop)
Drag and drop **any file** (PDF, text, image) into the `Drop_Folder`.
*Example: Drop a PDF request from a client.*

### Step 2: Automation (The Watcher)
The watcher automatically moves it to `AI_Employee_Vault/Needs_Action` and prepares it for the AI.
*(You don't do anything here, it just happens)*

### Step 3: Execution (The AI)
Run the AI command (or ask me to do it). The AI will:
- Read the file.
- Create a **Plan** in a new `.md` file.
- Update your **Dashboard**.
- If you ask it to `execute`, it will actually **do the work** (write the email, summary, etc.).

## 🔎 Where do I look?
- **Dashboard.md**: Your daily status report.
- **Needs_Action/**: See the work the AI is doing.
