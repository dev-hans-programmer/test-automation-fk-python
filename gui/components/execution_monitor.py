"""
Execution Monitor Component
GUI component for monitoring test execution in real-time
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime
from typing import Dict, Any, Callable, List

from framework.utils.logger import Logger


class ExecutionMonitor:
    def __init__(self, parent: tk.Widget, start_callback: Callable, stop_callback: Callable):
        """Initialize Execution Monitor"""
        self.parent = parent
        self.start_callback = start_callback
        self.stop_callback = stop_callback
        self.logger = Logger()
        
        # Execution state
        self.is_running = False
        self.current_execution = None
        self.selected_scenarios = []
        
        # Create UI
        self._create_ui()
    
    def _create_ui(self):
        """Create the user interface"""
        # Main container
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(self.main_frame, text="Test Execution Monitor", font=('Arial', 14, 'bold'))
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Control panel
        control_frame = ttk.LabelFrame(self.main_frame, text="Execution Control", padding=10)
        control_frame.pack(fill='x', pady=(0, 10))
        
        # Control buttons frame
        buttons_frame = ttk.Frame(control_frame)
        buttons_frame.pack(fill='x')
        
        self.start_button = ttk.Button(
            buttons_frame, 
            text="Start Execution", 
            command=self._start_execution,
            style='Accent.TButton'
        )
        self.start_button.pack(side='left', padx=(0, 10))
        
        self.stop_button = ttk.Button(
            buttons_frame, 
            text="Stop Execution", 
            command=self._stop_execution,
            state='disabled'
        )
        self.stop_button.pack(side='left', padx=(0, 10))
        
        self.pause_button = ttk.Button(
            buttons_frame, 
            text="Pause", 
            command=self._pause_execution,
            state='disabled'
        )
        self.pause_button.pack(side='left', padx=(0, 10))
        
        # Execution options
        options_frame = ttk.Frame(control_frame)
        options_frame.pack(fill='x', pady=(10, 0))
        
        # Checkbox options
        self.continue_on_failure_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Continue on failure",
            variable=self.continue_on_failure_var
        ).pack(side='left', padx=(0, 20))
        
        self.headless_mode_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Headless mode",
            variable=self.headless_mode_var
        ).pack(side='left', padx=(0, 20))
        
        self.screenshot_on_step_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Screenshot on each step",
            variable=self.screenshot_on_step_var
        ).pack(side='left')
        
        # Progress section
        progress_frame = ttk.LabelFrame(self.main_frame, text="Execution Progress", padding=10)
        progress_frame.pack(fill='x', pady=(0, 10))
        
        # Overall progress
        ttk.Label(progress_frame, text="Overall Progress:").pack(anchor='w')
        self.overall_progress = ttk.Progressbar(
            progress_frame, 
            mode='determinate',
            length=400
        )
        self.overall_progress.pack(fill='x', pady=(5, 10))
        
        # Progress info
        progress_info_frame = ttk.Frame(progress_frame)
        progress_info_frame.pack(fill='x')
        
        self.progress_label = ttk.Label(progress_info_frame, text="Ready to start execution")
        self.progress_label.pack(side='left')
        
        self.time_label = ttk.Label(progress_info_frame, text="")
        self.time_label.pack(side='right')
        
        # Current scenario progress
        ttk.Label(progress_frame, text="Current Scenario:").pack(anchor='w', pady=(10, 0))
        self.scenario_progress = ttk.Progressbar(
            progress_frame,
            mode='indeterminate',
            length=400
        )
        self.scenario_progress.pack(fill='x', pady=(5, 5))
        
        self.current_scenario_label = ttk.Label(progress_frame, text="No scenario running")
        self.current_scenario_label.pack(anchor='w')
        
        # Execution summary
        summary_frame = ttk.LabelFrame(self.main_frame, text="Execution Summary", padding=10)
        summary_frame.pack(fill='x', pady=(0, 10))
        
        # Summary grid
        summary_grid = ttk.Frame(summary_frame)
        summary_grid.pack(fill='x')
        
        # Left column
        left_col = ttk.Frame(summary_grid)
        left_col.pack(side='left', fill='x', expand=True)
        
        ttk.Label(left_col, text="Total Scenarios:").grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.total_scenarios_label = ttk.Label(left_col, text="0", font=('Arial', 10, 'bold'))
        self.total_scenarios_label.grid(row=0, column=1, sticky='w')
        
        ttk.Label(left_col, text="Passed:").grid(row=1, column=0, sticky='w', padx=(0, 10))
        self.passed_label = ttk.Label(left_col, text="0", foreground='green', font=('Arial', 10, 'bold'))
        self.passed_label.grid(row=1, column=1, sticky='w')
        
        ttk.Label(left_col, text="Failed:").grid(row=2, column=0, sticky='w', padx=(0, 10))
        self.failed_label = ttk.Label(left_col, text="0", foreground='red', font=('Arial', 10, 'bold'))
        self.failed_label.grid(row=2, column=1, sticky='w')
        
        # Right column
        right_col = ttk.Frame(summary_grid)
        right_col.pack(side='right', fill='x', expand=True)
        
        ttk.Label(right_col, text="Success Rate:").grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.success_rate_label = ttk.Label(right_col, text="0%", font=('Arial', 10, 'bold'))
        self.success_rate_label.grid(row=0, column=1, sticky='w')
        
        ttk.Label(right_col, text="Duration:").grid(row=1, column=0, sticky='w', padx=(0, 10))
        self.duration_label = ttk.Label(right_col, text="0s", font=('Arial', 10, 'bold'))
        self.duration_label.grid(row=1, column=1, sticky='w')
        
        ttk.Label(right_col, text="Status:").grid(row=2, column=0, sticky='w', padx=(0, 10))
        self.status_label = ttk.Label(right_col, text="Ready", font=('Arial', 10, 'bold'))
        self.status_label.grid(row=2, column=1, sticky='w')
        
        # Execution log
        log_frame = ttk.LabelFrame(self.main_frame, text="Execution Log", padding=10)
        log_frame.pack(fill='both', expand=True)
        
        # Log text widget with scrollbar
        log_text_frame = ttk.Frame(log_frame)
        log_text_frame.pack(fill='both', expand=True)
        
        self.log_text = tk.Text(
            log_text_frame,
            height=12,
            wrap=tk.WORD,
            state='disabled',
            font=('Consolas', 9)
        )
        log_scrollbar = ttk.Scrollbar(log_text_frame, orient='vertical', command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side='left', fill='both', expand=True)
        log_scrollbar.pack(side='right', fill='y')
        
        # Log control buttons
        log_control_frame = ttk.Frame(log_frame)
        log_control_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(log_control_frame, text="Clear Log", command=self._clear_log).pack(side='left')
        ttk.Button(log_control_frame, text="Save Log", command=self._save_log).pack(side='left', padx=(10, 0))
        
        # Auto-scroll checkbox
        self.auto_scroll_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            log_control_frame,
            text="Auto-scroll",
            variable=self.auto_scroll_var
        ).pack(side='right')
    
    def _start_execution(self):
        """Start test execution"""
        if self.is_running:
            messagebox.showwarning("Already Running", "Execution is already in progress")
            return
        
        # Prepare execution configuration
        execution_config = {
            'continue_on_failure': self.continue_on_failure_var.get(),
            'headless_mode': self.headless_mode_var.get(),
            'screenshot_on_step': self.screenshot_on_step_var.get(),
            'selected_scenarios': self.selected_scenarios
        }
        
        # Update UI state
        self._set_execution_state(True)
        self._reset_execution_data()
        self._log_message("Starting test execution...", "INFO")
        
        # Call start callback
        if self.start_callback:
            self.start_callback(execution_config)
    
    def _stop_execution(self):
        """Stop test execution"""
        if not self.is_running:
            messagebox.showinfo("Not Running", "No execution is currently in progress")
            return
        
        result = messagebox.askyesno("Stop Execution", "Are you sure you want to stop the execution?")
        if result:
            self._log_message("Stopping test execution...", "WARNING")
            
            # Call stop callback
            if self.stop_callback:
                self.stop_callback()
            
            self._set_execution_state(False)
    
    def _pause_execution(self):
        """Pause test execution (placeholder for future implementation)"""
        messagebox.showinfo("Pause", "Pause functionality will be implemented in future version")
    
    def _set_execution_state(self, running: bool):
        """Set UI state based on execution status"""
        self.is_running = running
        
        if running:
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.pause_button.config(state='normal')
            self.status_label.config(text="Running", foreground='blue')
            self.scenario_progress.start(10)  # Start indeterminate animation
        else:
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            self.pause_button.config(state='disabled')
            self.scenario_progress.stop()
            
            if self.current_execution and self.current_execution.get('status') == 'completed':
                self.status_label.config(text="Completed", foreground='green')
            elif self.current_execution and self.current_execution.get('status') == 'stopped':
                self.status_label.config(text="Stopped", foreground='orange')
            else:
                self.status_label.config(text="Ready", foreground='black')
    
    def _reset_execution_data(self):
        """Reset execution data"""
        self.current_execution = None
        self.overall_progress['value'] = 0
        self.total_scenarios_label.config(text="0")
        self.passed_label.config(text="0")
        self.failed_label.config(text="0")
        self.success_rate_label.config(text="0%")
        self.duration_label.config(text="0s")
        self.current_scenario_label.config(text="Initializing...")
        self.progress_label.config(text="Starting execution...")
    
    def _log_message(self, message: str, level: str = "INFO"):
        """Add message to execution log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {level}: {message}\n"
        
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, formatted_message)
        
        # Color coding
        if level == "ERROR":
            self.log_text.tag_add("error", f"end-{len(formatted_message)}c", "end-1c")
            self.log_text.tag_config("error", foreground='red')
        elif level == "WARNING":
            self.log_text.tag_add("warning", f"end-{len(formatted_message)}c", "end-1c")
            self.log_text.tag_config("warning", foreground='orange')
        elif level == "SUCCESS":
            self.log_text.tag_add("success", f"end-{len(formatted_message)}c", "end-1c")
            self.log_text.tag_config("success", foreground='green')
        
        self.log_text.config(state='disabled')
        
        # Auto-scroll if enabled
        if self.auto_scroll_var.get():
            self.log_text.see(tk.END)
    
    def _clear_log(self):
        """Clear execution log"""
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
    
    def _save_log(self):
        """Save execution log to file"""
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            title="Save Execution Log",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                log_content = self.log_text.get(1.0, tk.END)
                with open(file_path, 'w') as file:
                    file.write(log_content)
                messagebox.showinfo("Save Complete", f"Log saved to: {file_path}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save log: {str(e)}")
    
    def update_selected_scenarios(self, scenarios: List[Dict[str, Any]]):
        """Update selected scenarios"""
        self.selected_scenarios = scenarios
        self._log_message(f"Selected {len(scenarios)} scenarios for execution", "INFO")
    
    def update_progress(self, current: int, total: int, scenario_name: str):
        """Update execution progress"""
        if total > 0:
            progress_percentage = (current / total) * 100
            self.overall_progress['value'] = progress_percentage
            self.progress_label.config(text=f"Scenario {current}/{total} ({progress_percentage:.1f}%)")
        
        self.current_scenario_label.config(text=f"Executing: {scenario_name}")
        self._log_message(f"Starting scenario: {scenario_name}", "INFO")
        
        # Update time
        if self.current_execution and 'start_time' in self.current_execution:
            start_time = datetime.fromisoformat(self.current_execution['start_time'])
            duration = (datetime.now() - start_time).total_seconds()
            self.time_label.config(text=f"Elapsed: {duration:.0f}s")
    
    def update_execution_results(self, results: Dict[str, Any]):
        """Update execution results"""
        self.current_execution = results
        
        # Update summary
        total = results.get('total_scenarios', 0)
        passed = results.get('passed_scenarios', 0)
        failed = results.get('failed_scenarios', 0)
        duration = results.get('duration', 0)
        
        self.total_scenarios_label.config(text=str(total))
        self.passed_label.config(text=str(passed))
        self.failed_label.config(text=str(failed))
        
        if total > 0:
            success_rate = (passed / total) * 100
            self.success_rate_label.config(text=f"{success_rate:.1f}%")
        
        self.duration_label.config(text=f"{duration:.1f}s")
        
        # Update progress
        self.overall_progress['value'] = 100
        self.progress_label.config(text=f"Execution completed - {passed}/{total} passed")
        self.current_scenario_label.config(text="Execution completed")
        
        # Log results
        self._log_message(f"Execution completed - {passed}/{total} scenarios passed", "SUCCESS")
        
        # Log individual scenario results
        for scenario in results.get('scenarios', []):
            scenario_name = scenario.get('scenario_name', 'Unknown')
            scenario_status = scenario.get('status', 'unknown')
            
            if scenario_status == 'passed':
                self._log_message(f"✓ {scenario_name} - PASSED", "SUCCESS")
            else:
                error = scenario.get('error', 'Unknown error')
                self._log_message(f"✗ {scenario_name} - FAILED: {error}", "ERROR")
        
        # Update execution state
        self._set_execution_state(False)
    
    def update_execution_error(self, error_message: str):
        """Update execution error"""
        self._log_message(f"Execution failed: {error_message}", "ERROR")
        self.status_label.config(text="Error", foreground='red')
        self.current_scenario_label.config(text="Execution failed")
        self._set_execution_state(False)
    
    def update_execution_stopped(self):
        """Update execution stopped"""
        self._log_message("Execution stopped by user", "WARNING")
        self.status_label.config(text="Stopped", foreground='orange')
        self.current_scenario_label.config(text="Execution stopped")
        self._set_execution_state(False)
