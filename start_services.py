import subprocess
import time
import sys
import os

def start_process(command, name):
    print(f"Starting {name}...")
    try:
        # Use Popen to start independent processes
        # creationflags=subprocess.CREATE_NEW_CONSOLE opens a new window for each watcher
        # This is useful for the initial login (interactive)
        return subprocess.Popen(
            command, 
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            cwd=os.getcwd()
        )
    except Exception as e:
        print(f"Failed to start {name}: {e}")
        return None

def main():
    print("--- Starting Silver Tier AI Employee Services ---")
    
    # 1. Start WhatsApp Watcher
    whatsapp = start_process(['python', 'whatsapp_watcher.py'], "WhatsApp Watcher")
    
    # 2. Start LinkedIn Watcher
    linkedin = start_process(['python', 'linkedin_watcher.py'], "LinkedIn Watcher")
    
    # 3. Start Orchestrator
    orchestrator = start_process(['python', 'orchestrator.py'], "Orchestrator")
    
    print("\nAll services started in separate windows.")
    print("Please check the new windows for login prompts (WhatsApp/LinkedIn).")
    print("Press Ctrl+C in this window to stop all services (might need to close windows manually).")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping services...")
        # Note: This might not kill external consoles on Windows easily without more complex logic
        # But it's a start.
        if whatsapp: whatsapp.terminate()
        if linkedin: linkedin.terminate()
        if orchestrator: orchestrator.terminate()
        print("Services stopped.")

if __name__ == "__main__":
    main()
