"""
Custom Logger
Centralized logging system for the framework
"""

import logging
import os
from datetime import datetime
from typing import Optional


class Logger:
    _instance: Optional['Logger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls):
        """Singleton pattern for logger"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance
    
    def _initialize_logger(self):
        """Initialize logging configuration"""
        if self._logger is not None:
            return
        
        # Create logs directory
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)
        
        # Configure logger
        self._logger = logging.getLogger('TestAutomationFramework')
        self._logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self._logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # File handler for detailed logs
        log_filename = datetime.now().strftime("test_automation_%Y%m%d.log")
        file_handler = logging.FileHandler(
            os.path.join(log_dir, log_filename),
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        
        # Console handler for important messages
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        
        # Add handlers
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)
        
    def debug(self, message: str):
        """Log debug message"""
        self._logger.debug(message)
    
    def info(self, message: str):
        """Log info message"""
        self._logger.info(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self._logger.warning(message)
    
    def error(self, message: str):
        """Log error message"""
        self._logger.error(message)
    
    def critical(self, message: str):
        """Log critical message"""
        self._logger.critical(message)
    
    def log_test_start(self, test_name: str):
        """Log test start"""
        self.info(f"=" * 50)
        self.info(f"Starting test: {test_name}")
        self.info(f"=" * 50)
    
    def log_test_end(self, test_name: str, status: str, duration: float):
        """Log test end"""
        self.info(f"Test completed: {test_name}")
        self.info(f"Status: {status}")
        self.info(f"Duration: {duration:.2f} seconds")
        self.info(f"=" * 50)
    
    def log_step(self, step_name: str, action: str, target: str, value: str = ""):
        """Log test step"""
        self.info(f"Executing step: {step_name}")
        self.debug(f"Action: {action}, Target: {target}, Value: {value}")
    
    def log_assertion(self, assertion_type: str, expected: str, actual: str, passed: bool):
        """Log assertion result"""
        status = "PASSED" if passed else "FAILED"
        self.info(f"Assertion {status}: {assertion_type}")
        if not passed:
            self.error(f"Expected: {expected}, Actual: {actual}")
    
    def log_error_with_screenshot(self, error_message: str, screenshot_path: str = ""):
        """Log error with screenshot information"""
        self.error(f"Error occurred: {error_message}")
        if screenshot_path:
            self.info(f"Screenshot captured: {screenshot_path}")
    
    def get_log_file_path(self) -> str:
        """Get current log file path"""
        log_filename = datetime.now().strftime("test_automation_%Y%m%d.log")
        return os.path.join('logs', log_filename)
    
    def cleanup_old_logs(self, days_old: int = 30):
        """Clean up log files older than specified days"""
        try:
            log_dir = 'logs'
            if not os.path.exists(log_dir):
                return
            
            cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            deleted_count = 0
            
            for filename in os.listdir(log_dir):
                if filename.startswith('test_automation_') and filename.endswith('.log'):
                    filepath = os.path.join(log_dir, filename)
                    if os.path.getctime(filepath) < cutoff_time:
                        os.remove(filepath)
                        deleted_count += 1
            
            if deleted_count > 0:
                self.info(f"Cleaned up {deleted_count} old log files")
                
        except Exception as e:
            self.error(f"Failed to cleanup old logs: {str(e)}")
