"""
Helper Utilities
Common utility functions used throughout the framework
"""

import os
import re
import time
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from framework.utils.logger import Logger


class FrameworkHelpers:
    def __init__(self):
        """Initialize Framework Helpers"""
        self.logger = Logger()
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = 50) -> str:
        """Sanitize string for use in filenames or identifiers"""
        if not text:
            return "empty"
        
        # Remove special characters and replace with underscores
        sanitized = re.sub(r'[^\w\s-]', '_', text)
        
        # Replace multiple spaces/underscores with single underscore
        sanitized = re.sub(r'[\s_]+', '_', sanitized)
        
        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')
        
        # Limit length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized.lower()
    
    @staticmethod
    def generate_unique_id(prefix: str = "") -> str:
        """Generate unique identifier"""
        timestamp = str(int(time.time() * 1000))
        if prefix:
            return f"{prefix}_{timestamp}"
        return timestamp
    
    @staticmethod
    def calculate_duration(start_time: str, end_time: str) -> float:
        """Calculate duration between two ISO format timestamps"""
        try:
            start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            return (end - start).total_seconds()
        except Exception:
            return 0.0
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in seconds to human readable format"""
        if seconds < 1:
            return f"{seconds*1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.2f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds:.0f}s"
        else:
            hours = int(seconds // 3600)
            remaining_minutes = int((seconds % 3600) // 60)
            return f"{hours}h {remaining_minutes}m"
    
    @staticmethod
    def calculate_success_rate(total: int, passed: int) -> float:
        """Calculate success rate percentage"""
        if total == 0:
            return 0.0
        return round((passed / total) * 100, 2)
    
    @staticmethod
    def ensure_directory_exists(directory_path: str) -> str:
        """Ensure directory exists, create if it doesn't"""
        os.makedirs(directory_path, exist_ok=True)
        return directory_path
    
    @staticmethod
    def get_file_hash(filepath: str) -> Optional[str]:
        """Get MD5 hash of file"""
        try:
            hash_md5 = hashlib.md5()
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return None
    
    @staticmethod
    def get_file_size_mb(filepath: str) -> float:
        """Get file size in MB"""
        try:
            size_bytes = os.path.getsize(filepath)
            return round(size_bytes / (1024 * 1024), 2)
        except Exception:
            return 0.0
    
    @staticmethod
    def clean_old_files(directory: str, days_old: int = 7, pattern: str = "*") -> int:
        """Clean files older than specified days"""
        try:
            import glob
            cutoff_time = time.time() - (days_old * 24 * 60 * 60)
            deleted_count = 0
            
            search_pattern = os.path.join(directory, pattern)
            for filepath in glob.glob(search_pattern):
                if os.path.isfile(filepath) and os.path.getctime(filepath) < cutoff_time:
                    os.remove(filepath)
                    deleted_count += 1
            
            return deleted_count
            
        except Exception:
            return 0
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None
    
    @staticmethod
    def parse_selector(selector: str) -> tuple:
        """Parse CSS selector or XPath"""
        if selector.startswith('//') or selector.startswith('('):
            return 'xpath', selector
        elif '=' in selector and not selector.startswith('#') and not selector.startswith('.'):
            # Attribute selector like [name=value]
            return 'css', selector
        else:
            return 'css', selector
    
    @staticmethod
    def merge_dictionaries(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """Merge two dictionaries, with dict2 values taking precedence"""
        merged = dict1.copy()
        merged.update(dict2)
        return merged
    
    @staticmethod
    def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """Flatten nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(FrameworkHelpers.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    @staticmethod
    def get_timestamp(format_type: str = 'iso') -> str:
        """Get current timestamp in various formats"""
        now = datetime.now()
        
        if format_type == 'iso':
            return now.isoformat()
        elif format_type == 'filename':
            return now.strftime('%Y%m%d_%H%M%S')
        elif format_type == 'display':
            return now.strftime('%Y-%m-%d %H:%M:%S')
        elif format_type == 'date':
            return now.strftime('%Y-%m-%d')
        else:
            return now.isoformat()


class DataProcessor:
    """Helper class for data processing operations"""
    
    @staticmethod
    def extract_numbers(text: str) -> List[float]:
        """Extract all numbers from text"""
        pattern = r'-?\d+\.?\d*'
        matches = re.findall(pattern, text)
        return [float(match) for match in matches]
    
    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """Extract email addresses from text"""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(pattern, text)
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def convert_to_bool(value: Any) -> bool:
        """Convert various value types to boolean"""
        if isinstance(value, bool):
            return value
        elif isinstance(value, str):
            return value.lower() in ('true', 'yes', 'y', '1', 'on')
        elif isinstance(value, (int, float)):
            return value != 0
        else:
            return bool(value)
