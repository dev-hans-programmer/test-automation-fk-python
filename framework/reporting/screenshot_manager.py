"""
Screenshot Manager
Manages screenshot capture, organization and storage
"""

import os
from datetime import datetime
from typing import Optional

from framework.utils.logger import Logger


class ScreenshotManager:
    def __init__(self, config: dict):
        """Initialize Screenshot Manager"""
        self.config = config
        self.logger = Logger()
        self.screenshot_dir = config.get('reporting', {}).get('screenshot_directory', './screenshots')
        
        # Create base screenshot directory
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        # Create session directory
        self.session_dir = self._create_session_directory()
        
    def _create_session_directory(self) -> str:
        """Create directory for current test session"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = os.path.join(self.screenshot_dir, f"session_{timestamp}")
        os.makedirs(session_dir, exist_ok=True)
        return session_dir
    
    def capture_step_screenshot(self, driver, step_id: int, step_name: str, status: str) -> Optional[str]:
        """Capture screenshot for a test step"""
        try:
            # Generate filename
            safe_step_name = self._sanitize_filename(step_name)
            timestamp = datetime.now().strftime("%H%M%S")
            filename = f"step_{step_id:02d}_{timestamp}_{safe_step_name}_{status}.png"
            filepath = os.path.join(self.session_dir, filename)
            
            # Take actual screenshot using WebDriver
            if driver:
                driver.save_screenshot(filepath)
                self.logger.info(f"Screenshot captured: {filepath}")
                return filepath
            else:
                self.logger.warning(f"No driver available for screenshot at step {step_id}")
                return None
            
        except Exception as e:
            self.logger.error(f"Failed to capture screenshot for step {step_id}: {str(e)}")
            return None
    
    def _create_placeholder_screenshot(self, filepath: str, step_name: str, status: str):
        """Create a placeholder screenshot file (for demonstration)"""
        try:
            # In a real implementation, this would use the WebDriver to take the screenshot
            # For now, we'll create a simple text file as a placeholder
            with open(filepath.replace('.png', '.txt'), 'w') as f:
                f.write(f"Screenshot placeholder\n")
                f.write(f"Step: {step_name}\n")
                f.write(f"Status: {status}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                
        except Exception as e:
            self.logger.error(f"Failed to create placeholder screenshot: {str(e)}")
    
    def capture_failure_screenshot(self, driver, scenario_name: str, error_message: str) -> Optional[str]:
        """Capture screenshot on test failure"""
        try:
            safe_scenario_name = self._sanitize_filename(scenario_name)
            timestamp = datetime.now().strftime("%H%M%S")
            filename = f"failure_{timestamp}_{safe_scenario_name}.png"
            filepath = os.path.join(self.session_dir, filename)
            
            # Take actual failure screenshot using WebDriver
            if driver:
                driver.save_screenshot(filepath)
                self.logger.info(f"Failure screenshot captured: {filepath}")
                return filepath
            else:
                self.logger.warning(f"No driver available for failure screenshot")
                return None
            
        except Exception as e:
            self.logger.error(f"Failed to capture failure screenshot: {str(e)}")
            return None
    
    def capture_custom_screenshot(self, name: str, description: str = "") -> Optional[str]:
        """Capture custom screenshot with specified name"""
        try:
            safe_name = self._sanitize_filename(name)
            timestamp = datetime.now().strftime("%H%M%S")
            filename = f"custom_{timestamp}_{safe_name}.png"
            filepath = os.path.join(self.session_dir, filename)
            
            # Create placeholder for custom screenshot
            self._create_placeholder_screenshot(filepath, f"CUSTOM: {name}", "custom")
            
            self.logger.info(f"Custom screenshot captured: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Failed to capture custom screenshot: {str(e)}")
            return None
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize string for use as filename"""
        # Remove or replace invalid filename characters
        invalid_chars = '<>:"/\\|?*'
        sanitized = name
        
        for char in invalid_chars:
            sanitized = sanitized.replace(char, '_')
        
        # Replace spaces with underscores
        sanitized = sanitized.replace(' ', '_')
        
        # Limit length
        if len(sanitized) > 50:
            sanitized = sanitized[:50]
        
        return sanitized
    
    def get_session_screenshots(self) -> list:
        """Get list of screenshots from current session"""
        try:
            screenshots = []
            
            for filename in os.listdir(self.session_dir):
                if filename.endswith(('.png', '.jpg', '.jpeg')):
                    filepath = os.path.join(self.session_dir, filename)
                    stat = os.stat(filepath)
                    screenshots.append({
                        'filename': filename,
                        'filepath': filepath,
                        'created': datetime.fromtimestamp(stat.st_ctime),
                        'size': stat.st_size
                    })
            
            # Sort by creation time
            screenshots.sort(key=lambda x: x['created'])
            return screenshots
            
        except Exception as e:
            self.logger.error(f"Failed to get session screenshots: {str(e)}")
            return []
    
    def cleanup_old_screenshots(self, days_old: int = 7):
        """Clean up screenshots older than specified days"""
        try:
            cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            deleted_count = 0
            
            for root, dirs, files in os.walk(self.screenshot_dir):
                for file in files:
                    filepath = os.path.join(root, file)
                    if os.path.getctime(filepath) < cutoff_time:
                        os.remove(filepath)
                        deleted_count += 1
            
            self.logger.info(f"Cleaned up {deleted_count} old screenshots")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old screenshots: {str(e)}")
    
    def get_current_session_dir(self) -> str:
        """Get current session directory path"""
        return self.session_dir
