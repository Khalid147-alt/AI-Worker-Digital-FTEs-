import os
import sys
import ast
from pathlib import Path

# Configuration
VAULT_PATH = Path('D:/Hackathon0/AI_Employee_Vault')
ROOT_PATH = Path('D:/Hackathon0')
DOCS_PATH = ROOT_PATH / 'docs'

results = []

def check(name, condition, error_msg):
    if condition:
        results.append(f"- [x] **{name}**: PASSED")
        return True
    else:
        results.append(f"- [ ] **{name}**: FAILED - {error_msg}")
        return False

def check_file(path, description):
    p = Path(path)
    return check(f"File Existence: {description}", p.exists(), f"File not found: {path}")

def check_content(path, string, description):
    p = Path(path)
    if not p.exists():
        return check(f"Content Check: {description}", False, f"File not found: {path}")
    
    try:
        content = p.read_text(encoding='utf-8', errors='ignore')
        return check(f"Content Check: {description}", string in content, f"String '{string}' not found in {path}")
    except Exception as e:
        return check(f"Content Check: {description}", False, f"Error reading file: {e}")

def syntax_check_python(path):
    p = Path(path)
    if not p.exists(): return False
    try:
        ast.parse(p.read_text(encoding='utf-8', errors='ignore'))
        return check(f"Syntax Check: {p.name}", True, "")
    except Exception as e:
        return check(f"Syntax Check: {p.name}", False, f"Syntax Error: {e}")

def run_qa():
    print("Starting Gold Tier QA...")
    
    # 1. Structure
    check_file(ROOT_PATH / 'mcp_servers/odoo_mcp/index.js', "Odoo MCP Server")
    check_file(ROOT_PATH / 'mcp_servers/social_media_mcp/index.js', "Social Media MCP Server")
    
    # 2. Scripts
    scripts = ['orchestrator.py', 'filesystem_watcher.py', 'linkedin_watcher.py', 
              'scripts/ralph_loop.py', 'scripts/ceo_briefing_generator.py', 
              'scripts/watchdog.py', 'scripts/audit_logger.py', 'scripts/retry_handler.py']
    
    for s in scripts:
        check_file(ROOT_PATH / s, s)
        syntax_check_python(ROOT_PATH / s)

    # 3. Skills
    skills = ['email_responder', 'whatsapp_handler', 'task_planner', 'invoice_generator',
             'social_media_poster', 'ceo_briefing', 'subscription_auditor', 
             'autonomous_task', 'audit_review']
             
    for skill in skills:
        check_file(VAULT_PATH / f'Skills/{skill}/SKILL.md', f"Skill: {skill}")

    # 4. Integration Checks
    check_content(ROOT_PATH / 'orchestrator.py', 'ralph_loop', "Orchestrator calls Ralph Loop")
    check_content(ROOT_PATH / 'scripts/ralph_loop.py', 'audit_logger', "Ralph Loop uses Audit Logger")
    check_content(ROOT_PATH / 'filesystem_watcher.py', 'audit_logger', "FS Watcher uses Audit Logger")
    
    # 5. Docs
    docs = ['ARCHITECTURE.md', 'LESSONS_LEARNED.md', 'DEMO_SCRIPT.md', 'SETUP_GUIDE.md']
    for d in docs:
        check_file(DOCS_PATH / d, f"Doc: {d}")

    # 6. Config
    check_file(ROOT_PATH / 'README.md', "Root README")
    check_file(VAULT_PATH / 'Company_Handbook.md', "Company Handbook")
    check_content(VAULT_PATH / 'Company_Handbook.md', 'Skills & Capabilities', "Handbook references Skills")

    # Output Results
    output = "# Gold Tier QA Results\n\n" + "\n".join(results)
    print(output)
    
    # Save to file
    (DOCS_PATH / 'QA_RESULTS.md').write_text(output, encoding='utf-8')
    print(f"\nQA Results saved to {DOCS_PATH / 'QA_RESULTS.md'}")

if __name__ == "__main__":
    run_qa()
