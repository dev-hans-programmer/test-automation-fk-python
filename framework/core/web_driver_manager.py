"""
WebDriver Manager
Manages WebDriver instances with configuration and cleanup
"""

import os
import time
from typing import Dict, Any, Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from framework.utils.logger import Logger


class WebDriverManager:
    def __init__(self, config: Dict[str, Any]):
        """Initialize WebDriver Manager"""
        self.config = config
        self.logger = Logger()
        self.driver: Optional[webdriver.Remote] = None
        self.browser = config.get('framework_config', {}).get('browser', 'chrome').lower()
        
    def initialize_driver(self) -> webdriver.Remote:
        """Initialize WebDriver based on configuration"""
        try:
            if self.browser == 'chrome':
                self.driver = self._create_chrome_driver()
            elif self.browser == 'firefox':
                self.driver = self._create_firefox_driver()
            else:
                raise ValueError(f"Unsupported browser: {self.browser}")
            
            # Configure timeouts
            implicit_wait = self.config.get('framework_config', {}).get('implicit_wait', 10)
            self.driver.implicitly_wait(implicit_wait)
            
            # Set window size
            self.driver.maximize_window()
            
            self.logger.info(f"WebDriver initialized: {self.browser}")
            return self.driver
            
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {str(e)}")
            raise
    
    def _create_chrome_driver(self) -> webdriver.Chrome:
        """Create Chrome WebDriver instance"""
        options = ChromeOptions()
        
        # Add common options
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        # Headless mode if specified
        framework_config = self.config.get('framework_config', {})
        if framework_config.get('headless', False):
            options.add_argument('--headless')
        
        # Disable notifications
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.images": 2
        }
        options.add_experimental_option("prefs", prefs)
        
        # Enable logging
        options.add_argument('--enable-logging')
        options.add_argument('--log-level=3')
        
        try:
            # Try to use system ChromeDriver
            driver = webdriver.Chrome(options=options)
            return driver
        except Exception as e:
            self.logger.error(f"Failed to create Chrome driver: {str(e)}")
            raise
    
    def _create_firefox_driver(self) -> webdriver.Firefox:
        """Create Firefox WebDriver instance"""
        options = FirefoxOptions()
        
        # Headless mode if specified
        framework_config = self.config.get('framework_config', {})
        if framework_config.get('headless', False):
            options.add_argument('--headless')
        
        # Set preferences
        options.set_preference('dom.webnotifications.enabled', False)
        options.set_preference('media.volume_scale', '0.0')
        
        try:
            driver = webdriver.Firefox(options=options)
            return driver
        except Exception as e:
            self.logger.error(f"Failed to create Firefox driver: {str(e)}")
            raise
    
    def quit_driver(self):
        """Quit WebDriver and cleanup"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("WebDriver quit successfully")
            except Exception as e:
                self.logger.error(f"Error quitting WebDriver: {str(e)}")
            finally:
                self.driver = None
    
    def restart_driver(self) -> webdriver.Remote:
        """Restart WebDriver"""
        self.quit_driver()
        time.sleep(2)  # Brief pause before restart
        return self.initialize_driver()
    
    def take_screenshot(self, filename: str) -> str:
        """Take screenshot and save to file"""
        if not self.driver:
            raise Exception("WebDriver not initialized")
        
        try:
            # Ensure screenshots directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Take screenshot
            self.driver.save_screenshot(filename)
            self.logger.info(f"Screenshot saved: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {str(e)}")
            raise
    
    def get_driver_info(self) -> Dict[str, Any]:
        """Get information about current driver"""
        if not self.driver:
            return {'status': 'not_initialized'}
        
        try:
            return {
                'status': 'active',
                'browser': self.browser,
                'current_url': self.driver.current_url,
                'title': self.driver.title,
                'window_size': self.driver.get_window_size(),
                'session_id': self.driver.session_id
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
