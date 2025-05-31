"""
Environment Manager
Handles environment-specific configurations and data sets
"""

import json
import os
import re
from typing import Dict, List, Any, Optional
from framework.utils.logger import Logger


class EnvironmentManager:
    def __init__(self):
        """Initialize Environment Manager"""
        self.logger = Logger()
        self.environments_dir = "config/environments"
        self.current_environment = None
        self.environment_data = {}
        
    def load_available_environments(self) -> List[Dict[str, str]]:
        """Load list of available environments"""
        environments = []
        
        if not os.path.exists(self.environments_dir):
            self.logger.warning(f"Environments directory not found: {self.environments_dir}")
            return environments
            
        try:
            for filename in os.listdir(self.environments_dir):
                if filename.endswith('.json'):
                    env_path = os.path.join(self.environments_dir, filename)
                    with open(env_path, 'r', encoding='utf-8') as f:
                        env_data = json.load(f)
                        
                    environments.append({
                        'id': env_data.get('environment_id', filename.replace('.json', '')),
                        'name': env_data.get('environment_name', 'Unknown'),
                        'description': env_data.get('description', ''),
                        'file_path': env_path
                    })
                    
        except Exception as e:
            self.logger.error(f"Failed to load environments: {str(e)}")
            
        return environments
        
    def load_environment(self, environment_id: str) -> bool:
        """Load specific environment configuration"""
        try:
            env_file = os.path.join(self.environments_dir, f"{environment_id}_environment.json")
            
            if not os.path.exists(env_file):
                self.logger.error(f"Environment file not found: {env_file}")
                return False
                
            with open(env_file, 'r', encoding='utf-8') as f:
                self.environment_data = json.load(f)
                
            self.current_environment = environment_id
            self.logger.info(f"Loaded environment: {environment_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load environment {environment_id}: {str(e)}")
            return False
            
    def get_environment_data(self) -> Dict[str, Any]:
        """Get current environment data"""
        return self.environment_data.copy()
        
    def get_base_url(self) -> str:
        """Get base URL for current environment"""
        return self.environment_data.get('base_url', '')
        
    def get_timeout_settings(self) -> Dict[str, int]:
        """Get timeout settings for current environment"""
        return self.environment_data.get('timeout_settings', {
            'page_load_timeout': 30,
            'element_wait_timeout': 15,
            'script_timeout': 10
        })
        
    def get_browser_settings(self) -> Dict[str, Any]:
        """Get browser settings for current environment"""
        return self.environment_data.get('browser_settings', {
            'window_size': {'width': 1920, 'height': 1080},
            'headless': False,
            'incognito': True
        })
        
    def get_credentials(self, credential_type: str = None) -> Dict[str, Any]:
        """Get credentials for current environment"""
        credentials = self.environment_data.get('credentials', {})
        
        if credential_type:
            return credentials.get(credential_type, {})
        return credentials
        
    def get_test_data(self, data_type: str = None) -> Dict[str, Any]:
        """Get test data for current environment"""
        test_data = self.environment_data.get('test_data', {})
        
        if data_type:
            return test_data.get(data_type, [])
        return test_data
        
    def get_api_endpoints(self) -> Dict[str, str]:
        """Get API endpoints for current environment"""
        return self.environment_data.get('api_endpoints', {})
        
    def get_feature_flags(self) -> Dict[str, bool]:
        """Get feature flags for current environment"""
        return self.environment_data.get('feature_flags', {})
        
    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if specific feature is enabled in current environment"""
        feature_flags = self.get_feature_flags()
        return feature_flags.get(feature_name, False)
        
    def substitute_environment_variables(self, text: str) -> str:
        """Substitute environment variables in text using ${VAR} syntax"""
        if not isinstance(text, str):
            return text
            
        # Find all ${VARIABLE} patterns
        pattern = r'\$\{([^}]+)\}'
        matches = re.findall(pattern, text)
        
        for var_name in matches:
            # Get value from environment variables
            env_value = os.environ.get(var_name, '')
            if env_value:
                text = text.replace(f'${{{var_name}}}', env_value)
            else:
                self.logger.warning(f"Environment variable not found: {var_name}")
                
        return text
        
    def prepare_environment_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data with environment variable substitution"""
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                result[key] = self.prepare_environment_data(value)
            return result
        elif isinstance(data, list):
            return [self.prepare_environment_data(item) for item in data]
        elif isinstance(data, str):
            return self.substitute_environment_variables(data)
        else:
            return data
            
    def get_environment_specific_url(self, path: str = '') -> str:
        """Get full URL by combining base URL with path"""
        base_url = self.get_base_url().rstrip('/')
        path = path.lstrip('/')
        
        if path:
            return f"{base_url}/{path}"
        return base_url
        
    def validate_environment_config(self, environment_id: str) -> Dict[str, Any]:
        """Validate environment configuration"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            env_file = os.path.join(self.environments_dir, f"{environment_id}_environment.json")
            
            if not os.path.exists(env_file):
                validation_result['valid'] = False
                validation_result['errors'].append(f"Environment file not found: {env_file}")
                return validation_result
                
            with open(env_file, 'r', encoding='utf-8') as f:
                env_data = json.load(f)
                
            # Check required fields
            required_fields = ['environment_name', 'environment_id', 'base_url']
            for field in required_fields:
                if field not in env_data:
                    validation_result['errors'].append(f"Missing required field: {field}")
                    
            # Check base URL format
            base_url = env_data.get('base_url', '')
            if base_url and not (base_url.startswith('http://') or base_url.startswith('https://')):
                validation_result['warnings'].append("Base URL should start with http:// or https://")
                
            # Check for environment variables that might not be set
            env_vars_found = re.findall(r'\$\{([^}]+)\}', json.dumps(env_data))
            for var_name in env_vars_found:
                if not os.environ.get(var_name):
                    validation_result['warnings'].append(f"Environment variable not set: {var_name}")
                    
            if validation_result['errors']:
                validation_result['valid'] = False
                
        except Exception as e:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Failed to validate environment: {str(e)}")
            
        return validation_result
        
    def get_current_environment_id(self) -> Optional[str]:
        """Get current environment ID"""
        return self.current_environment
        
    def create_environment_template(self, environment_id: str, environment_name: str) -> bool:
        """Create a new environment template"""
        try:
            template = {
                "environment_name": environment_name,
                "environment_id": environment_id,
                "description": f"{environment_name} environment configuration",
                "base_url": f"https://{environment_id}.example.com",
                "timeout_settings": {
                    "page_load_timeout": 30,
                    "element_wait_timeout": 15,
                    "script_timeout": 10
                },
                "browser_settings": {
                    "window_size": {
                        "width": 1920,
                        "height": 1080
                    },
                    "headless": False,
                    "incognito": True
                },
                "credentials": {
                    "admin_user": {
                        "username": f"${{{environment_id.upper()}_ADMIN_USERNAME}}",
                        "password": f"${{{environment_id.upper()}_ADMIN_PASSWORD}}"
                    },
                    "test_user": {
                        "username": f"${{{environment_id.upper()}_TEST_USERNAME}}",
                        "password": f"${{{environment_id.upper()}_TEST_PASSWORD}}"
                    },
                    "api_key": f"${{{environment_id.upper()}_API_KEY}}"
                },
                "test_data": {
                    "products": [],
                    "customers": []
                },
                "api_endpoints": {
                    "login": "/api/v1/auth/login",
                    "products": "/api/v1/products"
                },
                "feature_flags": {
                    "debug_mode": environment_id == "dev"
                }
            }
            
            env_file = os.path.join(self.environments_dir, f"{environment_id}_environment.json")
            with open(env_file, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2)
                
            self.logger.info(f"Created environment template: {env_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create environment template: {str(e)}")
            return False