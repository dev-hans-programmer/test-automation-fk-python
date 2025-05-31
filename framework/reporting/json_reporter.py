"""
JSON Reporter
Generates detailed JSON reports of test execution
"""

import json
import os
from datetime import datetime
from typing import Dict, Any

from framework.utils.logger import Logger


class JsonReporter:
    def __init__(self, config: Dict[str, Any]):
        """Initialize JSON Reporter"""
        self.config = config
        self.logger = Logger()
        self.report_dir = config.get('reporting', {}).get('report_directory', './reports')
        
        # Ensure report directory exists
        os.makedirs(self.report_dir, exist_ok=True)
    
    def generate_report(self, execution_data: Dict[str, Any]) -> str:
        """Generate JSON report file"""
        try:
            # Create report filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            execution_id = execution_data.get('execution_id', 'unknown')
            filename = f"test_report_{execution_id}_{timestamp}.json"
            filepath = os.path.join(self.report_dir, filename)
            
            # Prepare report data
            report_data = self._prepare_report_data(execution_data)
            
            # Write JSON report
            with open(filepath, 'w') as file:
                json.dump(report_data, file, indent=2, ensure_ascii=False)
            
            self.logger.info(f"JSON report generated: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Failed to generate JSON report: {str(e)}")
            raise
    
    def _prepare_report_data(self, execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare comprehensive report data"""
        report_data = {
            "report_metadata": {
                "report_type": "json",
                "generated_at": datetime.now().isoformat(),
                "framework_version": "1.0.0",
                "report_format_version": "1.0"
            },
            "execution_summary": {
                "execution_id": execution_data.get('execution_id'),
                "start_time": execution_data.get('start_time'),
                "end_time": execution_data.get('end_time'),
                "duration": execution_data.get('duration'),
                "status": execution_data.get('status'),
                "total_scenarios": execution_data.get('total_scenarios', 0),
                "passed_scenarios": execution_data.get('passed_scenarios', 0),
                "failed_scenarios": execution_data.get('failed_scenarios', 0),
                "success_rate": self._calculate_success_rate(execution_data)
            },
            "scenarios": []
        }
        
        # Add scenario details
        for scenario in execution_data.get('scenarios', []):
            scenario_data = self._prepare_scenario_data(scenario)
            report_data["scenarios"].append(scenario_data)
        
        # Add environment information
        report_data["environment"] = self._get_environment_info()
        
        return report_data
    
    def _prepare_scenario_data(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare scenario data for report"""
        scenario_data = {
            "scenario_name": scenario.get('scenario_name'),
            "scenario_file": scenario.get('scenario_file'),
            "start_time": scenario.get('start_time'),
            "end_time": scenario.get('end_time'),
            "duration": scenario.get('duration'),
            "status": scenario.get('status'),
            "error": scenario.get('error'),
            "total_steps": len(scenario.get('steps', [])),
            "passed_steps": len([s for s in scenario.get('steps', []) if s.get('status') == 'passed']),
            "failed_steps": len([s for s in scenario.get('steps', []) if s.get('status') == 'failed']),
            "steps": []
        }
        
        # Add step details
        for step in scenario.get('steps', []):
            step_data = self._prepare_step_data(step)
            scenario_data["steps"].append(step_data)
        
        return scenario_data
    
    def _prepare_step_data(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare step data for report"""
        return {
            "step_id": step.get('step_id'),
            "step_name": step.get('step_name'),
            "action": step.get('action'),
            "target": step.get('target'),
            "value": step.get('value'),
            "start_time": step.get('start_time'),
            "end_time": step.get('end_time'),
            "duration": step.get('duration'),
            "status": step.get('status'),
            "error": step.get('error'),
            "screenshot_path": step.get('screenshot_path')
        }
    
    def _calculate_success_rate(self, execution_data: Dict[str, Any]) -> float:
        """Calculate success rate percentage"""
        total = execution_data.get('total_scenarios', 0)
        passed = execution_data.get('passed_scenarios', 0)
        
        if total == 0:
            return 0.0
        
        return round((passed / total) * 100, 2)
    
    def _get_environment_info(self) -> Dict[str, Any]:
        """Get environment information"""
        import platform
        import sys
        
        return {
            "platform": platform.platform(),
            "python_version": sys.version,
            "os": platform.system(),
            "architecture": platform.architecture(),
            "hostname": platform.node()
        }
    
    def load_report(self, filepath: str) -> Dict[str, Any]:
        """Load existing JSON report"""
        try:
            with open(filepath, 'r') as file:
                return json.load(file)
        except Exception as e:
            self.logger.error(f"Failed to load JSON report: {str(e)}")
            raise
    
    def get_recent_reports(self, limit: int = 10) -> list:
        """Get list of recent report files"""
        try:
            report_files = []
            
            for filename in os.listdir(self.report_dir):
                if filename.startswith('test_report_') and filename.endswith('.json'):
                    filepath = os.path.join(self.report_dir, filename)
                    stat = os.stat(filepath)
                    report_files.append({
                        'filename': filename,
                        'filepath': filepath,
                        'created': datetime.fromtimestamp(stat.st_ctime),
                        'size': stat.st_size
                    })
            
            # Sort by creation time (newest first)
            report_files.sort(key=lambda x: x['created'], reverse=True)
            
            return report_files[:limit]
            
        except Exception as e:
            self.logger.error(f"Failed to get recent reports: {str(e)}")
            return []
