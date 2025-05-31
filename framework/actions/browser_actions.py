"""
Browser Actions
High-level browser interaction actions
"""

import time
from typing import Optional

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from framework.utils.logger import Logger


class BrowserActions:
    def __init__(self, driver: webdriver.Remote):
        """Initialize Browser Actions"""
        self.driver = driver
        self.logger = Logger()
        self.wait = WebDriverWait(driver, 30)
        self.actions = ActionChains(driver)
    
    def navigate_to(self, url: str) -> bool:
        """Navigate to specified URL"""
        try:
            self.logger.info(f"Navigating to: {url}")
            self.driver.get(url)
            self.wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
            self.logger.info(f"Successfully navigated to: {url}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to navigate to {url}: {str(e)}")
            return False
    
    def refresh_page(self) -> bool:
        """Refresh current page"""
        try:
            self.logger.info("Refreshing page")
            self.driver.refresh()
            self.wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
            self.logger.info("Page refreshed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to refresh page: {str(e)}")
            return False
    
    def go_back(self) -> bool:
        """Navigate back in browser history"""
        try:
            self.logger.info("Navigating back")
            self.driver.back()
            time.sleep(2)  # Wait for navigation
            self.logger.info("Successfully navigated back")
            return True
        except Exception as e:
            self.logger.error(f"Failed to navigate back: {str(e)}")
            return False
    
    def go_forward(self) -> bool:
        """Navigate forward in browser history"""
        try:
            self.logger.info("Navigating forward")
            self.driver.forward()
            time.sleep(2)  # Wait for navigation
            self.logger.info("Successfully navigated forward")
            return True
        except Exception as e:
            self.logger.error(f"Failed to navigate forward: {str(e)}")
            return False
    
    def maximize_window(self) -> bool:
        """Maximize browser window"""
        try:
            self.logger.info("Maximizing window")
            self.driver.maximize_window()
            self.logger.info("Window maximized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to maximize window: {str(e)}")
            return False
    
    def minimize_window(self) -> bool:
        """Minimize browser window"""
        try:
            self.logger.info("Minimizing window")
            self.driver.minimize_window()
            self.logger.info("Window minimized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to minimize window: {str(e)}")
            return False
    
    def set_window_size(self, width: int, height: int) -> bool:
        """Set browser window size"""
        try:
            self.logger.info(f"Setting window size to {width}x{height}")
            self.driver.set_window_size(width, height)
            self.logger.info(f"Window size set to {width}x{height}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to set window size: {str(e)}")
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
    
    def get_page_source(self) -> str:
        """Get page source HTML"""
        try:
            source = self.driver.page_source
            self.logger.debug("Retrieved page source")
            return source
        except Exception as e:
            self.logger.error(f"Failed to get page source: {str(e)}")
            return ""
    
    def execute_javascript(self, script: str, *args) -> any:
        """Execute JavaScript code"""
        try:
            self.logger.info(f"Executing JavaScript: {script[:50]}...")
            result = self.driver.execute_script(script, *args)
            self.logger.info("JavaScript executed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Failed to execute JavaScript: {str(e)}")
            return None
    
    def scroll_to_top(self) -> bool:
        """Scroll to top of page"""
        try:
            self.logger.info("Scrolling to top of page")
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            self.logger.info("Scrolled to top successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to scroll to top: {str(e)}")
            return False
    
    def scroll_to_bottom(self) -> bool:
        """Scroll to bottom of page"""
        try:
            self.logger.info("Scrolling to bottom of page")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            self.logger.info("Scrolled to bottom successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to scroll to bottom: {str(e)}")
            return False
    
    def scroll_by_pixels(self, x: int, y: int) -> bool:
        """Scroll by specified pixel amounts"""
        try:
            self.logger.info(f"Scrolling by {x}, {y} pixels")
            self.driver.execute_script(f"window.scrollBy({x}, {y});")
            time.sleep(1)
            self.logger.info("Scroll completed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to scroll by pixels: {str(e)}")
            return False
    
    def wait_for_page_load(self, timeout: int = 30) -> bool:
        """Wait for page to completely load"""
        try:
            self.logger.info("Waiting for page to load")
            wait = WebDriverWait(self.driver, timeout)
            wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
            self.logger.info("Page loaded successfully")
            return True
        except Exception as e:
            self.logger.error(f"Page failed to load within {timeout} seconds: {str(e)}")
            return False
    
    def close_current_tab(self) -> bool:
        """Close current browser tab"""
        try:
            self.logger.info("Closing current tab")
            self.driver.close()
            self.logger.info("Tab closed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to close tab: {str(e)}")
            return False
    
    def switch_to_window(self, window_handle: str) -> bool:
        """Switch to specified window/tab"""
        try:
            self.logger.info(f"Switching to window: {window_handle}")
            self.driver.switch_to.window(window_handle)
            self.logger.info("Window switch successful")
            return True
        except Exception as e:
            self.logger.error(f"Failed to switch window: {str(e)}")
            return False
    
    def get_window_handles(self) -> list:
        """Get all window handles"""
        try:
            handles = self.driver.window_handles
            self.logger.debug(f"Found {len(handles)} window handles")
            return handles
        except Exception as e:
            self.logger.error(f"Failed to get window handles: {str(e)}")
            return []
    
    def accept_alert(self) -> bool:
        """Accept browser alert"""
        try:
            self.logger.info("Accepting alert")
            alert = self.driver.switch_to.alert
            alert.accept()
            self.logger.info("Alert accepted successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to accept alert: {str(e)}")
            return False
    
    def dismiss_alert(self) -> bool:
        """Dismiss browser alert"""
        try:
            self.logger.info("Dismissing alert")
            alert = self.driver.switch_to.alert
            alert.dismiss()
            self.logger.info("Alert dismissed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to dismiss alert: {str(e)}")
            return False
    
    def get_alert_text(self) -> Optional[str]:
        """Get text from browser alert"""
        try:
            alert = self.driver.switch_to.alert
            text = alert.text
            self.logger.info(f"Alert text: {text}")
            return text
        except Exception as e:
            self.logger.error(f"Failed to get alert text: {str(e)}")
            return None
