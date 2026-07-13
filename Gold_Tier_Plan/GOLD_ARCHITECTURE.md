# Gold Tier Architecture Upgrade Plan

## 1. Executive Summary
The Move from Silver to Gold Tier represents a shift from "Automated Scripts" to a "Resilient, Semi-Autonomous System".
- **Silver Check**: Basic watchers, file-based triggers, simple linear execution.
- **Gold Goal**: Event-driven architecture, structured state management (beyond just files), rich feedback loops, and a visual dashboard.

## 2. System Architecture

### A. The Core (Orchestrator 2.0)
- **Current**: `orchestrator.py` runs a simple `schedule` loop.
- **Upgrade**: `gold_orchestrator.py`
    - **AsyncIO based**: Handle multiple watchers concurrently without blocking.
    - **State Management**: `state.json` or SQLite key-value store to track task IDs, retries, and failure reasons.
    - **Error Recovery**: Automatic restart of watchers if they crash (e.g., Playwright disconnects).

### B. The Memory (Enhanced Vault)
- **Current**: Folder structure (`Needs_Action`, `Done`).
- **Upgrade**:
    - **Context Store**: `knowledge_graph.json` to link people, projects, and tasks.
    - **Semantic Search**: Ability to query past tasks by meaning, not just filename.

### C. The Senses (Inputs)
1.  **Universal Watcher**: Unified class for File, Email, and Message watchers.
2.  **New Sensors**:
    - **Calendar Watcher**: Checks upcoming meetings to prepare briefing notes automatically.
    - **Web Monitor**: Watches specific URLs for changes (competitor pricing, news).

### D. The Hands (Outputs)
- **Smart Approval**: Instead of blocking on *everything*, calculate a "Confidence Score".
    - Score > 90%: Auto-execute (e.g., file filing).
    - Score < 90%: Ask for approval.
- **Interactive UI**: A simple Streamlit or Flask dashboard to approve tasks with one click, rather than moving markdown files.

## 3. Component List & Implementation Order

### Phase 1: Foundation (Dependencies: None)
1.  **`config_gold.py`**: Centralized configuration (API keys, paths, thresholds).
2.  **`logger_gold.py`**: Structured logging (JSON logs) for better debugging.
3.  **`state_manager.py`**: Class to handle persistent state (completed tasks DB).

### Phase 2: Core Upgrade (Dependencies: Phase 1)
4.  **`gold_orchestrator.py`**: The new main loop.
    - Needs to import `filesystem_watcher` and wrap it in a non-blocking way.
5.  **`input_handlers/`**: Refactor existing watchers into classes inheriting from a `BaseWatcher`.

### Phase 3: Intelligence (Dependencies: Phase 2)
6.  **`skills/calendar_skill.py`**: Google Calendar integration.
7.  **`skills/research_skill.py`**: Tavily/Perplexity API wrapper for deep research.
8.  **`memory_manager.py`**: Script to index `Done` folder into a vector store (or simple keyword index).

### Phase 4: Interface (Dependencies: Phase 3)
9.  **`dashboard_app.py`**: Streamlit app for real-time monitoring and "Click to Approve".

## 4. Estimates & Risks

| Component | Est. Hours | Risk Level | Mitigation |
|-----------|------------|------------|------------|
| Core Refactor | 4h | Med | Keep Silver running in parallel until Gold is stable. |
| Calendar Integration | 2h | Low | specific API permissions needed. |
| Knowledge Index | 3h | High | Complexity of RAG; start with simple keyword search. |
| Dashboard UI | 3h | Low | Use Streamlit for rapid dev. |

**Total Estimated Time**: ~12-15 Hours

## 5. Risk Areas
1.  **Playwright Stability**: WhatsApp web sessions often expire or get disconnected.
    - *Fix*: Implement a "Health Check" loop that restarts the browser instantiation on failure.
2.  **API Costs**: Autonomous loops can spiral.
    - *Fix*: Strict daily budget limits in `config_gold.py`.
3.  **Data Corruption**: If `state.json` corrupts, context is lost.
    - *Fix*: Atomic writes and daily backups of the Vault.
