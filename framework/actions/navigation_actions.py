"""
Navigation Actions
High-level navigation and window management actions
"""

import time
from typing import List, Optional

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoAlertPresentException

from framework.utils.logger import Logger


class NavigationActions:
    def __init__(self, driver: webdriver.Remote):
        """Initialize Navigation Actions"""
        self.driver = driver
        self.logger = Logger()
        self.wait = WebDriverWait(driver, 30)
    
    def navigate_to_url(self, url: str, wait_for_load: bool = True) -> bool:
        """Navigate to specific URL"""
        try:
            self.logger.info(f"Navigating to URL: {url}")
            self.driver.get(url)
            
            if wait_for_load:
                self.wait_for_page_to_load()
            
            self.logger.info(f"Successfully navigated to: {url}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to navigate to URL {url}: {str(e)}")
            return False
    
    def refresh_page(self, wait_for_load: bool = True) -> bool:
        """Refresh current page"""
        try:
            self.logger.info("Refreshing current page")
            self.driver.refresh()
            
            if wait_for_load:
                self.wait_for_page_to_load()
            
            self.logger.info("Page refreshed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to refresh page: {str(e)}")
            return False
    
    def go_back(self, wait_for_load: bool = True) -> bool:
        """Navigate back in browser history"""
        try:
            self.logger.info("Navigating back in browser history")
            self.driver.back()
            
            if wait_for_load:
                self.wait_for_page_to_load()
            
            self.logger.info("Successfully navigated back")
            return True
        except Exception as e:
            self.logger.error(f"Failed to navigate back: {str(e)}")
            return False
    
    def go_forward(self, wait_for_load: bool = True) -> bool:
        """Navigate forward in browser history"""
        try:
            self.logger.info("Navigating forward in browser history")
            self.driver.forward()
            
            if wait_for_load:
                self.wait_for_page_to_load()
            
            self.logger.info("Successfully navigated forward")
            return True
        except Exception as e:
            self.logger.error(f"Failed to navigate forward: {str(e)}")
            return False
    
    def wait_for_page_to_load(self, timeout: int = 30) -> bool:
        """Wait for page to completely load"""
        try:
            self.logger.debug("Waiting for page to load")
            
            # Wait for document ready state
            wait = WebDriverWait(self.driver, timeout)
            wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
            
            # Additional wait for any AJAX/dynamic content
            time.sleep(2)
            
            self.logger.debug("Page loaded successfully")
            return True
        except TimeoutException:
            self.logger.warning(f"Page did not load completely within {timeout} seconds")
            return False
        except Exception as e:
            self.logger.error(f"Error waiting for page load: {str(e)}")
            return False
    
    def wait_for_url_to_contain(self, url_part: str, timeout: int = 30) -> bool:
        """Wait for URL to contain specific text"""
        try:
            self.logger.info(f"Waiting for URL to contain: {url_part}")
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.url_contains(url_part))
            self.logger.info(f"URL now contains: {url_part}")
            return True
        except TimeoutException:
            current_url = self.driver.current_url
            self.logger.error(f"URL did not contain '{url_part}' within {timeout} seconds. Current URL: {current_url}")
            return False
        except Exception as e:
            self.logger.error(f"Error waiting for URL to contain '{url_part}': {str(e)}")
            return False
    
    def wait_for_title_to_contain(self, title_part: str, timeout: int = 30) -> bool:
        """Wait for page title to contain specific text"""
        try:
            self.logger.info(f"Waiting for title to contain: {title_part}")
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.title_contains(title_part))
            self.logger.info(f"Title now contains: {title_part}")
            return True
        except TimeoutException:
            current_title = self.driver.title
            self.logger.error(f"Title did not contain '{title_part}' within {timeout} seconds. Current title: {current_title}")
            return False
        except Exception as e:
            self.logger.error(f"Error waiting for title to contain '{title_part}': {str(e)}")
            return False
    
    def open_new_tab(self, url: Optional[str] = None) -> bool:
        """Open new browser tab"""
        try:
            self.logger.info("Opening new tab")
            
            # Store current window handle
            original_window = self.driver.current_window_handle
            
            # Open new tab using JavaScript
            self.driver.execute_script("window.open('');")
            
            # Switch to new tab
            new_windows = self.driver.window_handles
            for window in new_windows:
                if window != original_window:
                    self.driver.switch_to.window(window)
                    break
            
            # Navigate to URL if provided
            if url:
                self.driver.get(url)
                self.wait_for_page_to_load()
            
            self.logger.info("New tab opened successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to open new tab: {str(e)}")
            return False
    
    def close_current_tab(self) -> bool:
        """Close current browser tab"""
        try:
            self.logger.info("Closing current tab")
            
            # Get all window handles before closing
            windows_before = self.driver.window_handles
            
            if len(windows_before) > 1:
                self.driver.close()
                
                # Switch to remaining window
                windows_after = self.driver.window_handles
                if windows_after:
                    self.driver.switch_to.window(windows_after[0])
                
                self.logger.info("Tab closed successfully")
                return True
            else:
                self.logger.warning("Cannot close the last remaining tab")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to close tab: {str(e)}")
            return False
    
    def switch_to_tab_by_index(self, index: int) -> bool:
        """Switch to tab by index (0-based)"""
        try:
            windows = self.driver.window_handles
            
            if 0 <= index < len(windows):
                self.driver.switch_to.window(windows[index])
                self.logger.info(f"Switched to tab at index: {index}")
                return True
            else:
                self.logger.error(f"Invalid tab index: {index}. Available tabs: {len(windows)}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to switch to tab {index}: {str(e)}")
            return False
    
    def switch_to_tab_by_title(self, title_part: str) -> bool:
        """Switch to tab by partial title match"""
        try:
            original_window = self.driver.current_window_handle
            
            for window in self.driver.window_handles:
                self.driver.switch_to.window(window)
                if title_part.lower() in self.driver.title.lower():
                    self.logger.info(f"Switched to tab with title containing: {title_part}")
                    return True
            
            # If not found, switch back to original
            self.driver.switch_to.window(original_window)
            self.logger.error(f"No tab found with title containing: {title_part}")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to switch to tab by title: {str(e)}")
            return False
    
    def get_current_url(self) -> str:
        """Get current page URL"""
        try:
            url = self.driver.current_url
            self.logger.debug(f"Current URL: {url}")
            return url
        except Exception as e:
            self.logger.error(f"Failed to get current URL: {str(e)}")
            return ""
    
    def get_page_title(self) -> str:
        """Get current page title"""
        try:
            title = self.driver.title
            self.logger.debug(f"Page title: {title}")
            return title
        except Exception as e:
            self.logger.error(f"Failed to get page title: {str(e)}")
            return ""
    
    def get_window_handles(self) -> List[str]:
        """Get all window handles"""
        try:
            handles = self.driver.window_handles
            self.logger.debug(f"Found {len(handles)} window handles")
            return handles
        except Exception as e:
            self.logger.error(f"Failed to get window handles: {str(e)}")
            return []
    
    def maximize_window(self) -> bool:
        """Maximize browser window"""
        try:
            self.driver.maximize_window()
            self.logger.info("Window maximized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to maximize window: {str(e)}")
            return False
    
    def minimize_window(self) -> bool:
        """Minimize browser window"""
        try:
            self.driver.minimize_window()
            self.logger.info("Window minimized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to minimize window: {str(e)}")
            return False
    
    def set_window_size(self, width: int, height: int) -> bool:
        """Set browser window size"""
        try:
            self.driver.set_window_size(width, height)
            self.logger.info(f"Window size set to {width}x{height}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to set window size: {str(e)}")
            return False
    
    def handle_alert(self, action: str = "accept", text_input: str = None) -> Optional[str]:
        """Handle browser alerts"""
        try:
            # Wait for alert to be present
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.alert_is_present())
            
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            
            self.logger.info(f"Alert detected with text: {alert_text}")
            
            if action.lower() == "accept":
                if text_input:
                    alert.send_keys(text_input)
                alert.accept()
                self.logger.info("Alert accepted")
            elif action.lower() == "dismiss":
                alert.dismiss()
                self.logger.info("Alert dismissed")
            
            return alert_text
            
        except TimeoutException:
            self.logger.debug("No alert present")
            return None
        except NoAlertPresentException:
            self.logger.debug("No alert present")
            return None
        except Exception as e:
            self.logger.error(f"Error handling alert: {str(e)}")
            return None
    
    def scroll_to_top(self) -> bool:
        """Scroll to top of page"""
        try:
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            self.logger.info("Scrolled to top of page")
            return True
        except Exception as e:
            self.logger.error(f"Failed to scroll to top: {str(e)}")
            return False
    
    def scroll_to_bottom(self) -> bool:
        """Scroll to bottom of page"""
        try:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            self.logger.info("Scrolled to bottom of page")
            return True
        except Exception as e:
            self.logger.error(f"Failed to scroll to bottom: {str(e)}")
            return False
