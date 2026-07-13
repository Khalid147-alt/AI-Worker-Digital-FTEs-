# Personal AI Employee (Gold Tier)

## 🏆 Project Status: GOLD TIER (Complete)
A fully autonomous, self-healing, and accountable AI Employee system.

**[Watch the Demo](docs/DEMO_SCRIPT.md)**

## 🌟 Key Features
-   **Autonomous Loops**: Uses the **Ralph Wiggum Pattern** to execute multi-step tasks without hand-holding.
-   **Full Integration**: Connects to **Odoo ERP** (Accounting) and **SaaS Platforms** (Twitter/LinkedIn) via MCP.
-   **Resilience**: Self-healing process management with `watchdog.py`.
-   **Accountability**: Immutable audit logs with 90-day retention.
-   **Reporting**: Automated weekly CEO Briefings.

## 📚 Documentation
-   **[Architecture](docs/ARCHITECTURE.md)**: System design and data flows.
-   **[Setup Guide](docs/SETUP_GUIDE.md)**: How to run this locally.
-   **[Lessons Learned](docs/LESSONS_LEARNED.md)**: Technical challenges and solutions.
-   **[Skills Index](AI_Employee_Vault/Skills/README.md)**: The AI's job descriptions.

## 🚀 Quick Start
1.  **Clone**: `git clone <repo>`
2.  **Install**: `pip install -r requirements.txt`
3.  **Run**: `python scripts/watchdog.py`

## 📁 Repository Structure
-   `/mcp_servers`: Node.js integrations (Odoo, Social).
-   `/scripts`: Python core (Orchestrator, Watchdog, Loops).
-   `/AI_Employee_Vault`: The "Brain" (Tasks, Logs, Skills).
-   `/docs`: System documentation.

---
**Built with Claude Code** | Gold Tier Hackathon Submission
