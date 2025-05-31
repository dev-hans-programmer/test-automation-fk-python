"""
Scenario Parser
Parses JSON scenario files and test data files with variable substitution
"""

import json
import re
from typing import Dict, Any, List

from framework.utils.logger import Logger


class ScenarioParser:
    def __init__(self):
        """Initialize Scenario Parser"""
        self.logger = Logger()
        
    def parse_scenario(self, scenario_file: str) -> Dict[str, Any]:
        """Parse scenario JSON file"""
        try:
            with open(scenario_file, 'r') as file:
                scenario = json.load(file)
            
            self.logger.info(f"Parsed scenario: {scenario['scenario_info']['name']}")
            return scenario
            
        except Exception as e:
            self.logger.error(f"Failed to parse scenario file {scenario_file}: {str(e)}")
            raise
    
    def parse_test_data(self, test_data_file: str) -> Dict[str, Any]:
        """Parse test data JSON file"""
        try:
            with open(test_data_file, 'r') as file:
                test_data = json.load(file)
            
            self.logger.info(f"Parsed test data from: {test_data_file}")
            return test_data
            
        except Exception as e:
            self.logger.error(f"Failed to parse test data file {test_data_file}: {str(e)}")
            raise
    
    def substitute_variables(self, text: str, test_data: Dict[str, Any]) -> str:
        """Substitute variables in text using ${variable} syntax"""
        if not isinstance(text, str):
            return text
        
        # Find all variables in ${variable} format
        variables = re.findall(r'\$\{([^}]+)\}', text)
        
        for variable in variables:
            # Support nested object access with dot notation
            value = self._get_nested_value(test_data, variable)
            if value is not None:
                text = text.replace(f'${{{variable}}}', str(value))
            else:
                self.logger.warning(f"Variable '{variable}' not found in test data")
        
        return text
    
    def _get_nested_value(self, data: Dict[str, Any], key_path: str) -> Any:
        """Get value from nested dictionary using dot notation"""
        try:
            keys = key_path.split('.')
            value = data
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None
            
            return value
            
        except Exception:
            return None
    
    def prepare_step_data(self, step: Dict[str, Any], test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare step with substituted variables"""
        prepared_step = step.copy()
        
        # Substitute variables in target and value fields
        if 'target' in prepared_step:
            prepared_step['target'] = self.substitute_variables(
                prepared_step['target'], test_data
            )
        
        if 'value' in prepared_step:
            prepared_step['value'] = self.substitute_variables(
                prepared_step['value'], test_data
            )
        
        return prepared_step
    
    def validate_scenario_structure(self, scenario: Dict[str, Any]) -> bool:
        """Validate scenario structure"""
        required_fields = ['scenario_info', 'test_steps']
        
        for field in required_fields:
            if field not in scenario:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        # Validate scenario_info
        info_required = ['name', 'description', 'url']
        for field in info_required:
            if field not in scenario['scenario_info']:
                self.logger.error(f"Missing scenario_info field: {field}")
                return False
        
        # Validate test_steps
        if not isinstance(scenario['test_steps'], list):
            self.logger.error("test_steps must be a list")
            return False
        
        for i, step in enumerate(scenario['test_steps']):
            if not self._validate_step_structure(step, i):
                return False
        
        return True
    
    def _validate_step_structure(self, step: Dict[str, Any], step_index: int) -> bool:
        """Validate individual step structure"""
        required_fields = ['step_id', 'step_name', 'action']
        
        for field in required_fields:
            if field not in step:
                self.logger.error(f"Step {step_index}: Missing required field: {field}")
                return False
        
        # Validate step_id is unique and sequential
        if not isinstance(step['step_id'], int) or step['step_id'] != step_index + 1:
            self.logger.error(f"Step {step_index}: Invalid step_id")
            return False
        
        return True
