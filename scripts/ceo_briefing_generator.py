import sys
from pathlib import Path
from datetime import datetime, timedelta

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from config import get_runtime_paths

VAULT_PATH, _ = get_runtime_paths()
DONE_DIR = VAULT_PATH / 'Done'
NEEDS_ACTION = VAULT_PATH / 'Needs_Action'
TEMPLATE_PATH = VAULT_PATH / 'Briefings' / 'Briefing_Template.md'

def analyze_completed_tasks(days=7):
    """Analyze tasks in /Done from the last N days"""
    cutoff_date = datetime.now() - timedelta(days=days)
    tasks = []
    bottlenecks = []
    
    if not DONE_DIR.exists(): return [], []

    for file_path in DONE_DIR.glob('*.md'):
        try:
            # Check modification time first for speed
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if mtime < cutoff_date:
                continue
                
            content = file_path.read_text(encoding='utf-8', errors='replace')
            
            # Simple bottleneck detection: Look for "est_hours" vs actual, or just long processing
            # For prototype, we'll mark any file > 5KB as "complex/potential bottleneck" 
            # or if filename contains "DELAY" or "ERROR".
            
            task_info = {
                'name': file_path.name,
                'date': mtime.isoformat()
            }
            tasks.append(task_info)
            
            if 'DELAY' in file_path.name or 'ERROR' in content:
                bottlenecks.append(file_path.name)
                
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            
    return tasks, bottlenecks

def generate_task():
    print("Analyzing tasks...")
    tasks, bottlenecks = analyze_completed_tasks()
    
    print(f"Found {len(tasks)} tasks and {len(bottlenecks)} bottlenecks.")
    
    # Create the Prompt for Claude
    today = datetime.now().strftime('%Y-%m-%d')
    
    task_description = f"""
# Task: Generate CEO Briefing for {today}

## Context Data (Pre-calculated)
- **Reporting Period**: Last 7 Days
- **Completed Tasks Count**: {len(tasks)}
- **Identified Bottlenecks**:
{chr(10).join(['  - ' + b for b in bottlenecks]) if bottlenecks else '  - None detected'}

## Instructions
1. Use the `ceo_briefing` skill.
2. Call Odoo to get Revenue for the current month.
3. Read `Business_Goals.md` to compare against targets.
4. Draft the briefing using `Briefings/Briefing_Template.md`.
5. Save it to `Briefings/{today}_Monday_Briefing.md`.
6. Update `Dashboard.md` with the new metrics.
"""

    # Write to Needs_Action to trigger Orchestrator
    filename = f"GENERATE_BRIEFING_{today}.md"
    file_path = NEEDS_ACTION / filename
    
    metadata = f"""---
type: system_task
status: pending
priority: high
created_at: {datetime.now().isoformat()}
---
{task_description}
"""
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(metadata)
        
    print(f"Created task: {file_path}")

if __name__ == "__main__":
    generate_task()
