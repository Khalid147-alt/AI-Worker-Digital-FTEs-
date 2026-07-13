from playwright.sync_api import sync_playwright
from pathlib import Path
from datetime import datetime
import time
import json
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhatsAppWatcher:
    def __init__(self, vault_path: str, session_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.session_path = Path(session_path)
        self.keywords = ['urgent', 'asap', 'invoice', 'payment', 'help', 'project', 'quote']
        self.processed_file = Path('whatsapp_processed.json')
        self.processed_ids = self._load_processed()
        
        # Ensure Needs_Action exists
        self.needs_action.mkdir(exist_ok=True, parents=True)
        
    def _load_processed(self):
        if self.processed_file.exists():
            with open(self.processed_file, 'r') as f:
                return set(json.load(f))
        return set()
    
    def _save_processed(self):
        with open(self.processed_file, 'w') as f:
            json.dump(list(self.processed_ids), f)
    
    def check_for_updates(self, page):
        logger.info("Checking for updates...")
        messages = []
        try:
            # Ensure we are on WhatsApp Web
            if 'web.whatsapp.com' not in page.url:
                 page.goto('https://web.whatsapp.com')
                 try:
                    # Wait for ANY of these common selectors to indicate login
                    page.wait_for_selector('#pane-side, [data-testid="chat-list"], [aria-label="Chat list"]', timeout=30000)
                 except Exception:
                    logger.warning("Login check timed out. Proceeding to check messages assuming user is logged in...")
                    # return []

            # Filter valid chats to check
            chats_to_check = []
            
            # Scrape all visible rows first to find VIPs
            all_rows = page.query_selector_all('div[role="row"]')
            for row in all_rows[:10]: # Check top 10
                try:
                    row_text = row.inner_text().lower()
                    # logger.info(f"Row text: {row_text.splitlines()[0]}") # Debug
                    
                    # Priority: Is this Ali?
                    # if "ali nawaz" in row_text:
                    #     logger.info(f"Target found: Ali Nawaz (in row). Clicking...")
                    #     chats_to_check.insert(0, {'elem': row, 'is_vip': True, 'name': 'Ali Nawaz Unarr2'})
                    if "unread message" in row.get_attribute("aria-label") or "unread" in row_text:
                         chats_to_check.append({'elem': row, 'is_vip': False, 'name': 'Unknown'})
                except: pass
            
            # Process identified chats
            for chat_item in chats_to_check[:5]:
                try:
                    chat_elem = chat_item['elem']
                    chat_elem.click()
                    time.sleep(3) # Give it time to load messages
                    
                    contact = chat_item['name']
                    # If unknown, try to read header (fallback)
                    if contact == 'Unknown':
                        try:
                            contact = page.wait_for_selector('header span[title]', timeout=2000).get_attribute('title')
                        except: 
                            contact = "Unknown"
                    
                    logger.info(f"Inspecting chat with: {contact}")
                    
                    # Get messages
                    time.sleep(3) # Extra wait for messages to render
                    msg_containers = page.query_selector_all('[data-testid="msg-container"]')
                    if not msg_containers:
                         # Fallback selector
                         msg_containers = page.query_selector_all('div.message-in, div.message-out')
                    
                    logger.info(f"Found {len(msg_containers)} messages in chat.")
                    
                    for msg in msg_containers[-5:]:
                        text = msg.inner_text().lower()
                        msg_id = f"{contact}_{hash(text)}"
                        
                        # Relaxed VIP check
                        is_vip = False #"ali nawaz" in contact.lower()
                        
                        if is_vip and msg_id not in self.processed_ids:
                             logger.info(f"CAPTURED VIP MESSAGE: {text[:30]}...")
                             messages.append({
                                'contact': contact,
                                'text': msg.inner_text(),
                                'timestamp': datetime.now().isoformat(),
                                'id': msg_id
                            })
                             self.processed_ids.add(msg_id)
                        else:
                            # Debug why we skipped
                            if not is_vip: logger.info(f"Skipped (Not VIP): {contact}")
                            elif msg_id in self.processed_ids: logger.info(f"Skipped (Already Processed): {text[:15]}...")

                except Exception as e:
                    logger.error(f"Error processing chat: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"WhatsApp watcher error: {e}")
            # Do NOT raise e, otherwise the main loop will close the browser.
            # Just return empty list and try again next loop.
            return []
        
        return messages
    
    def create_action_file(self, message):
        content = f'''---
type: whatsapp
from: {message['contact']}
received: {message['timestamp']}
priority: high
status: pending
keywords_matched: {[kw for kw in self.keywords if kw in message['text'].lower()]}
---

## Message Content
{message['text']}

## Suggested Actions
- [ ] Analyze the request
- [ ] Draft appropriate reply
- [ ] Create approval file in /Pending_Approval
- [ ] Log interaction
'''
        
        filename = f"WHATSAPP_{message['contact'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = self.needs_action / filename
        filepath.write_text(content, encoding='utf-8')
        logger.info(f"Created: {filepath}")
        return filepath

    def send_message(self, page, contact_name, message_text):
        try:
            logger.info(f"Sending message to {contact_name}...")
            # Search for contact
            search_box = page.wait_for_selector('div[contenteditable="true"][data-tab="3"]', timeout=5000)
            search_box.click()
            # Clear previous search
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            
            search_box.fill(contact_name)
            time.sleep(2)
            
            # Click the contact (first result)
            page.wait_for_selector(f'span[title="{contact_name}"]', timeout=5000).click()
            time.sleep(1)
            
            # Type and send message
            msg_box = page.wait_for_selector('div[contenteditable="true"][data-tab="10"]', timeout=5000)
            msg_box.click()
            msg_box.fill(message_text)
            time.sleep(1)
            page.keyboard.press("Enter")
            
            logger.info(f"Message sent to {contact_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to send message to {contact_name}: {e}")
            return False

    def check_approved_messages(self, page):
        approved_dir = self.vault_path / 'Approved'
        done_dir = self.vault_path / 'Done'
        approved_dir.mkdir(exist_ok=True)
        done_dir.mkdir(exist_ok=True)
        
        for file_path in approved_dir.glob("*.md"):
            try:
                content = file_path.read_text(encoding='utf-8')
                if "type: whatsapp_message" in content:
                    logger.info(f"Processing outgoing message: {file_path.name}")
                    # Extract fields
                    lines = content.split('\n')
                    contact = next((l.split('to:')[1].strip() for l in lines if l.startswith('to:')), None)
                    
                    if not contact:
                        logger.error(f"No 'to:' field found in {file_path}")
                        continue
                        
                    # Extract message body
                    if "## Message Content" in content:
                        message_body = content.split("## Message Content")[1].strip()
                    else:
                        message_body = content.split('---')[-1].strip()
                        
                    if self.send_message(page, contact, message_body):
                        file_path.rename(done_dir / file_path.name)
            except Exception as e:
                logger.error(f"Error processing approved message {file_path}: {e}")

    def run(self, check_interval=10):
        logger.info("Starting WhatsApp Watcher...")
        browser = None
        page = None
        playwright = None

        while True:
            try:
                if browser is None:
                    playwright = sync_playwright().start()
                    # Launch persistent context (keeps you logged in)
                    if not self.session_path.exists():
                        self.session_path.mkdir(parents=True)

                    browser = playwright.chromium.launch_persistent_context(
                        str(self.session_path.resolve()),
                        headless=False,  # Set True for background operation
                        args=['--start-maximized']
                    )
                    
                    page = browser.pages[0] if browser.pages else browser.new_page()
                    page.goto('https://web.whatsapp.com')
                    logger.info("WhatsApp loaded. Waiting for login or messages...")
                    
                    # increased initial wait for login
                    # Login check handled inside check_for_updates now
                    # self.check_for_updates(page) calls ensure_login implicitly or bypasses it
                    pass


                messages = self.check_for_updates(page)
                for msg in messages:
                    self.create_action_file(msg)
                
                # Check for approved messages to send
                self.check_approved_messages(page)
                
                self._save_processed()
                if messages:
                    logger.info(f"Checked WhatsApp. Found {len(messages)} new urgent messages.")
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                # Reset browser on error
                try:
                    if browser: browser.close()
                    if playwright: playwright.stop()
                except:
                    pass
                browser = None
                playwright = None
            
            time.sleep(check_interval)

if __name__ == "__main__":
    import os
    # Default paths
    VAULT = os.getenv('VAULT_PATH', './AI_Employee_Vault')
    SESSION = os.getenv('WHATSAPP_SESSION_PATH', './whatsapp_session')
    
    watcher = WhatsAppWatcher(VAULT, SESSION)
    watcher.run()
