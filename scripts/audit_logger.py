import json
import logging
import os
import glob
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
VAULT_PATH = Path(os.getenv('VAULT_PATH', 'D:/Hackathon0/AI_Employee_Vault'))
LOGS_DIR = VAULT_PATH / 'Logs'
RETENTION_DAYS = 90

class AuditLogger:
    def __init__(self, component_name):
        self.component_name = component_name
        self.logs_dir = LOGS_DIR
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        # Ensure retention policy is enforced on init (could be done via cron too)
        self.purge_old_logs()

    def _get_log_file(self):
        date_str = datetime.now().strftime('%Y-%m-%d')
        return self.logs_dir / f'{date_str}.json'

    def log_action(self, action_type, target, parameters=None, status="success", result=None):
        """
        Log an accountable action.
        
        Args:
            action_type (str): e.g., 'file_move', 'email_send'
            target (str): The object acting upon (filename, email address)
            parameters (dict, optional): Details (destination path, subject line)
            status (str): 'success', 'pending_approval', 'failure'
            result (str, optional): Outcome details
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "actor": self.component_name,
            "target": target,
            "parameters": parameters or {},
            "status": status,
            "result": result
        }

        log_file = self._get_log_file()
        try:
            # Append JSON object (using JSON Lines format for appendability)
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            print(f"CRITICAL: Failed to write audit log: {e}")

    def purge_old_logs(self):
        cutoff = datetime.now() - timedelta(days=RETENTION_DAYS)
        for log_file in self.logs_dir.glob('????-??-??.json'):
            try:
                # Parse filename date
                file_date_str = log_file.stem
                file_date = datetime.strptime(file_date_str, '%Y-%m-%d')
                if file_date < cutoff:
                    log_file.unlink()
                    print(f"Purged old log: {log_file.name}")
            except Exception:
                pass

    def get_actions(self, date_from=None, date_to=None, action_type=None, actor=None):
        """Query logs"""
        results = []
        # Basic implementation: read all relevant files. 
        # For production, this should be indexed or DB-backed.
        
        # Determine file range logic (omitted for brevity, just reading all JSONs)
        log_files = sorted(self.logs_dir.glob('????-??-??.json'))
        
        for log_file in log_files:
            # Simple date filtering on filename could optimize this
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        entry_date = datetime.fromisoformat(entry['timestamp'])
                        
                        if date_from and entry_date < date_from: continue
                        if date_to and entry_date > date_to: continue
                        if action_type and entry['action_type'] != action_type: continue
                        if actor and entry['actor'] != actor: continue
                        
                        results.append(entry)
                    except: continue
        return results

# Singleton helper
_global_logger = None
def get_audit_logger(component_name):
    # Just return a new instance, overhead is low
    return AuditLogger(component_name)
