"""
Main GUI Window
Central GUI controller for the Test Automation Framework
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import threading
from typing import Dict, Any, Optional

from gui.components.scenario_selector import ScenarioSelector
from gui.components.execution_monitor import ExecutionMonitor
from gui.components.report_viewer import ReportViewer
from gui.components.config_manager import ConfigManager
from gui.components.environment_selector import EnvironmentSelector
from gui.styles.main_style import StyleManager

from framework.core.test_engine import TestEngine
from framework.utils.logger import Logger


class MainWindow:
    def __init__(self, root: tk.Tk):
        """Initialize Main Window"""
        self.root = root
        self.logger = Logger()
        self.test_engine = None
        self.execution_thread = None
        self.execution_running = False
        
        # Initialize GUI
        self._setup_window()
        self._create_menu()
        self._create_main_layout()
        self._setup_components()
        self._apply_styles()
        
        # Initialize test engine
        self._initialize_test_engine()
        
        self.logger.info("Main window initialized")
    
    def _setup_window(self):
        """Setup main window properties"""
        self.root.title("Test Automation Framework - v1.0.0")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        
        # Configure window close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Set window icon (optional)
        try:
            # You can add an icon file here if available
            pass
        except:
            pass
    
    def _create_menu(self):
        """Create application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Config", command=self._open_config_file)
        file_menu.add_command(label="Save Config", command=self._save_config_file)
        file_menu.add_separator()
        file_menu.add_command(label="Export Reports", command=self._export_reports)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Validate Configuration", command=self._validate_configuration)
        tools_menu.add_command(label="Clear Reports", command=self._clear_reports)
        tools_menu.add_command(label="Clear Screenshots", command=self._clear_screenshots)
        tools_menu.add_command(label="Clear Logs", command=self._clear_logs)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self._show_documentation)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _create_main_layout(self):
        """Create main layout structure"""
        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tab frames
        self.scenario_tab = ttk.Frame(self.notebook)
        self.execution_tab = ttk.Frame(self.notebook)
        self.reports_tab = ttk.Frame(self.notebook)
        self.config_tab = ttk.Frame(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.scenario_tab, text="Scenarios")
        self.notebook.add(self.execution_tab, text="Execution")
        self.notebook.add(self.reports_tab, text="Reports")
        self.notebook.add(self.config_tab, text="Configuration")
        
        # Bind tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
    
    def _setup_components(self):
        """Setup all GUI components"""
        # Scenario selector component
        self.scenario_selector = ScenarioSelector(
            self.scenario_tab, 
            self._on_scenario_selection_changed
        )
        
        # Execution monitor component
        self.execution_monitor = ExecutionMonitor(
            self.execution_tab,
            self._start_execution,
            self._stop_execution
        )
        
        # Report viewer component
        self.report_viewer = ReportViewer(
            self.reports_tab,
            self._on_report_selected
        )
        
        # Create config tab layout with environment selector
        config_container = ttk.Frame(self.config_tab)
        config_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Environment selector component (top section)
        self.environment_selector = EnvironmentSelector(config_container)
        self.environment_selector.set_environment_changed_callback(self._on_environment_changed)
        
        # Configuration manager component (bottom section)
        self.config_manager = ConfigManager(
            config_container,
            self._on_config_changed
        )
    
    def _apply_styles(self):
        """Apply custom styles to components"""
        self.style_manager = StyleManager()
        self.style_manager.apply_styles()
    
    def _initialize_test_engine(self):
        """Initialize test engine"""
        try:
            self.test_engine = TestEngine()
            self.logger.info("Test engine initialized successfully")
            
            # Load configuration into GUI components
            self._refresh_scenario_list()
            self._refresh_reports_list()
            
        except Exception as e:
            error_msg = f"Failed to initialize test engine: {str(e)}"
            self.logger.error(error_msg)
            messagebox.showerror("Initialization Error", error_msg)
    
    def _refresh_scenario_list(self):
        """Refresh scenario list in selector"""
        if self.test_engine:
            try:
                scenarios = self.test_engine.get_executable_scenarios()
                self.scenario_selector.update_scenarios(scenarios)
            except Exception as e:
                self.logger.error(f"Failed to refresh scenario list: {str(e)}")
    
    def _refresh_reports_list(self):
        """Refresh reports list in viewer"""
        try:
            self.report_viewer.refresh_reports()
        except Exception as e:
            self.logger.error(f"Failed to refresh reports list: {str(e)}")
    
    # Event handlers
    def _on_tab_changed(self, event):
        """Handle tab change event"""
        selected_tab = event.widget.tab('current')['text']
        self.logger.debug(f"Switched to tab: {selected_tab}")
        
        # Refresh data when switching to specific tabs
        if selected_tab == "Reports":
            self._refresh_reports_list()
        elif selected_tab == "Scenarios":
            self._refresh_scenario_list()
    
    def _on_scenario_selection_changed(self, selected_scenarios):
        """Handle scenario selection change"""
        self.logger.debug(f"Scenario selection changed: {len(selected_scenarios)} selected")
        # Update execution monitor with selected scenarios
        self.execution_monitor.update_selected_scenarios(selected_scenarios)
    
    def _on_config_changed(self, config_data):
        """Handle configuration change"""
        self.logger.info("Configuration changed")
        try:
            # Reinitialize test engine with new config
            self._initialize_test_engine()
        except Exception as e:
            self.logger.error(f"Failed to apply configuration changes: {str(e)}")
            messagebox.showerror("Configuration Error", f"Failed to apply changes: {str(e)}")
    
    def _on_report_selected(self, report_path):
        """Handle report selection"""
        self.logger.debug(f"Report selected: {report_path}")
    
    def _on_environment_changed(self, environment_id: str, environment_data: Dict[str, Any]):
        """Handle environment change"""
        self.logger.info(f"Environment changed to: {environment_id}")
        try:
            # Update test engine with new environment data
            if self.test_engine:
                self.test_engine.set_environment_data(environment_id, environment_data)
            
            # Refresh scenario list to reflect environment changes
            self._refresh_scenario_list()
            
            # Update execution monitor
            if hasattr(self, 'execution_monitor'):
                self.execution_monitor.update_environment_info(environment_id, environment_data)
                
            self.logger.info(f"Successfully switched to {environment_id} environment")
            
        except Exception as e:
            self.logger.error(f"Failed to switch environment: {str(e)}")
            messagebox.showerror("Environment Error", f"Failed to switch to {environment_id}: {str(e)}")
    
    def _start_execution(self, execution_config):
        """Start test execution"""
        if self.execution_running:
            messagebox.showwarning("Execution Running", "Test execution is already in progress")
            return
        
        try:
            self.execution_running = True
            self.logger.info("Starting test execution")
            
            # Run execution in separate thread
            self.execution_thread = threading.Thread(
                target=self._execute_tests_thread,
                args=(execution_config,),
                daemon=True
            )
            self.execution_thread.start()
            
        except Exception as e:
            self.execution_running = False
            error_msg = f"Failed to start execution: {str(e)}"
            self.logger.error(error_msg)
            messagebox.showerror("Execution Error", error_msg)
    
    def _execute_tests_thread(self, execution_config):
        """Execute tests in separate thread"""
        try:
            # Progress callback for updates
            def progress_callback(current, total, scenario_name):
                self.root.after(0, lambda: self.execution_monitor.update_progress(
                    current, total, scenario_name
                ))
            
            # Execute all scenarios
            results = self.test_engine.execute_all_scenarios(progress_callback)
            
            # Update GUI with results
            self.root.after(0, lambda: self._on_execution_completed(results))
            
        except Exception as e:
            error_msg = f"Execution failed: {str(e)}"
            self.logger.error(error_msg)
            self.root.after(0, lambda: self._on_execution_failed(error_msg))
        finally:
            self.execution_running = False
    
    def _on_execution_completed(self, results):
        """Handle execution completion"""
        self.logger.info("Test execution completed")
        self.execution_monitor.update_execution_results(results)
        
        # Refresh reports list
        self._refresh_reports_list()
        
        # Show completion message
        total = results.get('total_scenarios', 0)
        passed = results.get('passed_scenarios', 0)
        failed = results.get('failed_scenarios', 0)
        
        messagebox.showinfo(
            "Execution Complete",
            f"Test execution completed!\n\n"
            f"Total Scenarios: {total}\n"
            f"Passed: {passed}\n"
            f"Failed: {failed}\n"
            f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "No scenarios executed"
        )
    
    def _on_execution_failed(self, error_msg):
        """Handle execution failure"""
        self.logger.error(f"Execution failed: {error_msg}")
        self.execution_monitor.update_execution_error(error_msg)
        messagebox.showerror("Execution Failed", error_msg)
    
    def _stop_execution(self):
        """Stop test execution"""
        if not self.execution_running:
            messagebox.showinfo("No Execution", "No test execution is currently running")
            return
        
        try:
            self.logger.info("Stopping test execution")
            if self.test_engine:
                self.test_engine.stop_execution()
            
            self.execution_running = False
            self.execution_monitor.update_execution_stopped()
            
            messagebox.showinfo("Execution Stopped", "Test execution has been stopped")
            
        except Exception as e:
            error_msg = f"Failed to stop execution: {str(e)}"
            self.logger.error(error_msg)
            messagebox.showerror("Stop Error", error_msg)
    
    # Menu event handlers
    def _open_config_file(self):
        """Open configuration file"""
        file_path = filedialog.askopenfilename(
            title="Open Configuration File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.config_manager.load_config_file(file_path)
                self.logger.info(f"Loaded configuration from: {file_path}")
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load configuration: {str(e)}")
    
    def _save_config_file(self):
        """Save configuration file"""
        file_path = filedialog.asksaveasfilename(
            title="Save Configuration File",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.config_manager.save_config_file(file_path)
                self.logger.info(f"Saved configuration to: {file_path}")
                messagebox.showinfo("Save Complete", f"Configuration saved to: {file_path}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save configuration: {str(e)}")
    
    def _export_reports(self):
        """Export reports"""
        directory = filedialog.askdirectory(title="Select Export Directory")
        
        if directory:
            try:
                # Implement report export logic
                self.report_viewer.export_reports(directory)
                messagebox.showinfo("Export Complete", f"Reports exported to: {directory}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export reports: {str(e)}")
    
    def _validate_configuration(self):
        """Validate current configuration"""
        try:
            if self.test_engine and self.test_engine.validate_configuration():
                messagebox.showinfo("Validation Success", "Configuration validation passed!")
            else:
                messagebox.showerror("Validation Failed", "Configuration validation failed. Check logs for details.")
        except Exception as e:
            messagebox.showerror("Validation Error", f"Failed to validate configuration: {str(e)}")
    
    def _clear_reports(self):
        """Clear old reports"""
        result = messagebox.askyesno(
            "Clear Reports",
            "Are you sure you want to clear all reports? This action cannot be undone."
        )
        
        if result:
            try:
                # Implement report clearing logic
                import shutil
                reports_dir = "reports"
                if os.path.exists(reports_dir):
                    shutil.rmtree(reports_dir)
                    os.makedirs(reports_dir, exist_ok=True)
                
                self._refresh_reports_list()
                messagebox.showinfo("Clear Complete", "Reports cleared successfully")
            except Exception as e:
                messagebox.showerror("Clear Error", f"Failed to clear reports: {str(e)}")
    
    def _clear_screenshots(self):
        """Clear old screenshots"""
        result = messagebox.askyesno(
            "Clear Screenshots",
            "Are you sure you want to clear all screenshots? This action cannot be undone."
        )
        
        if result:
            try:
                import shutil
                screenshots_dir = "screenshots"
                if os.path.exists(screenshots_dir):
                    shutil.rmtree(screenshots_dir)
                    os.makedirs(screenshots_dir, exist_ok=True)
                
                messagebox.showinfo("Clear Complete", "Screenshots cleared successfully")
            except Exception as e:
                messagebox.showerror("Clear Error", f"Failed to clear screenshots: {str(e)}")
    
    def _clear_logs(self):
        """Clear old logs"""
        result = messagebox.askyesno(
            "Clear Logs",
            "Are you sure you want to clear all logs? This action cannot be undone."
        )
        
        if result:
            try:
                import shutil
                logs_dir = "logs"
                if os.path.exists(logs_dir):
                    shutil.rmtree(logs_dir)
                    os.makedirs(logs_dir, exist_ok=True)
                
                messagebox.showinfo("Clear Complete", "Logs cleared successfully")
            except Exception as e:
                messagebox.showerror("Clear Error", f"Failed to clear logs: {str(e)}")
    
    def _show_documentation(self):
        """Show documentation"""
        doc_text = """
Test Automation Framework - Documentation

OVERVIEW:
This framework provides a comprehensive solution for automated testing with:
- JSON-based scenario definitions
- Selenium WebDriver integration
- Dual reporting (JSON + Word with screenshots)
- GUI-based test management

TABS:
1. Scenarios: Select and configure test scenarios
2. Execution: Monitor test execution in real-time
3. Reports: View and analyze test results
4. Configuration: Manage framework settings

USAGE:
1. Configure test scenarios in the Scenarios tab
2. Start execution from the Execution tab
3. Monitor progress and view results
4. Analyze reports in the Reports tab

For detailed documentation, please refer to the user manual.
        """
        
        # Create documentation window
        doc_window = tk.Toplevel(self.root)
        doc_window.title("Documentation")
        doc_window.geometry("600x400")
        
        text_widget = tk.Text(doc_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill='both', expand=True)
        text_widget.insert('1.0', doc_text)
        text_widget.config(state='disabled')
        
        scrollbar = ttk.Scrollbar(doc_window, orient="vertical", command=text_widget.yview)
        scrollbar.pack(side="right", fill="y")
        text_widget.config(yscrollcommand=scrollbar.set)
    
    def _show_about(self):
        """Show about dialog"""
        about_text = """
Test Automation Framework
Version 1.0.0

A comprehensive test automation solution built with Python and Tkinter.

Features:
• JSON-based scenario definitions
• Selenium WebDriver integration
• Dual reporting system
• Real-time execution monitoring
• Screenshot capture
• Configuration management

Built with Python, Selenium, Tkinter, and python-docx.

© 2024 Test Automation Framework
        """
        
        messagebox.showinfo("About", about_text)
    
    def _on_closing(self):
        """Handle window closing event"""
        if self.execution_running:
            result = messagebox.askyesno(
                "Execution Running",
                "Test execution is in progress. Do you want to stop it and exit?"
            )
            
            if result:
                self._stop_execution()
            else:
                return
        
        self.logger.info("Application closing")
        self.root.destroy()
