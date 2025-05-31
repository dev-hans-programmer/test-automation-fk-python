"""
Configuration Manager Component
GUI component for managing framework configuration settings
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from typing import Dict, Any, Callable, Optional

from framework.utils.logger import Logger
from framework.utils.config_validator import ConfigValidator


class ConfigManager:
    def __init__(self, parent: tk.Widget, config_callback: Callable[[Dict[str, Any]], None]):
        """Initialize Configuration Manager"""
        self.parent = parent
        self.config_callback = config_callback
        self.logger = Logger()
        self.validator = ConfigValidator()
        
        # Configuration data
        self.config_data = {}
        self.config_file_path = "config/master_config.json"
        self.unsaved_changes = False
        
        # Create UI
        self._create_ui()
        self._load_configuration()
    
    def _create_ui(self):
        """Create the user interface"""
        # Main container
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(self.main_frame, text="Framework Configuration", font=('Arial', 14, 'bold'))
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Control frame
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(fill='x', pady=(0, 10))
        
        # Control buttons
        ttk.Button(control_frame, text="Load Config", command=self._load_config_file).pack(side='left', padx=(0, 5))
        ttk.Button(control_frame, text="Save Config", command=self._save_config_file).pack(side='left', padx=(0, 5))
        ttk.Button(control_frame, text="Reset to Default", command=self._reset_to_default).pack(side='left', padx=(0, 5))
        ttk.Button(control_frame, text="Validate", command=self._validate_config).pack(side='left', padx=(0, 5))
        
        # Status label
        self.status_label = ttk.Label(control_frame, text="Configuration loaded", foreground='green')
        self.status_label.pack(side='right')
        
        # Create notebook for configuration sections
        self.config_notebook = ttk.Notebook(self.main_frame)
        self.config_notebook.pack(fill='both', expand=True)
        
        # Framework settings tab
        self.framework_tab = ttk.Frame(self.config_notebook)
        self.config_notebook.add(self.framework_tab, text="Framework Settings")
        self._create_framework_tab()
        
        # Reporting settings tab
        self.reporting_tab = ttk.Frame(self.config_notebook)
        self.config_notebook.add(self.reporting_tab, text="Reporting")
        self._create_reporting_tab()
        
        # Browser settings tab
        self.browser_tab = ttk.Frame(self.config_notebook)
        self.config_notebook.add(self.browser_tab, text="Browser Settings")
        self._create_browser_tab()
        
        # Advanced settings tab
        self.advanced_tab = ttk.Frame(self.config_notebook)
        self.config_notebook.add(self.advanced_tab, text="Advanced")
        self._create_advanced_tab()
        
        # Bind change tracking
        self.config_notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
    
    def _create_framework_tab(self):
        """Create framework settings tab"""
        # Main scrollable frame
        canvas = tk.Canvas(self.framework_tab)
        scrollbar = ttk.Scrollbar(self.framework_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Framework configuration frame
        framework_frame = ttk.LabelFrame(scrollable_frame, text="Framework Configuration", padding=10)
        framework_frame.pack(fill='x', padx=10, pady=10)
        
        # Version
        version_frame = ttk.Frame(framework_frame)
        version_frame.pack(fill='x', pady=5)
        ttk.Label(version_frame, text="Framework Version:", width=20).pack(side='left')
        self.version_label = ttk.Label(version_frame, text="1.0.0", font=('Arial', 9, 'bold'))
        self.version_label.pack(side='left')
        
        # Browser selection
        browser_frame = ttk.Frame(framework_frame)
        browser_frame.pack(fill='x', pady=5)
        ttk.Label(browser_frame, text="Browser:", width=20).pack(side='left')
        self.browser_var = tk.StringVar(value="chrome")
        browser_combo = ttk.Combobox(
            browser_frame, 
            textvariable=self.browser_var,
            values=["chrome", "firefox"],
            state="readonly",
            width=15
        )
        browser_combo.pack(side='left')
        browser_combo.bind('<<ComboboxSelected>>', self._on_config_changed)
        
        # Wait times
        wait_frame = ttk.LabelFrame(framework_frame, text="Wait Times (seconds)", padding=5)
        wait_frame.pack(fill='x', pady=10)
        
        # Implicit wait
        implicit_frame = ttk.Frame(wait_frame)
        implicit_frame.pack(fill='x', pady=2)
        ttk.Label(implicit_frame, text="Implicit Wait:", width=15).pack(side='left')
        self.implicit_wait_var = tk.StringVar(value="10")
        implicit_spin = ttk.Spinbox(
            implicit_frame,
            from_=1, to=60,
            textvariable=self.implicit_wait_var,
            width=10
        )
        implicit_spin.pack(side='left')
        implicit_spin.bind('<KeyRelease>', self._on_config_changed)
        
        # Explicit wait
        explicit_frame = ttk.Frame(wait_frame)
        explicit_frame.pack(fill='x', pady=2)
        ttk.Label(explicit_frame, text="Explicit Wait:", width=15).pack(side='left')
        self.explicit_wait_var = tk.StringVar(value="30")
        explicit_spin = ttk.Spinbox(
            explicit_frame,
            from_=5, to=120,
            textvariable=self.explicit_wait_var,
            width=10
        )
        explicit_spin.pack(side='left')
        explicit_spin.bind('<KeyRelease>', self._on_config_changed)
        
        # Screenshot settings
        screenshot_frame = ttk.LabelFrame(framework_frame, text="Screenshot Settings", padding=5)
        screenshot_frame.pack(fill='x', pady=10)
        
        self.screenshot_on_step_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            screenshot_frame,
            text="Take screenshot on each step",
            variable=self.screenshot_on_step_var,
            command=self._on_config_changed
        ).pack(anchor='w')
        
        self.screenshot_on_failure_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            screenshot_frame,
            text="Take screenshot on failure",
            variable=self.screenshot_on_failure_var,
            command=self._on_config_changed
        ).pack(anchor='w')
        
        # Execution settings
        execution_frame = ttk.LabelFrame(framework_frame, text="Execution Settings", padding=5)
        execution_frame.pack(fill='x', pady=10)
        
        # Retry attempts
        retry_frame = ttk.Frame(execution_frame)
        retry_frame.pack(fill='x', pady=2)
        ttk.Label(retry_frame, text="Max Retry Attempts:", width=18).pack(side='left')
        self.retry_attempts_var = tk.StringVar(value="3")
        retry_spin = ttk.Spinbox(
            retry_frame,
            from_=0, to=10,
            textvariable=self.retry_attempts_var,
            width=10
        )
        retry_spin.pack(side='left')
        retry_spin.bind('<KeyRelease>', self._on_config_changed)
        
        self.parallel_execution_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            execution_frame,
            text="Enable parallel execution (Future feature)",
            variable=self.parallel_execution_var,
            state='disabled'
        ).pack(anchor='w', pady=2)
        
        self.video_recording_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            execution_frame,
            text="Enable video recording (Future feature)",
            variable=self.video_recording_var,
            state='disabled'
        ).pack(anchor='w', pady=2)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _create_reporting_tab(self):
        """Create reporting settings tab"""
        # Main frame
        main_frame = ttk.Frame(self.reporting_tab)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Report types
        types_frame = ttk.LabelFrame(main_frame, text="Report Types", padding=10)
        types_frame.pack(fill='x', pady=(0, 10))
        
        self.json_reports_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            types_frame,
            text="Generate JSON reports",
            variable=self.json_reports_var,
            command=self._on_config_changed
        ).pack(anchor='w')
        
        self.word_reports_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            types_frame,
            text="Generate Word reports",
            variable=self.word_reports_var,
            command=self._on_config_changed
        ).pack(anchor='w')
        
        self.screenshot_embedding_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            types_frame,
            text="Embed screenshots in reports",
            variable=self.screenshot_embedding_var,
            command=self._on_config_changed
        ).pack(anchor='w')
        
        # Directory settings
        dirs_frame = ttk.LabelFrame(main_frame, text="Directory Settings", padding=10)
        dirs_frame.pack(fill='x', pady=(0, 10))
        
        # Report directory
        report_dir_frame = ttk.Frame(dirs_frame)
        report_dir_frame.pack(fill='x', pady=5)
        ttk.Label(report_dir_frame, text="Report Directory:", width=18).pack(side='left')
        self.report_dir_var = tk.StringVar(value="./reports")
        report_dir_entry = ttk.Entry(report_dir_frame, textvariable=self.report_dir_var, width=30)
        report_dir_entry.pack(side='left', padx=(0, 5))
        report_dir_entry.bind('<KeyRelease>', self._on_config_changed)
        ttk.Button(
            report_dir_frame,
            text="Browse",
            command=lambda: self._browse_directory(self.report_dir_var)
        ).pack(side='left')
        
        # Screenshot directory
        screenshot_dir_frame = ttk.Frame(dirs_frame)
        screenshot_dir_frame.pack(fill='x', pady=5)
        ttk.Label(screenshot_dir_frame, text="Screenshot Directory:", width=18).pack(side='left')
        self.screenshot_dir_var = tk.StringVar(value="./screenshots")
        screenshot_dir_entry = ttk.Entry(screenshot_dir_frame, textvariable=self.screenshot_dir_var, width=30)
        screenshot_dir_entry.pack(side='left', padx=(0, 5))
        screenshot_dir_entry.bind('<KeyRelease>', self._on_config_changed)
        ttk.Button(
            screenshot_dir_frame,
            text="Browse",
            command=lambda: self._browse_directory(self.screenshot_dir_var)
        ).pack(side='left')
        
        # Report cleanup settings
        cleanup_frame = ttk.LabelFrame(main_frame, text="Cleanup Settings", padding=10)
        cleanup_frame.pack(fill='x', pady=(0, 10))
        
        # Auto cleanup
        self.auto_cleanup_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            cleanup_frame,
            text="Auto cleanup old files",
            variable=self.auto_cleanup_var,
            command=self._on_config_changed
        ).pack(anchor='w')
        
        # Cleanup days
        cleanup_days_frame = ttk.Frame(cleanup_frame)
        cleanup_days_frame.pack(fill='x', pady=5)
        ttk.Label(cleanup_days_frame, text="Keep files for (days):", width=18).pack(side='left')
        self.cleanup_days_var = tk.StringVar(value="7")
        cleanup_spin = ttk.Spinbox(
            cleanup_days_frame,
            from_=1, to=365,
            textvariable=self.cleanup_days_var,
            width=10
        )
        cleanup_spin.pack(side='left')
        cleanup_spin.bind('<KeyRelease>', self._on_config_changed)
    
    def _create_browser_tab(self):
        """Create browser settings tab"""
        # Main frame
        main_frame = ttk.Frame(self.browser_tab)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Browser options
        options_frame = ttk.LabelFrame(main_frame, text="Browser Options", padding=10)
        options_frame.pack(fill='x', pady=(0, 10))
        
        self.headless_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Run in headless mode",
            variable=self.headless_var,
            command=self._on_config_changed
        ).pack(anchor='w')
        
        self.maximize_window_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Maximize browser window",
            variable=self.maximize_window_var,
            command=self._on_config_changed
        ).pack(anchor='w')
        
        # Window size settings
        window_frame = ttk.LabelFrame(main_frame, text="Window Size", padding=10)
        window_frame.pack(fill='x', pady=(0, 10))
        
        size_frame = ttk.Frame(window_frame)
        size_frame.pack(fill='x')
        
        ttk.Label(size_frame, text="Width:", width=8).pack(side='left')
        self.window_width_var = tk.StringVar(value="1920")
        width_entry = ttk.Entry(size_frame, textvariable=self.window_width_var, width=8)
        width_entry.pack(side='left', padx=(0, 10))
        width_entry.bind('<KeyRelease>', self._on_config_changed)
        
        ttk.Label(size_frame, text="Height:", width=8).pack(side='left')
        self.window_height_var = tk.StringVar(value="1080")
        height_entry = ttk.Entry(size_frame, textvariable=self.window_height_var, width=8)
        height_entry.pack(side='left')
        height_entry.bind('<KeyRelease>', self._on_config_changed)
        
        # Chrome specific options
        chrome_frame = ttk.LabelFrame(main_frame, text="Chrome Options", padding=10)
        chrome_frame.pack(fill='x', pady=(0, 10))
        
        self.disable_images_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            chrome_frame,
            text="Disable image loading (faster execution)",
            variable=self.disable_images_var,
            command=self._on_config_changed
        ).pack(anchor='w')
        
        self.disable_notifications_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            chrome_frame,
            text="Disable notifications",
            variable=self.disable_notifications_var,
            command=self._on_config_changed
        ).pack(anchor='w')
        
        # Additional arguments
        args_frame = ttk.LabelFrame(main_frame, text="Additional Browser Arguments", padding=10)
        args_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(args_frame, text="Custom arguments (one per line):").pack(anchor='w')
        self.browser_args_text = tk.Text(args_frame, height=4, width=50)
        self.browser_args_text.pack(fill='x', pady=5)
        self.browser_args_text.bind('<KeyRelease>', self._on_config_changed)
        
        # Add some common arguments as examples
        example_args = "--disable-dev-shm-usage\n--no-sandbox\n--disable-gpu"
        self.browser_args_text.insert('1.0', example_args)
    
    def _create_advanced_tab(self):
        """Create advanced settings tab"""
        # Main frame
        main_frame = ttk.Frame(self.advanced_tab)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Logging settings
        logging_frame = ttk.LabelFrame(main_frame, text="Logging Settings", padding=10)
        logging_frame.pack(fill='x', pady=(0, 10))
        
        # Log level
        log_level_frame = ttk.Frame(logging_frame)
        log_level_frame.pack(fill='x', pady=5)
        ttk.Label(log_level_frame, text="Log Level:", width=15).pack(side='left')
        self.log_level_var = tk.StringVar(value="INFO")
        log_level_combo = ttk.Combobox(
            log_level_frame,
            textvariable=self.log_level_var,
            values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            state="readonly",
            width=12
        )
        log_level_combo.pack(side='left')
        log_level_combo.bind('<<ComboboxSelected>>', self._on_config_changed)
        
        # Log file settings
        self.log_to_file_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            logging_frame,
            text="Log to file",
            variable=self.log_to_file_var,
            command=self._on_config_changed
        ).pack(anchor='w')
        
        self.log_to_console_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            logging_frame,
            text="Log to console",
            variable=self.log_to_console_var,
            command=self._on_config_changed
        ).pack(anchor='w')
        
        # Performance settings
        performance_frame = ttk.LabelFrame(main_frame, text="Performance Settings", padding=10)
        performance_frame.pack(fill='x', pady=(0, 10))
        
        # Element wait strategy
        wait_strategy_frame = ttk.Frame(performance_frame)
        wait_strategy_frame.pack(fill='x', pady=5)
        ttk.Label(wait_strategy_frame, text="Element Wait Strategy:", width=20).pack(side='left')
        self.wait_strategy_var = tk.StringVar(value="presence")
        strategy_combo = ttk.Combobox(
            wait_strategy_frame,
            textvariable=self.wait_strategy_var,
            values=["presence", "visibility", "clickable"],
            state="readonly",
            width=15
        )
        strategy_combo.pack(side='left')
        strategy_combo.bind('<<ComboboxSelected>>', self._on_config_changed)
        
        # Page load strategy
        page_load_frame = ttk.Frame(performance_frame)
        page_load_frame.pack(fill='x', pady=5)
        ttk.Label(page_load_frame, text="Page Load Strategy:", width=20).pack(side='left')
        self.page_load_strategy_var = tk.StringVar(value="normal")
        page_load_combo = ttk.Combobox(
            page_load_frame,
            textvariable=self.page_load_strategy_var,
            values=["normal", "eager", "none"],
            state="readonly",
            width=15
        )
        page_load_combo.pack(side='left')
        page_load_combo.bind('<<ComboboxSelected>>', self._on_config_changed)
        
        # Security settings
        security_frame = ttk.LabelFrame(main_frame, text="Security Settings", padding=10)
        security_frame.pack(fill='x', pady=(0, 10))
        
        self.ignore_ssl_errors_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            security_frame,
            text="Ignore SSL certificate errors",
            variable=self.ignore_ssl_errors_var,
            command=self._on_config_changed
        ).pack(anchor='w')
        
        self.disable_web_security_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            security_frame,
            text="Disable web security (for testing)",
            variable=self.disable_web_security_var,
            command=self._on_config_changed
        ).pack(anchor='w')
        
        # Environment settings
        env_frame = ttk.LabelFrame(main_frame, text="Environment Settings", padding=10)
        env_frame.pack(fill='x')
        
        # Test environment
        env_select_frame = ttk.Frame(env_frame)
        env_select_frame.pack(fill='x', pady=5)
        ttk.Label(env_select_frame, text="Test Environment:", width=15).pack(side='left')
        self.test_env_var = tk.StringVar(value="development")
        env_combo = ttk.Combobox(
            env_select_frame,
            textvariable=self.test_env_var,
            values=["development", "staging", "production"],
            state="readonly",
            width=15
        )
        env_combo.pack(side='left')
        env_combo.bind('<<ComboboxSelected>>', self._on_config_changed)
    
    def _browse_directory(self, var: tk.StringVar):
        """Browse for directory"""
        directory = filedialog.askdirectory(initialdir=var.get())
        if directory:
            var.set(directory)
            self._on_config_changed()
    
    def _on_config_changed(self, event=None):
        """Handle configuration change"""
        self.unsaved_changes = True
        self.status_label.config(text="Unsaved changes", foreground='orange')
    
    def _on_tab_changed(self, event):
        """Handle tab change"""
        # This could be used to perform tab-specific updates
        pass
    
    def _load_configuration(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file_path):
                with open(self.config_file_path, 'r') as file:
                    self.config_data = json.load(file)
                
                self._update_ui_from_config()
                self.status_label.config(text="Configuration loaded", foreground='green')
                self.unsaved_changes = False
                
            else:
                self._create_default_config()
                
        except Exception as e:
            error_msg = f"Failed to load configuration: {str(e)}"
            self.logger.error(error_msg)
            self.status_label.config(text="Load error", foreground='red')
            messagebox.showerror("Load Error", error_msg)
    
    def _update_ui_from_config(self):
        """Update UI elements from configuration data"""
        try:
            framework_config = self.config_data.get('framework_config', {})
            reporting_config = self.config_data.get('reporting', {})
            
            # Framework settings
            self.browser_var.set(framework_config.get('browser', 'chrome'))
            self.implicit_wait_var.set(str(framework_config.get('implicit_wait', 10)))
            self.explicit_wait_var.set(str(framework_config.get('explicit_wait', 30)))
            self.screenshot_on_step_var.set(framework_config.get('screenshot_on_step', True))
            self.screenshot_on_failure_var.set(framework_config.get('screenshot_on_failure', True))
            self.retry_attempts_var.set(str(framework_config.get('max_retry_attempts', 3)))
            self.parallel_execution_var.set(framework_config.get('parallel_execution', False))
            self.video_recording_var.set(framework_config.get('video_recording', False))
            
            # Reporting settings
            self.json_reports_var.set(reporting_config.get('json_reports', True))
            self.word_reports_var.set(reporting_config.get('word_reports', True))
            self.screenshot_embedding_var.set(reporting_config.get('screenshot_embedding', True))
            self.report_dir_var.set(reporting_config.get('report_directory', './reports'))
            self.screenshot_dir_var.set(reporting_config.get('screenshot_directory', './screenshots'))
            
            # Browser settings
            browser_settings = framework_config.get('browser_settings', {})
            self.headless_var.set(browser_settings.get('headless', False))
            self.maximize_window_var.set(browser_settings.get('maximize_window', True))
            self.window_width_var.set(str(browser_settings.get('window_width', 1920)))
            self.window_height_var.set(str(browser_settings.get('window_height', 1080)))
            self.disable_images_var.set(browser_settings.get('disable_images', False))
            self.disable_notifications_var.set(browser_settings.get('disable_notifications', True))
            
            # Advanced settings
            advanced_settings = framework_config.get('advanced_settings', {})
            self.log_level_var.set(advanced_settings.get('log_level', 'INFO'))
            self.log_to_file_var.set(advanced_settings.get('log_to_file', True))
            self.log_to_console_var.set(advanced_settings.get('log_to_console', True))
            self.wait_strategy_var.set(advanced_settings.get('element_wait_strategy', 'presence'))
            self.page_load_strategy_var.set(advanced_settings.get('page_load_strategy', 'normal'))
            self.ignore_ssl_errors_var.set(advanced_settings.get('ignore_ssl_errors', False))
            self.disable_web_security_var.set(advanced_settings.get('disable_web_security', False))
            self.test_env_var.set(advanced_settings.get('test_environment', 'development'))
            
            # Browser arguments
            browser_args = browser_settings.get('additional_arguments', [])
            self.browser_args_text.delete('1.0', tk.END)
            if browser_args:
                self.browser_args_text.insert('1.0', '\n'.join(browser_args))
            
        except Exception as e:
            self.logger.error(f"Failed to update UI from config: {str(e)}")
    
    def _create_default_config(self):
        """Create default configuration"""
        self.config_data = {
            "framework_config": {
                "version": "1.0.0",
                "browser": "chrome",
                "implicit_wait": 10,
                "explicit_wait": 30,
                "screenshot_on_step": True,
                "screenshot_on_failure": True,
                "video_recording": False,
                "parallel_execution": False,
                "max_retry_attempts": 3,
                "browser_settings": {
                    "headless": False,
                    "maximize_window": True,
                    "window_width": 1920,
                    "window_height": 1080,
                    "disable_images": False,
                    "disable_notifications": True,
                    "additional_arguments": [
                        "--disable-dev-shm-usage",
                        "--no-sandbox",
                        "--disable-gpu"
                    ]
                },
                "advanced_settings": {
                    "log_level": "INFO",
                    "log_to_file": True,
                    "log_to_console": True,
                    "element_wait_strategy": "presence",
                    "page_load_strategy": "normal",
                    "ignore_ssl_errors": False,
                    "disable_web_security": False,
                    "test_environment": "development"
                }
            },
            "reporting": {
                "json_reports": True,
                "word_reports": True,
                "screenshot_embedding": True,
                "report_directory": "./reports",
                "screenshot_directory": "./screenshots",
                "auto_cleanup": False,
                "cleanup_days": 7
            },
            "test_scenarios": []
        }
        
        self._update_ui_from_config()
        self.status_label.config(text="Default configuration created", foreground='blue')
    
    def _collect_config_from_ui(self) -> Dict[str, Any]:
        """Collect configuration data from UI elements"""
        try:
            # Get browser arguments
            browser_args_text = self.browser_args_text.get('1.0', tk.END).strip()
            browser_args = [arg.strip() for arg in browser_args_text.split('\n') if arg.strip()]
            
            config = {
                "framework_config": {
                    "version": "1.0.0",
                    "browser": self.browser_var.get(),
                    "implicit_wait": int(self.implicit_wait_var.get()),
                    "explicit_wait": int(self.explicit_wait_var.get()),
                    "screenshot_on_step": self.screenshot_on_step_var.get(),
                    "screenshot_on_failure": self.screenshot_on_failure_var.get(),
                    "video_recording": self.video_recording_var.get(),
                    "parallel_execution": self.parallel_execution_var.get(),
                    "max_retry_attempts": int(self.retry_attempts_var.get()),
                    "browser_settings": {
                        "headless": self.headless_var.get(),
                        "maximize_window": self.maximize_window_var.get(),
                        "window_width": int(self.window_width_var.get()),
                        "window_height": int(self.window_height_var.get()),
                        "disable_images": self.disable_images_var.get(),
                        "disable_notifications": self.disable_notifications_var.get(),
                        "additional_arguments": browser_args
                    },
                    "advanced_settings": {
                        "log_level": self.log_level_var.get(),
                        "log_to_file": self.log_to_file_var.get(),
                        "log_to_console": self.log_to_console_var.get(),
                        "element_wait_strategy": self.wait_strategy_var.get(),
                        "page_load_strategy": self.page_load_strategy_var.get(),
                        "ignore_ssl_errors": self.ignore_ssl_errors_var.get(),
                        "disable_web_security": self.disable_web_security_var.get(),
                        "test_environment": self.test_env_var.get()
                    }
                },
                "reporting": {
                    "json_reports": self.json_reports_var.get(),
                    "word_reports": self.word_reports_var.get(),
                    "screenshot_embedding": self.screenshot_embedding_var.get(),
                    "report_directory": self.report_dir_var.get(),
                    "screenshot_directory": self.screenshot_dir_var.get(),
                    "auto_cleanup": getattr(self, 'auto_cleanup_var', tk.BooleanVar(value=False)).get(),
                    "cleanup_days": int(getattr(self, 'cleanup_days_var', tk.StringVar(value="7")).get())
                },
                "test_scenarios": self.config_data.get('test_scenarios', [])
            }
            
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to collect config from UI: {str(e)}")
            raise
    
    def _save_config_file(self):
        """Save configuration to file"""
        try:
            # Collect current configuration from UI
            config = self._collect_config_from_ui()
            
            # Ensure config directory exists
            os.makedirs(os.path.dirname(self.config_file_path), exist_ok=True)
            
            # Save to file
            with open(self.config_file_path, 'w') as file:
                json.dump(config, file, indent=4)
            
            self.config_data = config
            self.unsaved_changes = False
            self.status_label.config(text="Configuration saved", foreground='green')
            self.logger.info(f"Configuration saved to: {self.config_file_path}")
            
            # Notify callback
            if self.config_callback:
                self.config_callback(config)
            
        except Exception as e:
            error_msg = f"Failed to save configuration: {str(e)}"
            self.logger.error(error_msg)
            self.status_label.config(text="Save error", foreground='red')
            messagebox.showerror("Save Error", error_msg)
    
    def _load_config_file(self):
        """Load configuration from file dialog"""
        if self.unsaved_changes:
            result = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save them before loading a new configuration?"
            )
            if result is True:
                self._save_config_file()
            elif result is None:  # Cancel
                return
        
        file_path = filedialog.askopenfilename(
            title="Load Configuration File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir="config"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    config = json.load(file)
                
                self.config_data = config
                self.config_file_path = file_path
                self._update_ui_from_config()
                self.unsaved_changes = False
                self.status_label.config(text=f"Loaded: {os.path.basename(file_path)}", foreground='green')
                self.logger.info(f"Configuration loaded from: {file_path}")
                
            except Exception as e:
                error_msg = f"Failed to load configuration: {str(e)}"
                self.logger.error(error_msg)
                messagebox.showerror("Load Error", error_msg)
    
    def _reset_to_default(self):
        """Reset configuration to default values"""
        if self.unsaved_changes:
            result = messagebox.askyesno(
                "Unsaved Changes",
                "You have unsaved changes. Are you sure you want to reset to default configuration?"
            )
            if not result:
                return
        
        result = messagebox.askyesno(
            "Reset Configuration",
            "Are you sure you want to reset all settings to default values?"
        )
        
        if result:
            self._create_default_config()
            self.unsaved_changes = True
            self.status_label.config(text="Reset to default (unsaved)", foreground='orange')
            self.logger.info("Configuration reset to default values")
    
    def _validate_config(self):
        """Validate current configuration"""
        try:
            config = self._collect_config_from_ui()
            
            if self.validator.validate_master_config(config):
                self.status_label.config(text="Configuration valid", foreground='green')
                messagebox.showinfo("Validation Success", "Configuration is valid!")
            else:
                self.status_label.config(text="Configuration invalid", foreground='red')
                messagebox.showerror("Validation Failed", "Configuration validation failed. Check logs for details.")
                
        except Exception as e:
            error_msg = f"Failed to validate configuration: {str(e)}"
            self.logger.error(error_msg)
            self.status_label.config(text="Validation error", foreground='red')
            messagebox.showerror("Validation Error", error_msg)
    
    def load_config_file(self, file_path: str):
        """Public method to load configuration from specific path"""
        try:
            with open(file_path, 'r') as file:
                config = json.load(file)
            
            self.config_data = config
            self.config_file_path = file_path
            self._update_ui_from_config()
            self.unsaved_changes = False
            self.status_label.config(text=f"Loaded: {os.path.basename(file_path)}", foreground='green')
            self.logger.info(f"Configuration loaded from: {file_path}")
            
        except Exception as e:
            error_msg = f"Failed to load configuration: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
    
    def save_config_file(self, file_path: str):
        """Public method to save configuration to specific path"""
        try:
            config = self._collect_config_from_ui()
            
            with open(file_path, 'w') as file:
                json.dump(config, file, indent=4)
            
            self.logger.info(f"Configuration saved to: {file_path}")
            
        except Exception as e:
            error_msg = f"Failed to save configuration: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
    
    def get_current_config(self) -> Dict[str, Any]:
        """Get current configuration data"""
        return self._collect_config_from_ui()
    
    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes"""
        return self.unsaved_changes
