from pathlib import Path
import os
import json
import logging
import tempfile
from datetime import datetime

from config import get_runtime_paths

VAULT_PATH, _ = get_runtime_paths()
DASHBOARD_PATH = VAULT_PATH / 'Dashboard.md'
INBOX_PATH = VAULT_PATH / 'Inbox'
TEMP_DIR = Path(tempfile.gettempdir())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('DegradationManager')

class DegradationManager:
    def __init__(self, component_name):
        self.component_name = component_name
        self.health_file = VAULT_PATH / 'Logs' / f'health_{component_name}.json'
        # Ensure Logs dir exists (might be redundant if retry_handler also checks, but safe)
        (VAULT_PATH / 'Logs').mkdir(parents=True, exist_ok=True)

    def report_failure(self, error_type, details):
        """Report a failure and trigger degradation if needed"""
        logger.warning(f"Reporting failure for {self.component_name}: {error_type}")
        
        # 1. Log to health file
        self._update_health_status(status="degraded", error=details)
        
        # 2. Execute specific degradation logic
        if self.component_name == 'gmail_watcher':
            self.handle_gmail_failure(details)
        elif self.component_name == 'whatsapp_watcher':
             self.handle_whatsapp_failure(details)
        elif self.component_name == 'odoo_client':
            self.handle_odoo_failure(details)
            
        # 3. Alert Dashboard (via generic health update)
        # self.update_dashboard_status() # (Optional, or handled by watchdog)

    def report_recovery(self):
        """Report component recovery"""
        self._update_health_status(status="healthy")
        logger.info(f"{self.component_name} recovered.")

    def _update_health_status(self, status, error=None):
        data = {
            "status": status,
            "last_audit": datetime.now().isoformat(),
            "last_error": error
        }
        try:
            with open(self.health_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Failed to update health file: {e}")

    # --- Specific Handlers ---

    def handle_gmail_failure(self, details):
        """Graceful degradation for Gmail"""
        # Strategy: Queue locally
        logger.info("Engaging Gmail Degradation Protocol: Local Queueing")
        outbox = VAULT_PATH / 'Outbox_Queue'
        outbox.mkdir(exist_ok=True)
        # (Consumers of this would check this queue later)

    def handle_whatsapp_failure(self, details):
        """Graceful degradation for WhatsApp"""
        logger.info("Engaging WhatsApp Degradation Protocol: Pause & Alert")
        # Create alert file
        alert_file = INBOX_PATH / f"SYSTEM_ALERT_WHATSAPP_{datetime.now().strftime('%H%M%S')}.md"
        alert_file.write_text(f"""---
type: system_alert
priority: high
component: whatsapp
status: failed
---
WhatsApp Session Expired or Failed.
Details: {details}
Manual Intervention Required: Scan QR Code or Restart Session.
""")
    
    def handle_odoo_failure(self, details):
        logger.info("Engaging Odoo Degradation Protocol: Stale Data Mode")
        # Logic to maybe create a lock file 'ODOO_OFFLINE' which prevents billing scripts from running
        
    def handle_vault_lock(self, content, filename):
        """Emergency write if vault is locked"""
        emergency_path = TEMP_DIR / 'emergency_inbox'
        emergency_path.mkdir(exist_ok=True)
        try:
            (emergency_path / filename).write_text(content)
            logger.info(f"Wrote to emergency inbox: {filename}")
        except:
            logger.critical("Failed to write even to emergency inbox!")

