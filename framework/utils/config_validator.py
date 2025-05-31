"""
Configuration Validator
Validates JSON configuration files and schemas
"""

import json
import os
from typing import Dict, Any, List

from framework.utils.logger import Logger


class ConfigValidator:
    def __init__(self):
        """Initialize Configuration Validator"""
        self.logger = Logger()
        
    def validate_master_config(self, config: Dict[str, Any]) -> bool:
        """Validate master configuration file"""
        try:
            # Check required sections
            required_sections = ['framework_config', 'reporting', 'test_scenarios']
            for section in required_sections:
                if section not in config:
                    self.logger.error(f"Missing required section: {section}")
                    return False
            
            # Validate framework_config
            if not self._validate_framework_config(config['framework_config']):
                return False
            
            # Validate reporting config
            if not self._validate_reporting_config(config['reporting']):
                return False
            
            # Validate test scenarios
            if not self._validate_test_scenarios_config(config['test_scenarios']):
                return False
            
            self.logger.info("Master configuration validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Master config validation failed: {str(e)}")
            return False
    
    def _validate_framework_config(self, framework_config: Dict[str, Any]) -> bool:
        """Validate framework configuration section"""
        required_fields = ['browser', 'implicit_wait', 'explicit_wait']
        
        for field in required_fields:
            if field not in framework_config:
                self.logger.error(f"Missing framework_config field: {field}")
                return False
        
        # Validate browser
        valid_browsers = ['chrome', 'firefox']
        if framework_config['browser'].lower() not in valid_browsers:
            self.logger.error(f"Invalid browser: {framework_config['browser']}")
            return False
        
        # Validate wait times
        for wait_field in ['implicit_wait', 'explicit_wait']:
            if not isinstance(framework_config[wait_field], (int, float)) or framework_config[wait_field] <= 0:
                self.logger.error(f"Invalid {wait_field}: must be positive number")
                return False
        
        return True
    
    def _validate_reporting_config(self, reporting_config: Dict[str, Any]) -> bool:
        """Validate reporting configuration section"""
        required_fields = ['json_reports', 'word_reports', 'report_directory', 'screenshot_directory']
        
        for field in required_fields:
            if field not in reporting_config:
                self.logger.error(f"Missing reporting field: {field}")
                return False
        
        # Validate boolean fields
        boolean_fields = ['json_reports', 'word_reports', 'screenshot_embedding']
        for field in boolean_fields:
            if field in reporting_config and not isinstance(reporting_config[field], bool):
                self.logger.error(f"Invalid {field}: must be boolean")
                return False
        
        return True
    
    def _validate_test_scenarios_config(self, scenarios: List[Dict[str, Any]]) -> bool:
        """Validate test scenarios configuration"""
        if not isinstance(scenarios, list):
            self.logger.error("test_scenarios must be a list")
            return False
        
        if not scenarios:
            self.logger.warning("No test scenarios defined")
            return True
        
        required_fields = ['name', 'scenario_file', 'test_data_file', 'execute']
        
        for i, scenario in enumerate(scenarios):
            for field in required_fields:
                if field not in scenario:
                    self.logger.error(f"Scenario {i}: Missing required field: {field}")
                    return False
            
            # Validate execute field
            if scenario['execute'].lower() not in ['y', 'n']:
                self.logger.error(f"Scenario {i}: execute must be 'y' or 'n'")
                return False
            
            # Check if files exist
            if not os.path.exists(scenario['scenario_file']):
                self.logger.error(f"Scenario {i}: scenario_file not found: {scenario['scenario_file']}")
                return False
            
            if not os.path.exists(scenario['test_data_file']):
                self.logger.error(f"Scenario {i}: test_data_file not found: {scenario['test_data_file']}")
                return False
        
        return True
    
    def validate_scenario_file(self, scenario_file: str) -> bool:
        """Validate individual scenario file"""
        try:
            if not os.path.exists(scenario_file):
                self.logger.error(f"Scenario file not found: {scenario_file}")
                return False
            
            with open(scenario_file, 'r') as file:
                scenario = json.load(file)
            
            # Check required sections
            if 'scenario_info' not in scenario:
                self.logger.error(f"Missing scenario_info in {scenario_file}")
                return False
            
            if 'test_steps' not in scenario:
                self.logger.error(f"Missing test_steps in {scenario_file}")
                return False
            
            # Validate scenario_info
            if not self._validate_scenario_info(scenario['scenario_info'], scenario_file):
                return False
            
            # Validate test_steps
            if not self._validate_test_steps(scenario['test_steps'], scenario_file):
                return False
            
            self.logger.info(f"Scenario file validation passed: {scenario_file}")
            return True
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in scenario file {scenario_file}: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Scenario file validation failed {scenario_file}: {str(e)}")
            return False
    
    def _validate_scenario_info(self, scenario_info: Dict[str, Any], filename: str) -> bool:
        """Validate scenario_info section"""
        required_fields = ['name', 'description', 'url']
        
        for field in required_fields:
            if field not in scenario_info:
                self.logger.error(f"Missing scenario_info field in {filename}: {field}")
                return False
        
        # Validate URL format (basic validation)
        url = scenario_info['url']
        if not url.startswith(('http://', 'https://')):
            self.logger.error(f"Invalid URL format in {filename}: {url}")
            return False
        
        return True
    
    def _validate_test_steps(self, test_steps: List[Dict[str, Any]], filename: str) -> bool:
        """Validate test_steps section"""
        if not isinstance(test_steps, list):
            self.logger.error(f"test_steps must be a list in {filename}")
            return False
        
        if not test_steps:
            self.logger.error(f"test_steps cannot be empty in {filename}")
            return False
        
        required_fields = ['step_id', 'step_name', 'action']
        valid_actions = [
            'navigate', 'click', 'input_text', 'clear_text', 'select_dropdown',
            'hover', 'double_click', 'right_click', 'wait', 'wait_for_element',
            'wait_for_text', 'execute_script', 'assert_element_visible',
            'assert_element_text', 'assert_element_count', 'assert_url_contains',
            'assert_title_contains', 'refresh', 'back', 'forward'
        ]
        
        for i, step in enumerate(test_steps):
            # Check required fields
            for field in required_fields:
                if field not in step:
                    self.logger.error(f"Step {i} in {filename}: Missing required field: {field}")
                    return False
            
            # Validate step_id
            if not isinstance(step['step_id'], int) or step['step_id'] <= 0:
                self.logger.error(f"Step {i} in {filename}: Invalid step_id")
                return False
            
            # Validate action
            if step['action'] not in valid_actions:
                self.logger.error(f"Step {i} in {filename}: Invalid action: {step['action']}")
                return False
        
        return True
    
    def validate_test_data_file(self, test_data_file: str) -> bool:
        """Validate test data file"""
        try:
            if not os.path.exists(test_data_file):
                self.logger.error(f"Test data file not found: {test_data_file}")
                return False
            
            with open(test_data_file, 'r') as file:
                test_data = json.load(file)
            
            # Basic validation - must be a dictionary
            if not isinstance(test_data, dict):
                self.logger.error(f"Test data must be a JSON object in {test_data_file}")
                return False
            
            # Check for common required fields
            if 'url' not in test_data:
                self.logger.warning(f"Test data missing 'url' field in {test_data_file}")
            
            self.logger.info(f"Test data file validation passed: {test_data_file}")
            return True
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in test data file {test_data_file}: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Test data file validation failed {test_data_file}: {str(e)}")
            return False
