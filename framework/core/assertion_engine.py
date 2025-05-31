"""
Assertion Engine
Custom assertion system for test validation
"""

from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from framework.utils.logger import Logger


class AssertionEngine:
    def __init__(self, driver: webdriver.Remote):
        """Initialize Assertion Engine"""
        self.driver = driver
        self.logger = Logger()
        self.wait = WebDriverWait(driver, 10)
    
    def assert_element_visible(self, target: str):
        """Assert element is visible"""
        try:
            by, locator = self._parse_target(target)
            element = self.wait.until(EC.visibility_of_element_located((by, locator)))
            self.logger.info(f"Element is visible: {target}")
            return True
        except Exception as e:
            raise AssertionError(f"Element not visible: {target} - {str(e)}")
    
    def assert_element_text(self, target: str, expected_text: str):
        """Assert element contains expected text"""
        try:
            by, locator = self._parse_target(target)
            element = self.wait.until(EC.presence_of_element_located((by, locator)))
            actual_text = element.text.strip()
            
            if expected_text not in actual_text:
                raise AssertionError(
                    f"Text assertion failed. Expected: '{expected_text}', "
                    f"Actual: '{actual_text}'"
                )
            
            self.logger.info(f"Text assertion passed: {target} contains '{expected_text}'")
            return True
            
        except Exception as e:
            if isinstance(e, AssertionError):
                raise
            raise AssertionError(f"Text assertion failed: {target} - {str(e)}")
    
    def assert_element_count(self, target: str, expected_count: int):
        """Assert number of elements matching target"""
        try:
            by, locator = self._parse_target(target)
            elements = self.driver.find_elements(by, locator)
            actual_count = len(elements)
            
            if actual_count != expected_count:
                raise AssertionError(
                    f"Element count assertion failed. Expected: {expected_count}, "
                    f"Actual: {actual_count}"
                )
            
            self.logger.info(f"Element count assertion passed: {target} count = {expected_count}")
            return True
            
        except Exception as e:
            if isinstance(e, AssertionError):
                raise
            raise AssertionError(f"Element count assertion failed: {target} - {str(e)}")
    
    def assert_url_contains(self, expected_url_part: str):
        """Assert current URL contains expected part"""
        try:
            current_url = self.driver.current_url
            
            if expected_url_part not in current_url:
                raise AssertionError(
                    f"URL assertion failed. Expected URL to contain: '{expected_url_part}', "
                    f"Actual URL: '{current_url}'"
                )
            
            self.logger.info(f"URL assertion passed: URL contains '{expected_url_part}'")
            return True
            
        except Exception as e:
            if isinstance(e, AssertionError):
                raise
            raise AssertionError(f"URL assertion failed - {str(e)}")
    
    def assert_title_contains(self, expected_title_part: str):
        """Assert page title contains expected part"""
        try:
            current_title = self.driver.title
            
            if expected_title_part not in current_title:
                raise AssertionError(
                    f"Title assertion failed. Expected title to contain: '{expected_title_part}', "
                    f"Actual title: '{current_title}'"
                )
            
            self.logger.info(f"Title assertion passed: Title contains '{expected_title_part}'")
            return True
            
        except Exception as e:
            if isinstance(e, AssertionError):
                raise
            raise AssertionError(f"Title assertion failed - {str(e)}")
    
    def assert_element_attribute(self, target: str, attribute: str, expected_value: str):
        """Assert element attribute has expected value"""
        try:
            by, locator = self._parse_target(target)
            element = self.wait.until(EC.presence_of_element_located((by, locator)))
            actual_value = element.get_attribute(attribute)
            
            if actual_value != expected_value:
                raise AssertionError(
                    f"Attribute assertion failed. Expected {attribute}='{expected_value}', "
                    f"Actual {attribute}='{actual_value}'"
                )
            
            self.logger.info(f"Attribute assertion passed: {target} {attribute}='{expected_value}'")
            return True
            
        except Exception as e:
            if isinstance(e, AssertionError):
                raise
            raise AssertionError(f"Attribute assertion failed: {target} - {str(e)}")
    
    def assert_element_not_visible(self, target: str):
        """Assert element is not visible"""
        try:
            by, locator = self._parse_target(target)
            elements = self.driver.find_elements(by, locator)
            
            if elements and elements[0].is_displayed():
                raise AssertionError(f"Element should not be visible: {target}")
            
            self.logger.info(f"Element not visible assertion passed: {target}")
            return True
            
        except Exception as e:
            if isinstance(e, AssertionError):
                raise
            raise AssertionError(f"Element not visible assertion failed: {target} - {str(e)}")
    
    def _parse_target(self, target: str) -> tuple:
        """Parse target string to By and locator"""
        if ':' not in target:
            raise ValueError(f"Invalid target format: {target}")
        
        strategy, locator = target.split(':', 1)
        
        strategy_map = {
            'id': By.ID,
            'name': By.NAME,
            'class': By.CLASS_NAME,
            'tag': By.TAG_NAME,
            'css': By.CSS_SELECTOR,
            'xpath': By.XPATH,
            'link_text': By.LINK_TEXT,
            'partial_link_text': By.PARTIAL_LINK_TEXT
        }
        
        if strategy not in strategy_map:
            raise ValueError(f"Unsupported target strategy: {strategy}")
        
        return strategy_map[strategy], locator
