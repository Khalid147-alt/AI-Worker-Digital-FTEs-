# Demo Script: Gold Tier AI Employee

**Duration**: 10 Minutes
**Goal**: Showcase autonomy, diverse integration (Odoo/Social), and reliability.

---

## 0:00 - 1:00: Introduction & Architecture
-   **Visual**: Show `docs/ARCHITECTURE.md` diagram.
-   **Voiceover**: "Welcome to the Gold Tier AI Employee. This isn't just a chatbot; it's a fully autonomous system that manages my email, social media, and accounting."
-   **Highlight**: Point out the Vault, Orchestrator, and Odoo MCP.

## 1:00 - 3:00: Automation Demo (Email)
-   **Action**: Drag a file `TEST_CLIENT_REQUEST.md` into `/Needs_Action`.
-   **Visual**: Split screen. Left: Folder view. Right: Orchestrator logs.
-   **Voiceover**: "I just received a client request. The watcher detects it instantly."
-   **Visual**: See `email_responder` skill activate. See file appear in `/Pending_Approval`.
-   **Action**: Move file to `/Approved`.
-   **Visual**: File moves to `/Done`. Log shows "Email Sent".

## 3:00 - 5:00: Social Media Workflow
-   **Action**: Show `Business_Goals.md` containing "Launch Gold Tier".
-   **Action**: Trigger `social_media_poster` skill (or wait for sched).
-   **Visual**: Agent drafts a tweet and LinkedIn post in `/Pending_Approval/Social/`.
-   **Voiceover**: "It knows my business goals and drafts relevant content. I just review and approve."

## 5:00 - 7:00: CEO Briefing (The "Gold" Feature)
-   **Action**: Run `python scripts/ceo_briefing_generator.py`.
-   **Visual**: Show the Odoo MCP logging revenue queries.
-   **Visual**: Open the generated PDF/Markdown Briefing.
-   **Voiceover**: "Every Monday, it queries my ERP, checks my tasks, and writes this executive summary. It even found an unused subscription here."

## 7:00 - 9:00: Ralph Wiggum Loop (Autonomy)
-   **Action**: Drop a complex task: "Plan and setup a new marketing campaign for February".
-   **Visual**: Watch `Plans/MARKETING_PLAN.md` get created and checked off line-by-line.
-   **Voiceover**: "For complex tasks, it enters the Ralph Loop. It plans, executes, verifies, and iterates until the job is done—without me holding its hand."

## 9:00 - 10:00: Resilience & Conclusion
-   **Action**: Manually kill the `orchestrator` process.
-   **Visual**: Watchdog log shows "CRASH DETECTED". Restarting in 3... 2... 1...
-   **Voiceover**: "And if something breaks? The self-healing watchdog fixes it. This is the Personal AI Employee: Autonomous, Resilient, and Capable."
