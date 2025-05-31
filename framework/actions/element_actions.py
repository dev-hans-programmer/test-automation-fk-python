"""
Element Actions
High-level element interaction actions
"""

import time
from typing import List, Optional, Union

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from framework.utils.logger import Logger


class ElementActions:
    def __init__(self, driver: webdriver.Remote):
        """Initialize Element Actions"""
        self.driver = driver
        self.logger = Logger()
        self.wait = WebDriverWait(driver, 30)
        self.actions = ActionChains(driver)
    
    def find_element(self, locator: tuple, timeout: int = 30) -> Optional[WebElement]:
        """Find single element with timeout"""
        try:
            by, value = locator
            self.logger.debug(f"Finding element: {by}={value}")
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((by, value)))
            self.logger.debug("Element found successfully")
            return element
        except TimeoutException:
            self.logger.error(f"Element not found within {timeout} seconds: {by}={value}")
            return None
        except Exception as e:
            self.logger.error(f"Error finding element: {str(e)}")
            return None
    
    def find_elements(self, locator: tuple, timeout: int = 30) -> List[WebElement]:
        """Find multiple elements with timeout"""
        try:
            by, value = locator
            self.logger.debug(f"Finding elements: {by}={value}")
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.presence_of_element_located((by, value)))
            elements = self.driver.find_elements(by, value)
            self.logger.debug(f"Found {len(elements)} elements")
            return elements
        except TimeoutException:
            self.logger.error(f"Elements not found within {timeout} seconds: {by}={value}")
            return []
        except Exception as e:
            self.logger.error(f"Error finding elements: {str(e)}")
            return []
    
    def click_element(self, locator: tuple, timeout: int = 30) -> bool:
        """Click on element"""
        try:
            element = self.find_element(locator, timeout)
            if element:
                # Wait for element to be clickable
                wait = WebDriverWait(self.driver, timeout)
                clickable_element = wait.until(EC.element_to_be_clickable(locator))
                clickable_element.click()
                self.logger.info(f"Clicked element: {locator[1]}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to click element {locator[1]}: {str(e)}")
            return False
    
    def double_click_element(self, locator: tuple, timeout: int = 30) -> bool:
        """Double click on element"""
        try:
            element = self.find_element(locator, timeout)
            if element:
                self.actions.double_click(element).perform()
                self.logger.info(f"Double clicked element: {locator[1]}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to double click element {locator[1]}: {str(e)}")
            return False
    
    def right_click_element(self, locator: tuple, timeout: int = 30) -> bool:
        """Right click on element"""
        try:
            element = self.find_element(locator, timeout)
            if element:
                self.actions.context_click(element).perform()
                self.logger.info(f"Right clicked element: {locator[1]}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to right click element {locator[1]}: {str(e)}")
            return False
    
    def hover_over_element(self, locator: tuple, timeout: int = 30) -> bool:
        """Hover over element"""
        try:
            element = self.find_element(locator, timeout)
            if element:
                self.actions.move_to_element(element).perform()
                self.logger.info(f"Hovered over element: {locator[1]}")
                time.sleep(1)  # Give time for hover effects
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to hover over element {locator[1]}: {str(e)}")
            return False
    
    def input_text(self, locator: tuple, text: str, clear_first: bool = True, timeout: int = 30) -> bool:
        """Input text into element"""
        try:
            element = self.find_element(locator, timeout)
            if element:
                if clear_first:
                    element.clear()
                element.send_keys(text)
                self.logger.info(f"Entered text '{text}' into element: {locator[1]}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to input text into element {locator[1]}: {str(e)}")
            return False
    
    def clear_text(self, locator: tuple, timeout: int = 30) -> bool:
        """Clear text from element"""
        try:
            element = self.find_element(locator, timeout)
            if element:
                element.clear()
                self.logger.info(f"Cleared text from element: {locator[1]}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to clear text from element {locator[1]}: {str(e)}")
            return False
    
    def get_element_text(self, locator: tuple, timeout: int = 30) -> Optional[str]:
        """Get text from element"""
        try:
            element = self.find_element(locator, timeout)
            if element:
                text = element.text
                self.logger.debug(f"Got text '{text}' from element: {locator[1]}")
                return text
            return None
        except Exception as e:
            self.logger.error(f"Failed to get text from element {locator[1]}: {str(e)}")
            return None
    
    def get_element_attribute(self, locator: tuple, attribute: str, timeout: int = 30) -> Optional[str]:
        """Get attribute value from element"""
        try:
            element = self.find_element(locator, timeout)
            if element:
                value = element.get_attribute(attribute)
                self.logger.debug(f"Got attribute '{attribute}' = '{value}' from element: {locator[1]}")
                return value
            return None
        except Exception as e:
            self.logger.error(f"Failed to get attribute from element {locator[1]}: {str(e)}")
            return None
    
    def is_element_visible(self, locator: tuple, timeout: int = 10) -> bool:
        """Check if element is visible"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.visibility_of_element_located(locator))
            self.logger.debug(f"Element is visible: {locator[1]}")
            return True
        except TimeoutException:
            self.logger.debug(f"Element is not visible: {locator[1]}")
            return False
        except Exception as e:
            self.logger.error(f"Error checking element visibility {locator[1]}: {str(e)}")
            return False
    
    def is_element_present(self, locator: tuple, timeout: int = 10) -> bool:
        """Check if element is present in DOM"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.presence_of_element_located(locator))
            self.logger.debug(f"Element is present: {locator[1]}")
            return True
        except TimeoutException:
            self.logger.debug(f"Element is not present: {locator[1]}")
            return False
        except Exception as e:
            self.logger.error(f"Error checking element presence {locator[1]}: {str(e)}")
            return False
    
    def is_element_clickable(self, locator: tuple, timeout: int = 10) -> bool:
        """Check if element is clickable"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.element_to_be_clickable(locator))
            self.logger.debug(f"Element is clickable: {locator[1]}")
            return True
        except TimeoutException:
            self.logger.debug(f"Element is not clickable: {locator[1]}")
            return False
        except Exception as e:
            self.logger.error(f"Error checking element clickability {locator[1]}: {str(e)}")
            return False
    
    def wait_for_element_to_disappear(self, locator: tuple, timeout: int = 30) -> bool:
        """Wait for element to disappear from DOM"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until_not(EC.presence_of_element_located(locator))
            self.logger.info(f"Element disappeared: {locator[1]}")
            return True
        except TimeoutException:
            self.logger.warning(f"Element did not disappear within {timeout} seconds: {locator[1]}")
            return False
        except Exception as e:
            self.logger.error(f"Error waiting for element to disappear {locator[1]}: {str(e)}")
            return False
    
    def select_dropdown_option(self, locator: tuple, option_text: str = None, 
                             option_value: str = None, option_index: int = None, 
                             timeout: int = 30) -> bool:
        """Select option from dropdown"""
        try:
            element = self.find_element(locator, timeout)
            if element:
                select = Select(element)
                
                if option_text:
                    select.select_by_visible_text(option_text)
                    self.logger.info(f"Selected dropdown option by text: {option_text}")
                elif option_value:
                    select.select_by_value(option_value)
                    self.logger.info(f"Selected dropdown option by value: {option_value}")
                elif option_index is not None:
                    select.select_by_index(option_index)
                    self.logger.info(f"Selected dropdown option by index: {option_index}")
                else:
                    self.logger.error("No selection criteria provided for dropdown")
                    return False
                
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to select dropdown option: {str(e)}")
            return False
    
    def get_dropdown_options(self, locator: tuple, timeout: int = 30) -> List[str]:
        """Get all options from dropdown"""
        try:
            element = self.find_element(locator, timeout)
            if element:
                select = Select(element)
                options = [option.text for option in select.options]
                self.logger.debug(f"Found {len(options)} dropdown options")
                return options
            return []
        except Exception as e:
            self.logger.error(f"Failed to get dropdown options: {str(e)}")
            return []
    
    def scroll_to_element(self, locator: tuple, timeout: int = 30) -> bool:
        """Scroll element into view"""
        try:
            element = self.find_element(locator, timeout)
            if element:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(1)  # Give time for scroll
                self.logger.info(f"Scrolled to element: {locator[1]}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to scroll to element {locator[1]}: {str(e)}")
            return False
    
    def send_keys_to_element(self, locator: tuple, keys: str, timeout: int = 30) -> bool:
        """Send special keys to element"""
        try:
            element = self.find_element(locator, timeout)
            if element:
                element.send_keys(keys)
                self.logger.info(f"Sent keys '{keys}' to element: {locator[1]}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to send keys to element {locator[1]}: {str(e)}")
            return False
    
    def click_at_coordinates(self, x: int, y: int) -> bool:
        """Click at specific coordinates"""
        try:
            self.actions.move_by_offset(x, y).click().perform()
            self.logger.info(f"Clicked at coordinates: ({x}, {y})")
            return True
        except Exception as e:
            self.logger.error(f"Failed to click at coordinates ({x}, {y}): {str(e)}")
            return False
    
    def drag_and_drop(self, source_locator: tuple, target_locator: tuple, timeout: int = 30) -> bool:
        """Drag element from source to target"""
        try:
            source = self.find_element(source_locator, timeout)
            target = self.find_element(target_locator, timeout)
            
            if source and target:
                self.actions.drag_and_drop(source, target).perform()
                self.logger.info(f"Dragged element from {source_locator[1]} to {target_locator[1]}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to drag and drop: {str(e)}")
            return False
    
    def get_element_count(self, locator: tuple, timeout: int = 10) -> int:
        """Get count of elements matching locator"""
        try:
            elements = self.find_elements(locator, timeout)
            count = len(elements)
            self.logger.debug(f"Found {count} elements for locator: {locator[1]}")
            return count
        except Exception as e:
            self.logger.error(f"Failed to get element count: {str(e)}")
            return 0
