"""
Core Test Engine
Orchestrates test execution, manages scenarios and generates reports
"""

import json
import time
import traceback
from datetime import datetime
from typing import Dict, List, Any

from framework.core.scenario_parser import ScenarioParser
from framework.core.web_driver_manager import WebDriverManager
from framework.core.action_executor import ActionExecutor
from framework.reporting.json_reporter import JsonReporter
from framework.reporting.word_reporter import WordReporter
from framework.reporting.video_recorder import VideoRecorder
from framework.utils.logger import Logger
from framework.utils.config_validator import ConfigValidator
from framework.utils.environment_manager import EnvironmentManager


class TestEngine:
    def __init__(self, config_path: str = "config/master_config.json"):
        """Initialize Test Engine with configuration"""
        self.config_path = config_path
        self.config = self._load_config()
        self.logger = Logger()
        self.validator = ConfigValidator()
        self.driver_manager = WebDriverManager(self.config)
        self.scenario_parser = ScenarioParser()
        self.action_executor = None
        self.json_reporter = JsonReporter(self.config)
        self.word_reporter = WordReporter(self.config)
        self.video_recorder = VideoRecorder(self.config)
        self.environment_manager = EnvironmentManager()
        
        # Execution state
        self.current_execution = None
        self.execution_results = []
        self.current_environment = None
        self.environment_data = {}
        
    def _load_config(self) -> Dict[str, Any]:
        """Load master configuration file"""
        try:
            with open(self.config_path, 'r') as file:
                return json.load(file)
        except Exception as e:
            raise Exception(f"Failed to load config: {str(e)}")
    
    def validate_configuration(self) -> bool:
        """Validate all configuration files"""
        try:
            # Validate master config
            if not self.validator.validate_master_config(self.config):
                return False
            
            # Validate scenario files
            for scenario in self.config['test_scenarios']:
                scenario_path = scenario['scenario_file']
                if not self.validator.validate_scenario_file(scenario_path):
                    return False
                    
                test_data_path = scenario['test_data_file']
                if not self.validator.validate_test_data_file(test_data_path):
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {str(e)}")
            return False
    
    def get_executable_scenarios(self) -> List[Dict[str, Any]]:
        """Get list of scenarios marked for execution"""
        executable = []
        for scenario in self.config['test_scenarios']:
            if scenario.get('execute', 'n').lower() == 'y':
                executable.append(scenario)
        
        # Sort by priority
        executable.sort(key=lambda x: x.get('priority', 999))
        return executable
    
    def execute_all_scenarios(self, progress_callback=None) -> Dict[str, Any]:
        """Execute all enabled scenarios sequentially"""
        self.logger.info("Starting test execution")
        
        execution_start = datetime.now()
        self.current_execution = {
            'execution_id': f"exec_{int(time.time())}",
            'start_time': execution_start.isoformat(),
            'scenarios': [],
            'status': 'running',
            'total_scenarios': 0,
            'passed_scenarios': 0,
            'failed_scenarios': 0
        }
        
        try:
            # Validate configuration
            if not self.validate_configuration():
                raise Exception("Configuration validation failed")
            
            # Get executable scenarios
            scenarios = self.get_executable_scenarios()
            self.current_execution['total_scenarios'] = len(scenarios)
            
            if not scenarios:
                self.logger.warning("No scenarios marked for execution")
                return self.current_execution
            
            # Initialize WebDriver
            self.driver_manager.initialize_driver()
            self.action_executor = ActionExecutor(
                self.driver_manager.driver, 
                self.config
            )
            
            # Execute each scenario
            for i, scenario_config in enumerate(scenarios):
                if progress_callback:
                    progress_callback(i, len(scenarios), scenario_config['name'])
                
                scenario_result = self.execute_scenario(scenario_config)
                self.current_execution['scenarios'].append(scenario_result)
                
                if scenario_result['status'] == 'passed':
                    self.current_execution['passed_scenarios'] += 1
                else:
                    self.current_execution['failed_scenarios'] += 1
            
        except Exception as e:
            self.logger.error(f"Execution failed: {str(e)}")
            self.current_execution['error'] = str(e)
            self.current_execution['status'] = 'error'
            
        finally:
            # Cleanup
            if self.driver_manager.driver:
                self.driver_manager.quit_driver()
            
            # Finalize execution
            execution_end = datetime.now()
            self.current_execution['end_time'] = execution_end.isoformat()
            self.current_execution['duration'] = (execution_end - execution_start).total_seconds()
            
            if self.current_execution['status'] == 'running':
                self.current_execution['status'] = 'completed'
            
            # Generate reports
            self._generate_reports()
        
        return self.current_execution
    
    def execute_scenario(self, scenario_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single scenario"""
        scenario_name = scenario_config['name']
        self.logger.info(f"Executing scenario: {scenario_name}")
        
        scenario_start = datetime.now()
        scenario_result = {
            'scenario_name': scenario_name,
            'scenario_file': scenario_config['scenario_file'],
            'start_time': scenario_start.isoformat(),
            'steps': [],
            'status': 'running',
            'error': None
        }
        
        video_path = None
        
        try:
            # Start video recording if enabled
            if self.config.get('framework_config', {}).get('video_recording', False):
                video_started = self.video_recorder.start_recording(scenario_name)
                if video_started:
                    self.logger.info(f"Video recording started for scenario: {scenario_name}")
            
            # Parse scenario and test data
            scenario = self.scenario_parser.parse_scenario(
                scenario_config['scenario_file']
            )
            test_data = self.scenario_parser.parse_test_data(
                scenario_config['test_data_file']
            )
            
            # Execute each step
            for step in scenario['test_steps']:
                step_result = self.action_executor.execute_step(step, test_data)
                scenario_result['steps'].append(step_result)
                
                # Stop on failure if configured
                if (step_result['status'] == 'failed' and 
                    not self.config.get('continue_on_failure', False)):
                    break
            
            # Determine scenario status
            failed_steps = [s for s in scenario_result['steps'] if s['status'] == 'failed']
            scenario_result['status'] = 'failed' if failed_steps else 'passed'
            
        except Exception as e:
            self.logger.error(f"Scenario execution failed: {str(e)}")
            scenario_result['status'] = 'failed'
            scenario_result['error'] = str(e)
            scenario_result['traceback'] = traceback.format_exc()
        
        finally:
            # Stop video recording if it was started
            if self.config.get('framework_config', {}).get('video_recording', False):
                video_path = self.video_recorder.stop_recording()
                if video_path:
                    scenario_result['video_path'] = video_path
                    self.logger.info(f"Video recording saved: {video_path}")
            
            scenario_end = datetime.now()
            scenario_result['end_time'] = scenario_end.isoformat()
            scenario_result['duration'] = (scenario_end - scenario_start).total_seconds()
        
        return scenario_result
    
    def _generate_reports(self):
        """Generate JSON and Word reports"""
        try:
            if self.config['reporting']['json_reports']:
                self.json_reporter.generate_report(self.current_execution)
            
            if self.config['reporting']['word_reports']:
                self.word_reporter.generate_report(self.current_execution)
                
        except Exception as e:
            self.logger.error(f"Report generation failed: {str(e)}")
    
    def get_execution_status(self) -> Dict[str, Any]:
        """Get current execution status"""
        return self.current_execution
    
    def stop_execution(self):
        """Stop current execution"""
        if self.current_execution and self.current_execution['status'] == 'running':
            self.current_execution['status'] = 'stopped'
            if self.driver_manager.driver:
                self.driver_manager.quit_driver()
    
    def set_environment_data(self, environment_id: str, environment_data: Dict[str, Any]):
        """Set environment-specific data for test execution"""
        self.current_environment = environment_id
        self.environment_data = environment_data
        self.logger.info(f"Environment data set for: {environment_id}")
        
        # Update driver manager with environment-specific browser settings
        browser_settings = environment_data.get('browser_settings', {})
        if browser_settings:
            self.driver_manager.update_browser_settings(browser_settings)
    
    def get_current_environment(self) -> str:
        """Get current environment ID"""
        return self.current_environment
    
    def get_environment_data(self) -> Dict[str, Any]:
        """Get current environment data"""
        return self.environment_data.copy()
    
    def get_environment_specific_data(self, data_type: str) -> Any:
        """Get environment-specific data by type"""
        return self.environment_data.get(data_type, {})
    
    def prepare_test_data_with_environment(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare test data with environment-specific substitutions"""
        if not self.environment_data:
            return test_data
            
        # Merge environment test data with scenario test data
        env_test_data = self.environment_data.get('test_data', {})
        merged_data = {**env_test_data, **test_data}
        
        # Add environment-specific URLs and endpoints
        merged_data['base_url'] = self.environment_data.get('base_url', '')
        merged_data['api_endpoints'] = self.environment_data.get('api_endpoints', {})
        merged_data['credentials'] = self.environment_data.get('credentials', {})
        merged_data['feature_flags'] = self.environment_data.get('feature_flags', {})
        
        # Substitute environment variables using environment manager
        return self.environment_manager.prepare_environment_data(merged_data)
