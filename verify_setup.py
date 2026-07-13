import os
from pathlib import Path

def verify_structure():
    vault_path = Path('AI_Employee_Vault')
    required_dirs = [
        'Pending_Approval',
        'Approved',
        'Rejected',
        'Plans',
        'Social_Media/LinkedIn_Queue',
        'Social_Media/Posted',
        'Templates',
        'Skills/draft_email_reply',
        'Skills/post_to_linkedin',
        'Skills/create_weekly_plan'
    ]
    
    required_files = [
        'Templates/email_reply_template.md',
        'Templates/linkedin_post_template.md',
        'Skills/draft_email_reply/SKILL.md',
        'Skills/post_to_linkedin/SKILL.md',
        '../whatsapp_watcher.py',
        '../linkedin_watcher.py',
        '../orchestrator.py',
        '../mcp_servers/email_server/index.js',
        'mcp_config_guide.md'
    ]
    
    missing = []
    
    print("Verifying directories...")
    for d in required_dirs:
        path = vault_path / d
        if not path.exists():
            print(f"[MISSING DIR] {path}")
            missing.append(str(path))
        else:
            print(f"[OK] {path}")
            
    print("\nVerifying files...")
    for f in required_files:
        path = vault_path / f
        if not path.exists():
            print(f"[MISSING FILE] {path}")
            missing.append(str(path))
        else:
            print(f"[OK] {path}")
            
    if missing:
        print(f"\nFAILED: {len(missing)} items missing.")
    else:
        print("\nSUCCESS: All Silver Tier structure verified.")

if __name__ == "__main__":
    verify_structure()
