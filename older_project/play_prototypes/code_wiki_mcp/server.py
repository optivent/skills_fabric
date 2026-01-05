import time
import sys
import signal
import atexit

from mcp.server.fastmcp import FastMCP
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Initialize FastMCP server
mcp = FastMCP("CodeWiki")

# Global driver registry for cleanup
_active_drivers = []

def log(message):
    """Helper function to log messages to stderr"""
    print(f"[CodeWiki] {message}", file=sys.stderr, flush=True)

def cleanup_all_drivers():
    """Cleanup all active Chrome drivers"""
    log(f"Cleaning up {len(_active_drivers)} active drivers...")
    for driver in _active_drivers:
        try:
            driver.quit()
        except:
            pass
    _active_drivers.clear()

# Register cleanup handlers
atexit.register(cleanup_all_drivers)
signal.signal(signal.SIGTERM, lambda s, f: cleanup_all_drivers())
signal.signal(signal.SIGINT, lambda s, f: cleanup_all_drivers())

@mcp.tool()
def search_code_wiki(repo_url: str, query: str = "") -> str:
    """
    Interacts with Google CodeWiki chat interface to ask questions about a repository.
    
    Args:
        repo_url: The full URL of the repository (e.g., https://github.com/microsoft/vscode-copilot-chat)
        query: Question to ask the CodeWiki chat agent (required for meaningful interaction).
    """
    import threading
    
    log(f"Starting search_code_wiki - repo: {repo_url}, query: {query}")
    
    if not query:
        log("Error: No query provided")
        return "Error: 'query' parameter is required to ask CodeWiki a question. Example: 'Where are the Allow/Skip buttons implemented?'"
    
    # Hard timeout - kill after 60 seconds
    result = [None]
    exception = [None]
    
    def run_with_timeout():
        try:
            result[0] = _search_code_wiki_impl(repo_url, query)
        except Exception as e:
            exception[0] = e
    
    thread = threading.Thread(target=run_with_timeout, daemon=True)
    thread.start()
    thread.join(timeout=60)  # 60 second hard timeout
    
    if thread.is_alive():
        log("TIMEOUT: Tool exceeded 60 seconds, forcing cleanup")
        cleanup_all_drivers()
        return "Error: Request timed out after 60 seconds. Chrome may have frozen. Please try again."
    
    if exception[0]:
        raise exception[0]
    
    return result[0] or "Error: No result returned"

