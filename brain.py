import time
import logging
from pathlib import Path
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Brain")

VAULT_PATH = Path(os.getenv('VAULT_PATH', './AI_Employee_Vault'))
NEEDS_ACTION = VAULT_PATH / 'Needs_Action'
APPROVED = VAULT_PATH / 'Approved'

def auto_respond():
    """Simulates the AI Brain: Reads Needs_Action and creates Approved responses for VIPs"""
    if not NEEDS_ACTION.exists(): return
    
    for file in NEEDS_ACTION.glob("*.md"):
        try:
            content = file.read_text(encoding='utf-8')
            
            # WhatsApp Auto-Reply for Ali
            if "type: whatsapp" in content and "from: Ali Nawaz Unarr2" in content:
                logger.info(f"Auto-replying to WhatsApp message: {file.name}")
                
                # Extract original message
                original_msg = content.split("## Message Content")[1].strip().split("\n")[0]
                
                # Simple AI Logic (Mocking Claude)
                reply_text = f"🤖 [Auto-Reply] I received your message: '{original_msg}'. How can I help further?"
                
                # Create Approved Response
                response_filename = f"WHATSAPP_REPLY_{int(time.time())}.md"
                response_content = f"""---
type: whatsapp_message
to: Ali Nawaz Unarr2
status: approved
---
## Message Content
{reply_text}
"""
                (APPROVED / response_filename).write_text(response_content, encoding='utf-8')
                
                # Move original to Done (Archive)
                (VAULT_PATH / 'Done').mkdir(exist_ok=True)
                file.rename(VAULT_PATH / 'Done' / file.name)
                
            # LinkedIn Comment Auto-Reply (Placeholder logic)
            elif "type: linkedin_feed_item" in content and "comment" in content.lower():
                 # Similar logic would go here for LinkedIn comments
                 pass

        except Exception as e:
            logger.error(f"Error processing {file.name}: {e}")

if __name__ == "__main__":
    logger.info("Starting AI Brain (Auto-Responder)...")
    while True:
        auto_respond()
        time.sleep(10)
