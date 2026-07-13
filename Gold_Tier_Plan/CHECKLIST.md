# Gold Tier Implementation Checklist

## Phase 1: Foundation & Infrastructure
- [ ] Create `config_gold.py` (Centralized config management)
- [ ] Create `logger_gold.py` (Structured JSON logging)
- [ ] Create `state_manager.py` (Persistence via lightweight DB/JSON)
- [ ] Setup `requirements_gold.txt` (New dependencies: `streamlit`, `asyncio`, etc.)

## Phase 2: The Core Rewrite
- [ ] Refactor `filesystem_watcher.py` into a Class `FileSensor`
- [ ] Create `gold_orchestrator.py` (Async implementation using `asyncio`)
- [ ] Implement `check_health()` logic in orchestrator (Monitoring watchers)

## Phase 3: Integrating Watchers (Sensors)
- [ ] Integrate `EmailWatcher` (Gmail API) into the new Orchestrator
- [ ] Integrate `WhatsAppWatcher` (Playwright) with improved error handling/restart logic
- [ ] Create `check_calendar_skill.py` (New Calendar integration)
- [ ] Create `web_monitor_skill.py` (New URL monitoring capability)

## Phase 4: Intelligence & Skills
- [ ] Create `memory_manager.py` (Indexing `Done` folder for context retrieval)
- [ ] Implement `research_skill.py` (Web Search capabilities)
- [ ] Update `process_task` prompts to use 'Confidence Scores' for approval logic

## Phase 5: The Interface (Dashboard)
- [ ] Create `dashboard_app.py` (Streamlit UI)
    - [ ] Tab 1: Current Status & Logs
    - [ ] Tab 2: Needs Approval (One-click approve/reject)
    - [ ] Tab 3: Configuration
- [ ] Run end-to-end test flow
    - [ ] Drop file -> Process -> Dashboard -> Approve -> Done

## Phase 6: Documentation & Handover
- [ ] Update `README_GOLD.md` with setup instructions
- [ ] Create `TROUBLESHOOTING.md` for common issues
- [ ] Finalize `Business_Goals.md` (Currently MISSING)