def _search_code_wiki_impl(repo_url: str, query: str) -> str:
    """Internal implementation of search_code_wiki"""
    # Clean repo URL to match CodeWiki format
    # Format: https://codewiki.google/github.com/owner/repo
    clean_repo = repo_url.replace("https://", "").replace("http://", "")
    target_url = f"https://codewiki.google/{clean_repo}"
    log(f"Target URL: {target_url}")
    
    driver = None
    try:
        log("Setting up Chrome options...")
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")  # Enable headless for speed
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.page_load_strategy = 'eager'  # Don't wait for all resources
        
        log("Initializing Chrome driver...")
        # Initialize driver with faster options
        try:
            driver = webdriver.Chrome(options=chrome_options)
            _active_drivers.append(driver)  # Track for cleanup
            log("Chrome driver initialized successfully")
        except Exception as e:
            log(f"FAILED to initialize Chrome driver: {str(e)}")
            raise
        
        driver.set_page_load_timeout(30)  # Set timeout
        
        log(f"Navigating to {target_url}...")
        driver.get(target_url)
        
        # Wait for page to load
        log("Waiting for page to load...")
        wait = WebDriverWait(driver, 20)  # Reduced from 30
        time.sleep(3)  # Reduced from 5 - just enough for JS to load
        log("Page loaded")
        
        # Try to find the chat input - common selectors for chat interfaces
        chat_input_selectors = [
            "textarea[placeholder*='Ask']",
            "textarea[placeholder*='ask']",
            "textarea[placeholder*='question']",
            "textarea[placeholder*='Question']",
            "input[placeholder*='Ask']",
            "input[placeholder*='ask']",
            "input[placeholder*='question']",
            "textarea[aria-label*='chat']",
            "textarea[aria-label*='Chat']",
            "textarea[aria-label*='message']",
            "div[contenteditable='true']",
            "textarea",
            "input[type='text']",
        ]
        
        log("Looking for chat input...")
        chat_input = None
        for selector in chat_input_selectors:
            try:
                chat_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                if chat_input.is_displayed() and chat_input.is_enabled():
                    log(f"Found chat input with selector: {selector}")
                    break
            except (TimeoutException, NoSuchElementException):
                continue
        
        if not chat_input:
            log("ERROR: Could not find chat input")
            return f"Error: Could not locate chat input on {target_url}. CodeWiki may require authentication or the page structure has changed."
        
        log("Typing query into chat input...")
        # Type the query
        chat_input.clear()
        time.sleep(0.3)
        chat_input.send_keys(query)
        time.sleep(0.5)
        log("Query typed successfully")
        
        # Get initial page text to compare later
        log("Getting initial page text...")
        initial_text = driver.find_element(By.TAG_NAME, "body").text
        log(f"Initial text length: {len(initial_text)}")
        
        log("Pressing Enter to submit...")
        # Try pressing Enter first (most reliable)
        from selenium.webdriver.common.keys import Keys
        chat_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        log("Looking for submit button...")
        # Also try to find and click submit button as backup
        submit_button_selectors = [
            "button[type='submit']",
            "button[aria-label*='Send']",
            "button[aria-label*='send']",
            "button[aria-label*='submit']",
            "button[title*='Send']",
            "button[title*='send']",
            "mat-icon:contains('send')",
            "svg[class*='send']",
        ]
        
        for selector in submit_button_selectors:
            try:
                buttons = driver.find_elements(By.CSS_SELECTOR, selector.split(':')[0])  # Remove pseudo-selector
                for btn in buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        try:
                            btn.click()
                            log(f"Clicked submit button: {selector}")
                            break
                        except:
                            pass
            except:
                continue
        
        # Wait for response to appear
        log("Waiting for response to generate...")
        time.sleep(5)  # Give time for response to start generating
        
        # Try to find response content - look for new content that wasn't there before
        response_selectors = [
            "div[class*='message']",
            "div[class*='response']",
            "div[class*='answer']",
            "div[class*='chat']",
            "div[role='article']",
            "div[class*='gemini']",
            "div[class*='ai']",
            "p",
            "pre",
            "code",
        ]
        
        # Wait up to 45 seconds for response (Gemini can be slow)
        max_wait = 45
        start_time = time.time()
        response_text = ""
        last_text_length = 0
        
        log("Polling for response content...")
        poll_count = 0
        
        while time.time() - start_time < max_wait:
            poll_count += 1
            # Check if page content changed (new text appeared)
            current_text = driver.find_element(By.TAG_NAME, "body").text
            
            if poll_count % 5 == 0:  # Log every 5th poll
                log(f"Poll #{poll_count}: current length={len(current_text)}, initial={len(initial_text)}")
            
            # If significant new text appeared
            if len(current_text) > len(initial_text) + 50:
                # Extract the new content
                response_text = current_text
                log(f"Detected new content! Length: {len(current_text)} vs {len(initial_text)}")
                
                # Check if response is still loading (text keeps growing)
                if len(current_text) > last_text_length:
                    last_text_length = len(current_text)
                    log("Response still growing, waiting more...")
                    time.sleep(2)  # Wait a bit more for response to complete
                    continue
                else:
                    # Response seems complete
                    log("Response complete!")
                    break
            
            time.sleep(3)
        
        if not response_text or response_text == initial_text:
            log("No new content detected, trying fallback selectors...")
            # Fallback: try specific selectors
            for selector in response_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        texts = [elem.text for elem in elements[-5:] if elem.text.strip() and len(elem.text) > 20]
                        if texts:
                            response_text = "\n\n".join(texts)
                            log(f"Found response using selector: {selector}")
                            break
                except:
                    continue
        
        if not response_text:
            log("Using last resort: entire body text")
            # Last resort: get all visible text
            body = driver.find_element(By.TAG_NAME, "body")
            response_text = body.text
        
        log(f"Final response text length: {len(response_text)}")
        
        # Clean and format response
        if response_text:
            log("Cleaning and formatting response...")
            # Try to extract just the relevant part (remove duplicate wiki content)
            lines = response_text.split('\n')
            # Find where the actual response starts (after query)
            response_start = -1
            for i, line in enumerate(lines):
                if query.lower() in line.lower():
                    response_start = i + 1
                    break
            
            if response_start > 0:
                relevant_lines = lines[response_start:]
                response_text = '\n'.join(relevant_lines)
            
            # Clean up common UI artifacts
            response_text = response_text.replace('content_copy', '').replace('refresh', '').replace('send', '').strip()
            
            log("Response ready to return")
            return f"CodeWiki response for '{query}':\n\n{response_text[:4000]}"
        else:
            log("ERROR: No response text found")
            return f"No response received from CodeWiki after submitting query: '{query}'. The page may require authentication or the response took too long."
        
    except TimeoutException:
        log("ERROR: Timeout exception")
        return f"Timeout: CodeWiki page took too long to load or respond. URL: {target_url}"
    except Exception as e:
        log(f"ERROR: Exception occurred: {str(e)}")
        return f"Error interacting with CodeWiki: {str(e)}\nURL: {target_url}"
    finally:
        if driver:
            log("Closing browser...")
            try:
                driver.quit()
                if driver in _active_drivers:
                    _active_drivers.remove(driver)
                log("Browser closed successfully")
            except Exception as e:
                log(f"Error closing browser: {str(e)}")
                # Force kill if needed
                try:
                    driver.service.process.kill()
                except:
                    pass

if __name__ == "__main__":
    mcp.run()
