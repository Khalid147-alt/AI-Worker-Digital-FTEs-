
import time
import subprocess
import os
import sys
import psutil
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from pathlib import Path

# Config
VAULT_PATH = Path(os.getenv('VAULT_PATH', 'D:/Hackathon0/AI_Employee_Vault'))
LOGS_DIR = VAULT_PATH / 'Logs'
DASHBOARD_PATH = VAULT_PATH / 'Dashboard.md'

# List of scripts to monitor
# Note: Orchestrator launches Ralph loop, but is itself a long-running process
MONITORED_PROCESSES = {
    'orchestrator': ['python', 'D:/Hackathon0/orchestrator.py'],
    'fs_watcher': ['python', 'D:/Hackathon0/filesystem_watcher.py'],
    'linkedin_watcher': ['python', 'D:/Hackathon0/linkedin_watcher.py'] # Optional, consumes browser
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - WATCHDOG - %(message)s')
logger = logging.getLogger('Watchdog')

# Global State
process_handles = {}
restart_counts = {name: 0 for name in MONITORED_PROCESSES}
last_restart_time = {name: 0 for name in MONITORED_PROCESSES}

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            status = {name: (proc.poll() is None) for name, proc in process_handles.items()}
            self.wfile.write(json.dumps(status).encode())
        else:
            self.send_response(404)
            self.end_headers()

def start_process(name, cmd):
    logger.info(f"Starting {name}...")
    try:
        # Use Popen to launch
        proc = subprocess.Popen(cmd, cwd='D:/Hackathon0') # Adjust CWD if needed
        process_handles[name] = proc
        return proc
    except Exception as e:
        logger.error(f"Failed to start {name}: {e}")
        return None

def update_dashboard():
    """Update System Health section in Dashboard.md"""
    # Simple replacement or append. For now, we append a status log.
    # In Gold Tier, this should be more sophisticated (MCP tool call or regex replace).
    # We will write to a dedicated status file that Dashboard.md can include or we rely on Orchestrator to update Dashboard.
    
    status_lines = []
    for name, proc in process_handles.items():
        is_running = proc.poll() is None
        status = "🟢 Running" if is_running else "🔴 Stopped"
        pid = proc.pid if is_running else "N/A"
        status_lines.append(f"- **{name}**: {status} (PID: {pid})")
    
    health_content = "\n".join(status_lines)
    
    # Write to a file that Orchestrator can read to update Dashboard
    health_file = LOGS_DIR / 'system_health.md'
    try:
        health_file.write_text(f"### System Health (Updated: {time.strftime('%H:%M:%S')})\n{health_content}")
    except: pass

def run_watchdog():
    # Start HTTP Server
    server = HTTPServer(('localhost', 8765), HealthHandler)
    thread = Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    logger.info("Health check server started on port 8765")

    # Initial Start
    for name, cmd in MONITORED_PROCESSES.items():
        start_process(name, cmd)

    while True:
        for name, proc in list(process_handles.items()):
            return_code = proc.poll()
            
            if return_code is not None:
                # Process crashed
                logger.warning(f"{name} exited with code {return_code}")
                
                # Check restart policy
                now = time.time()
                if now - last_restart_time[name] < 60:
                    restart_counts[name] += 1
                else:
                    restart_counts[name] = 1 # Reset if last crash was > 1 min ago
                
                last_restart_time[name] = now
                
                if restart_counts[name] > 5:
                    logger.error(f"{name} is crashing repeatedly. Stopping restarts.")
                    # Create Alert
                    alert_path = VAULT_PATH / 'Inbox' / f'SYSTEM_ALERT_{name}.md'
                    alert_path.write_text(f"# SYSTEM ALERT: {name} Crashing\nProcess {name} failed 5 times in 1 minute. Automatic restart disabled.")
                    del process_handles[name] # Stop monitoring
                else:
                    logger.info(f"Restarting {name} in 5 seconds...")
                    time.sleep(5)
                    start_process(name, MONITORED_PROCESSES[name])

        update_dashboard()
        time.sleep(30)

if __name__ == "__main__":
    run_watchdog()
