"""
Action Executor
Executes individual test steps with screenshot capture and error handling
"""

import time
from datetime import datetime
from typing import Dict, Any, List, Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

from framework.core.assertion_engine import AssertionEngine
from framework.reporting.screenshot_manager import ScreenshotManager
from framework.utils.logger import Logger
from framework.core.scenario_parser import ScenarioParser


class ActionExecutor:
    def __init__(self, driver: webdriver.Remote, config: Dict[str, Any]):
        """Initialize Action Executor"""
        self.driver = driver
        self.config = config
        self.logger = Logger()
        self.assertion_engine = AssertionEngine(driver)
        self.screenshot_manager = ScreenshotManager(config)
        self.scenario_parser = ScenarioParser()
        self.wait = WebDriverWait(
            driver, 
            config.get('framework_config', {}).get('explicit_wait', 30)
        )
        
    def execute_step(self, step: Dict[str, Any], test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single test step"""
        step_start = datetime.now()
        
        # Prepare step with variable substitution
        prepared_step = self.scenario_parser.prepare_step_data(step, test_data)
        
        step_result = {
            'step_id': step.get('step_id'),
            'step_name': step.get('step_name'),
            'action': step.get('action'),
            'target': prepared_step.get('target'),
            'value': prepared_step.get('value'),
            'start_time': step_start.isoformat(),
            'status': 'running',
            'error': None,
            'screenshot_path': None,
            'duration': 0
        }
        
        try:
            self.logger.info(f"Executing step: {step_result['step_name']}")
            
            # Execute the action
            self._execute_action(prepared_step)
            
            # Wait if specified
            wait_time = step.get('wait_time', 0)
            if wait_time > 0:
                time.sleep(wait_time)
            
            step_result['status'] = 'passed'
            
        except Exception as e:
            self.logger.error(f"Step failed: {step_result['step_name']} - {str(e)}")
            step_result['status'] = 'failed'
            step_result['error'] = str(e)
        
        finally:
            # Take screenshot if configured
            if (step.get('screenshot', False) or 
                step_result['status'] == 'failed' or
                self.config.get('framework_config', {}).get('screenshot_on_step', False)):
                
                screenshot_path = self.screenshot_manager.capture_step_screenshot(
                    self.driver,
                    step_result['step_id'],
                    step_result['step_name'],
                    step_result['status']
                )
                step_result['screenshot_path'] = screenshot_path
            
            # Calculate duration
            step_end = datetime.now()
            step_result['end_time'] = step_end.isoformat()
            step_result['duration'] = (step_end - step_start).total_seconds()
        
        return step_result
    
    def _execute_action(self, step: Dict[str, Any]):
        """Execute specific action based on action type"""
        action = step.get('action', '').lower()
        target = step.get('target', '')
        value = step.get('value', '')
        
        # Navigation actions
        if action == 'navigate':
            self._navigate(value)
        elif action == 'refresh':
            self._refresh()
        elif action == 'back':
            self._back()
        elif action == 'forward':
            self._forward()
        
        # Element interaction actions
        elif action == 'click':
            self._click(target)
        elif action == 'double_click':
            self._double_click(target)
        elif action == 'right_click':
            self._right_click(target)
        elif action == 'input_text':
            self._input_text(target, value)
        elif action == 'clear_text':
            self._clear_text(target)
        elif action == 'select_dropdown':
            self._select_dropdown(target, value)
        elif action == 'hover':
            self._hover(target)
        
        # Assertion actions
        elif action.startswith('assert_'):
            self._execute_assertion(action, target, value)
        
        # Wait actions
        elif action == 'wait_for_element':
            self._wait_for_element(target)
        elif action == 'wait_for_text':
            self._wait_for_text(target, value)
        elif action == 'wait':
            self._wait(float(value) if value else 1)
        
        # JavaScript actions
        elif action == 'execute_script':
            self._execute_script(value)
        
        else:
            raise ValueError(f"Unsupported action: {action}")
    
    # Navigation Actions
    def _navigate(self, url: str):
        """Navigate to URL"""
        self.driver.get(url)
    
    def _refresh(self):
        """Refresh page"""
        self.driver.refresh()
    
    def _back(self):
        """Go back"""
        self.driver.back()
    
    def _forward(self):
        """Go forward"""
        self.driver.forward()
    
    # Element Interaction Actions
    def _click(self, target: str):
        """Click element"""
        element = self._find_element(target)
        element.click()
    
    def _double_click(self, target: str):
        """Double click element"""
        element = self._find_element(target)
        ActionChains(self.driver).double_click(element).perform()
    
    def _right_click(self, target: str):
        """Right click element"""
        element = self._find_element(target)
        ActionChains(self.driver).context_click(element).perform()
    
    def _input_text(self, target: str, text: str):
        """Input text into element"""
        element = self._find_element(target)
        element.clear()
        element.send_keys(text)
    
    def _clear_text(self, target: str):
        """Clear text from element"""
        element = self._find_element(target)
        element.clear()
    
    def _select_dropdown(self, target: str, value: str):
        """Select dropdown option"""
        from selenium.webdriver.support.ui import Select
        element = self._find_element(target)
        select = Select(element)
        try:
            select.select_by_value(value)
        except:
            select.select_by_visible_text(value)
    
    def _hover(self, target: str):
        """Hover over element"""
        element = self._find_element(target)
        ActionChains(self.driver).move_to_element(element).perform()
    
    # Assertion Actions
    def _execute_assertion(self, action: str, target: str, value: str):
        """Execute assertion"""
        if action == 'assert_element_visible':
            self.assertion_engine.assert_element_visible(target)
        elif action == 'assert_element_text':
            self.assertion_engine.assert_element_text(target, value)
        elif action == 'assert_element_count':
            self.assertion_engine.assert_element_count(target, int(value))
        elif action == 'assert_url_contains':
            self.assertion_engine.assert_url_contains(value)
        elif action == 'assert_title_contains':
            self.assertion_engine.assert_title_contains(value)
        else:
            raise ValueError(f"Unsupported assertion: {action}")
    
    # Wait Actions
    def _wait_for_element(self, target: str):
        """Wait for element to be present"""
        by, locator = self._parse_target(target)
        self.wait.until(EC.presence_of_element_located((by, locator)))
    
    def _wait_for_text(self, target: str, text: str):
        """Wait for element to contain text"""
        by, locator = self._parse_target(target)
        self.wait.until(EC.text_to_be_present_in_element((by, locator), text))
    
    def _wait(self, seconds: float):
        """Wait for specified seconds"""
        time.sleep(seconds)
    
    # JavaScript Actions
    def _execute_script(self, script: str):
        """Execute JavaScript"""
        self.driver.execute_script(script)
    
    # Helper Methods
    def _find_element(self, target: str):
        """Find element using target selector"""
        by, locator = self._parse_target(target)
        return self.wait.until(EC.presence_of_element_located((by, locator)))
    
    def _find_elements(self, target: str):
        """Find multiple elements using target selector"""
        by, locator = self._parse_target(target)
        return self.driver.find_elements(by, locator)
    
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
