import time
import functools
import logging
import random
from pathlib import Path
from datetime import datetime

# Setup Logging
VAULT_PATH = Path('D:/Hackathon0/AI_Employee_Vault')
LOGS_DIR = VAULT_PATH / 'Logs'
LOGS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('RetryHandler')

def get_error_log_path():
    date_str = datetime.now().strftime('%Y-%m-%d')
    return LOGS_DIR / f'errors_{date_str}.log'

def log_error_to_file(component, error_type, message, context=""):
    try:
        log_file = get_error_log_path()
        timestamp = datetime.now().isoformat()
        entry = f"[{timestamp}] component={component} type={error_type} msg={message} context={context}\n"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(entry)
    except Exception as e:
        print(f"Failed to write to error log: {e}")

# Exception Hierarchy
class BaseRetryableError(Exception):
    """Base class for errors that can be retried"""
    pass

class TransientError(BaseRetryableError):
    """Temporary failures (network glitches, timeouts)"""
    pass

class AuthenticationError(BaseRetryableError):
    """Auth failures (expired tokens) - might need refresh logic before retry"""
    pass

class LogicError(Exception):
    """Code errors - usually NOT retryable unless it's a race condition"""
    pass

class DataError(Exception):
    """Invalid data formats - NOT retryable"""
    pass

# Decorator
def with_retry(max_attempts=3, base_delay=2, max_delay=60, backoff_factor=2, exceptions=(TransientError, AuthenticationError)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            delay = base_delay
            
            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    # Log the failure
                    error_msg = str(e)
                    component = func.__module__ + '.' + func.__name__
                    log_error_to_file(component, type(e).__name__, error_msg, f"Attempt {attempt}/{max_attempts}")
                    
                    if attempt == max_attempts:
                        logger.error(f"Max attempts reached for {component}. Raising error.")
                        raise # Re-raise the last exception
                    
                    # Calculate sleep time
                    sleep_time = min(delay + random.uniform(0, 1), max_delay) # Add jitter
                    logger.warning(f"{component} failed (Attempt {attempt}). Retrying in {sleep_time:.2f}s... Error: {error_msg}")
                    time.sleep(sleep_time)
                    
                    attempt += 1
                    delay *= backoff_factor
                except Exception as e:
                    # Non-retryable error
                    component = func.__module__ + '.' + func.__name__
                    log_error_to_file(component, "NonRetryable", str(e), "Fatal")
                    raise
            
        return wrapper
    return decorator
