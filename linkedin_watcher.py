from playwright.sync_api import sync_playwright
from pathlib import Path
from datetime import datetime
import time
import logging
import random
import traceback
import json
import sys

REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Import retry handler (assuming it's in the python path or relative)
try:
    from scripts.retry_handler import with_retry, TransientError
except ImportError:
    from scripts.retry_handler import with_retry, TransientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Import retry handler (assuming it's in the python path or relative)

class LinkedInWatcher:
    def __init__(self, vault_path: str, session_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.session_path = Path(session_path)
        self.processed_file = Path('linkedin_processed.json')
        self.processed_ids = self._load_processed()
        
        self.approved_path = self.vault_path / 'Approved'
        self.done_path = self.vault_path / 'Done'
        self.feed_queue = self.vault_path / 'Social_Media' / 'Feed_Queue'
        
        # Ensure directories exist
        self.needs_action.mkdir(exist_ok=True, parents=True)
        self.approved_path.mkdir(exist_ok=True, parents=True)
        self.done_path.mkdir(exist_ok=True, parents=True)
        self.feed_queue.mkdir(exist_ok=True, parents=True)
    
    def _load_processed(self):
        if self.processed_file.exists():
            with open(self.processed_file, 'r') as f:
                return set(json.load(f))
        return set()
    
    def _save_processed(self):
        with open(self.processed_file, 'w') as f:
            json.dump(list(self.processed_ids), f)
            
    def check_messages(self, page):
        messages = []
        try:
            if 'linkedin.com/messaging' not in page.url:
                page.goto('https://www.linkedin.com/messaging/')
                page.wait_for_load_state('networkidle')
            
            convos = page.query_selector_all('[data-view-name="message-list-item"]')
            
            for i, convo in enumerate(convos[:5]):
                try:
                    convo.click()
                    time.sleep(1)
                    sender_elem = page.query_selector('.msg-entity-lockup__entity-title')
                    sender = sender_elem.inner_text() if sender_elem else "Unknown"
                    msg_elem = page.query_selector('.msg-s-message-list__event--unread .msg-s-event-listitem__body')
                    if not msg_elem: continue
                    text = msg_elem.inner_text()
                    msg_id = f"{sender}_{hash(text)}"
                    if msg_id not in self.processed_ids:
                        messages.append({'sender': sender, 'text': text, 'timestamp': datetime.now().isoformat(), 'id': msg_id})
                        self.processed_ids.add(msg_id)
                except: continue
        except Exception as e:
            logger.error(f"Message check failed: {e}")
        return messages

    def create_action_file(self, message):
        content = f'''---
type: linkedin_message
from: {message['sender']}
received: {message['timestamp']}
priority: medium
status: pending
---
## Message Content
{message['text']}
## Suggested Actions
- [ ] Analyze the inquiry
- [ ] Draft professional reply
'''
        filename = f"LINKEDIN_MSG_{message['sender'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        (self.needs_action / filename).write_text(content, encoding='utf-8')

    def scan_feed(self, page):
        try:
            logger.info("Scanning feed...")
            if 'linkedin.com/feed' not in page.url:
                page.goto('https://www.linkedin.com/feed/')
                page.wait_for_load_state('networkidle')
            for _ in range(3):
                page.mouse.wheel(0, 500)
                time.sleep(2)
            # Try to find posts using data-view-name
            logger.info("Waiting for feed updates...")
            try:
                page.wait_for_selector('div[data-view-name="feed-full-update"]', timeout=10000)
                logger.info("Feed updates selector found!")
            except:
                logger.warning("Timeout waiting for feed-full-update selector")

            posts = page.locator('div[data-view-name="feed-full-update"]').all()
            logger.info(f"Selector 'div[data-view-name=\"feed-full-update\"]' found {len(posts)} items")

            if not posts:
                 # Fallback to list items or articles
                 logger.info("Falling back to role=listitem")
                 posts = page.locator('div[role="listitem"]').all()
                 logger.info(f"Selector 'div[role=\"listitem\"]' found {len(posts)} items")
            
            logger.info(f"Found {len(posts)} posts in feed")
            if len(posts) == 0:
                with open('debug_page.html', 'w', encoding='utf-8') as f:
                    f.write(page.content())
                logger.info("Dumped page content to debug_page.html")

            count = 0
            for post in posts:
                if count >= 3: break
                try:
                    # 1. Try attribute first
                    urn = post.get_attribute("data-urn")
                    
                    # 2. Try identifying via activity link
                    if not urn:
                        # Look for a link to the activity
                        link = post.locator('a[href*="urn:li:activity"]').first
                        if link.count() > 0:
                            href = link.get_attribute('href')
                            if "urn:li:activity:" in href:
                                import re
                                match = re.search(r'urn:li:activity:\d+', href)
                                if match:
                                    urn = match.group(0)
                    
                    # 3. Last ditch: data-id matching URN pattern
                    if not urn:
                        data_id = post.get_attribute("data-id")
                        if data_id and "urn:li:activity" in data_id:
                            urn = data_id

                    if not urn: continue
                    
                    if urn in self.processed_ids: continue
                    
                    # Text extraction
                    text = post.inner_text()
                    if not text: continue
                    
                    # Cleanup text
                    lines = [l.strip() for l in text.split('\n') if l.strip()]
                    clean_text = "\n".join(lines)
                    
                    self.create_feed_item(urn, clean_text)
                    self.processed_ids.add(urn)
                    
                    # --- ENGAGEMENT LOGIC ---
                    try:
                        logger.info(f"Engaging with post {urn}...")
                        
                        # 1. LIKE
                        like_btn = post.locator('button[aria-label*="Reaction button state: no reaction"]')
                        if like_btn.count() > 0:
                            like_btn.first.click()
                            logger.info("Liked post.")
                            time.sleep(2)
                        
                        # 2. COMMENT
                        comment_btn = post.locator('button[data-view-name="feed-comment-button"]')
                        if comment_btn.count() > 0:
                            comment_btn.first.click()
                            time.sleep(2)
                            
                            # Find the editor
                            editor = post.locator('div.ql-editor, div[role="textbox"]').first
                            if editor.count() > 0:
                                comments = ["Great insight!", "Thanks for sharing.", "Interesting perspective!", "Love this update."]
                                comment_text = random.choice(comments)
                                editor.fill(comment_text)
                                time.sleep(1)
                                
                                # Click Post
                                post_btn = post.locator('button.share-actions__primary-action, button:has-text("Post")').first
                                if post_btn.count() > 0:
                                    post_btn.click()
                                    logger.info(f"Commented: {comment_text}")
                                    time.sleep(3)
                    except Exception as e:
                        logger.error(f"Engagement failed for {urn}: {e}")
                    # ------------------------
                    
                    count += 1
                except Exception as e:
                    logger.error(f"Error processing post: {e}")
                    continue
        except Exception as e:
            logger.error(f"Feed scan failed: {e}")

    def create_feed_item(self, urn, text):
        safe_text = "".join([c for c in text[:30] if c.isalnum() or c==' ']).strip().replace(' ', '_')
        filename = f"POST_{safe_text}_{datetime.now().strftime('%H%M%S')}.md"
        content = f'''---
type: linkedin_feed_item
urn: {urn}
status: pending_review
timestamp: {datetime.now().isoformat()}
---
## Post Content
{text[:1000]}...
## Suggested Actions
- [ ] Like this post
- [ ] Comment: "Great insight!"
- [ ] Ignore
'''
        (self.feed_queue / filename).write_text(content, encoding='utf-8')
        logger.info(f"Saved feed item: {filename}")

    def execute_interaction(self, page, action_type, urn, comment_text=None):
        try:
            logger.info(f"Executing {action_type} on {urn}")
            post_url = f"https://www.linkedin.com/feed/update/{urn}/"
            page.goto(post_url)
            page.wait_for_load_state('networkidle')
            time.sleep(2)
            if action_type == 'linkedin_like':
                try: page.click('button[aria-label*="React Like"]', timeout=3000)
                except: page.click('text=Like', timeout=3000)
                logger.info("Liked post")
            elif action_type == 'linkedin_comment':
                page.click('button[aria-label*="Comment"]')
                time.sleep(1)
                page.type('.ql-editor', comment_text)
                time.sleep(1)
                page.click('button.comments-comment-box__submit-button')
                logger.info("Commented on post")
            return True
        except Exception as e:
            logger.error(f"Interaction failed: {e}")
            return False

    def post_update(self, page, content):
        try:
            logger.info("Posting update...")
            # Check if we need to navigate
            if 'linkedin.com/feed' not in page.url:
                try:
                    logger.info("Navigating to feed...")
                    page.goto('https://www.linkedin.com/feed/', timeout=60000, wait_until='domcontentloaded')
                except Exception as e:
                    logger.warning(f"Navigation timeout (ignoring if loaded): {e}")
            
            time.sleep(5)
            # Click "Start a post" - Try multiple selectors
            selectors = [
                'button.share-box-feed-entry__trigger',
                'button:has-text("Start a post")', 
                '.share-box-feed-entry__trigger',
                'text=Start a post'
            ]
            
            clicked = False
            for selector in selectors:
                try:
                    if page.is_visible(selector):
                        logger.info(f"Targeting '{selector}'...")
                        # Use force=True to bypass overlapping elements
                        page.click(selector, force=True)
                        clicked = True
                        logger.info(f"Clicked 'Start a post' using: {selector}")
                        break
                except Exception as e:
                    logger.warning(f"Failed to click '{selector}': {e}")
                    continue
            
            if not clicked:
                # Force click the first one found if visibility check fails
                try:
                    logger.info("Attempting fallback click...")
                    page.click('button.share-box-feed-entry__trigger', force=True, timeout=2000)
                    clicked = True
                except:
                    logger.error("Could not find 'Start a post' button with any selector")
                    # Capture screenshot for debugging
                    try:
                        page.screenshot(path="post_error.png")
                        logger.info("Saved error screenshot to post_error.png")
                    except: pass
                    return False
            
            time.sleep(2)
            
            # Type detection - handle different editors
            logger.info("Typing content...")
            try:
                page.fill('.ql-editor', content)
                logger.info("Typed using .ql-editor")
            except:
                # Fallback for different editor types
                logger.info("Typing using keyboard...")
                page.keyboard.type(content)
                logger.info("Typed using keyboard")

            time.sleep(2)
            
            # Post
            logger.info("Clicking Post button...")
            post_btn_selectors = ['.share-actions__primary-action', 'button:has-text("Post")']
            clicked_post = False
            for btn_sel in post_btn_selectors:
                try:
                    # Check if enabled
                    if page.is_disabled(btn_sel):
                        logger.warning(f"Post button {btn_sel} is disabled!")
                        continue
                        
                    page.click(btn_sel, timeout=3000)
                    logger.info(f"Clicked Post button: {btn_sel}")
                    clicked_post = True
                    break
                except Exception as e: 
                    logger.warning(f"Failed to click {btn_sel}: {e}")
                    continue
            
            if not clicked_post:
                logger.error("Failed to click any Post button")
                return False
                
            logger.info("Waiting for modal to close...")
            try:
                page.wait_for_selector('.share-box-feed-entry__trigger', timeout=10000)
                logger.info("Modal closed, post successful.")
                return True
            except:
                logger.warning("Timeout waiting for modal to close. Assuming success if no error.")
                return True # Optimistic success to move file

        except Exception as e:
            logger.error(f"Post failed: {e}")
            return False

    def check_approved_posts(self, page):
        for file_path in self.approved_path.glob("*.md"):
            try:
                content = file_path.read_text(encoding='utf-8')
                if "type: linkedin_post" in content and "## Post Content" in content:
                    post_body = content.split("## Post Content")[1].split("##")[0].strip()
                    if self.post_update(page, post_body):
                        file_path.rename(self.done_path / file_path.name)
                elif "type: linkedin_feed_item" in content:
                    urn = [line for line in content.split('\n') if 'urn:' in line][0].split('urn:')[1].strip()
                    if "- [x] Like this post" in content:
                        self.execute_interaction(page, 'linkedin_like', urn)
                    if "- [x] Comment:" in content:
                        import re
                        match = re.search(r'- \[x\] Comment: "(.*)"', content)
                        if match: self.execute_interaction(page, 'linkedin_comment', urn, match.group(1))
                    file_path.rename(self.done_path / file_path.name)
            except Exception as e:
                logger.error(f"Error processing approved file {file_path}: {e}")

    def run(self, check_interval=300):
        logger.info("Starting LinkedIn Watcher (Playwright)...")
        playwright = None
        browser = None
        page = None
        
        while True:
            try:
                if browser is None:
                    playwright = sync_playwright().start()
                    if not self.session_path.exists():
                        self.session_path.mkdir(parents=True)
                        
                    browser = playwright.chromium.launch_persistent_context(
                        user_data_dir=str(self.session_path.resolve()),
                        headless=False,
                        args=['--start-maximized']
                    )
                    
                    page = browser.pages[0] if browser.pages else browser.new_page()
                    
                    # Initial login check with blocking loop
                    try:
                        page.goto('https://www.linkedin.com/feed/', timeout=60000, wait_until='domcontentloaded')
                    except Exception as e:
                        logger.warning(f"Initial navigation warning: {e}")
                    logger.info("Checking login status...")
                    
                    logged_in = False
                    while not logged_in:
                        try:
                            # Check for profile photo, feed identity, or "Start a post"
                            if (page.query_selector('.global-nav__me-photo') or 
                                page.query_selector('#global-nav') or 
                                page.get_by_text("Start a post").is_visible() or
                                "Feed | LinkedIn" in page.title()):
                                
                                logger.info("✅ Login detected! Starting automation...")
                                logged_in = True
                            else:
                                logger.warning("❌ Not logged in. Please log in to LinkedIn in the opened browser window.")
                                time.sleep(5)
                        except Exception as e:
                            logger.error(f"Login check error: {e}")
                            time.sleep(5)

                # Main Cycle
                # self.check_messages(page) # Skipped for direct feed engagement
                self.scan_feed(page) # Re-enabled for autonomous engagement
                
                logger.info(f"Checking for approved posts in {self.approved_path}...")
                self.check_approved_posts(page)
                
                self._save_processed()
                logger.info("Cycle complete.")
                
            except Exception as e:
                logger.error(f"Main loop error: {e}")
                traceback.print_exc()
                # Reset browser on error to recover
                try:
                    if browser: browser.close()
                    if playwright: playwright.stop()
                except: pass
                browser = None
                playwright = None
                time.sleep(5) # Restart quickly on error
            
            time.sleep(check_interval)

if __name__ == "__main__":
    import os
    VAULT = os.getenv('VAULT_PATH', './AI_Employee_Vault')
    # Use different session path to avoid locks
    SESSION = os.getenv('LINKEDIN_SESSION_PATH', './linkedin_session_pw')
    # SESSION = f'./linkedin_session_debug_{random.randint(1000,9999)}'
    
    watcher = LinkedInWatcher(VAULT, SESSION)
    watcher.run()
