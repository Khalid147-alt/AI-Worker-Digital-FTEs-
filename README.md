# Personal AI Employee

## Production Hardening Status
This repository is now configured for portable, env-driven runtime operation and has a verified regression test for the orchestrator claim-before-run path.

## What changed
-   **Claim-first scheduling**: the orchestrator now claims a task file into the in-progress workspace before launching the Ralph loop.
-   **Bounded worker execution**: background work is tracked separately so the scheduler stays responsive and does not race file ownership.
-   **Hard failure on missing prerequisites**: if the Claude CLI or required scripts are missing, the runtime blocks the task instead of silently reporting success.
-   **Config bootstrap cleanup**: runtime paths are resolved from the repository environment file instead of hardcoded machine-specific paths.

## Verified evidence
-   Regression test: `tests/test_orchestrator.py`
-   Command used: `python -m pytest -q tests/test_orchestrator.py`
-   Result: `2 passed in 0.10s`

## 📚 Documentation
-   **[Architecture](docs/ARCHITECTURE.md)**: System design and data flows.
-   **[Setup Guide](docs/SETUP_GUIDE.md)**: How to run this locally.
-   **[Production Readiness](docs/PRODUCTION_READINESS.md)**: Current verified production-hardening state.
-   **[Lessons Learned](docs/LESSONS_LEARNED.md)**: Technical challenges and solutions.
-   **[Skills Index](AI_Employee_Vault/Skills/README.md)**: The AI's job descriptions.

## 🚀 Quick Start
1.  Copy `.env.example` to `.env` and set `VAULT_PATH` and `SCRIPTS_DIR`.
2.  Install dependencies: `pip install -r requirements.txt`
3.  Run the regression validation: `python -m pytest -q tests/test_orchestrator.py`
4.  Launch the services: `python scripts/watchdog.py`

## 📁 Repository Structure
-   `/mcp_servers`: Node.js integrations (Odoo, Social).
-   `/scripts`: Python core (orchestrator, watchdog, loop, audit utilities).
-   `/AI_Employee_Vault`: The file-based work queue, logs, and skills.
-   `/docs`: System documentation and operational notes.

---
Production hardening is now verified by regression tests and env-driven startup behavior.
