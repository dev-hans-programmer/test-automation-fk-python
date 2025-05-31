"""
Environment Selector Component
GUI component for selecting and managing test environments
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Any, Callable, Optional
from framework.utils.environment_manager import EnvironmentManager
from framework.utils.logger import Logger


class EnvironmentSelector:
    def __init__(self, parent: tk.Widget):
        """Initialize Environment Selector"""
        self.parent = parent
        self.logger = Logger()
        self.environment_manager = EnvironmentManager()
        self.on_environment_changed = None
        self.current_environment = None
        
        self._create_widgets()
        self._load_environments()
        
    def _create_widgets(self):
        """Create selector widgets"""
        # Main frame with modern styling
        self.main_frame = ttk.LabelFrame(self.parent, text="Environment Configuration", padding="20")
        self.main_frame.pack(fill='x', padx=15, pady=15)
        
        # Environment selection row
        env_frame = ttk.Frame(self.main_frame)
        env_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(env_frame, text="Environment:").pack(side='left', padx=(0, 10))
        
        self.environment_var = tk.StringVar()
        self.environment_combo = ttk.Combobox(
            env_frame, 
            textvariable=self.environment_var,
            state='readonly',
            width=20
        )
        self.environment_combo.pack(side='left', padx=(0, 10))
        self.environment_combo.bind('<<ComboboxSelected>>', self._on_environment_selected)
        
        # Buttons
        button_frame = ttk.Frame(env_frame)
        button_frame.pack(side='right')
        
        self.validate_btn = ttk.Button(
            button_frame,
            text="Validate",
            command=self._validate_environment,
            style='Accent.TButton'
        )
        self.validate_btn.pack(side='left', padx=(0, 10))
        
        self.refresh_btn = ttk.Button(
            button_frame,
            text="Refresh",
            command=self._refresh_environments,
            style='Secondary.TButton'
        )
        self.refresh_btn.pack(side='left')
        
        # Environment details frame
        details_frame = ttk.LabelFrame(self.main_frame, text="Environment Details", padding="5")
        details_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        # Create notebook for environment details
        self.details_notebook = ttk.Notebook(details_frame)
        self.details_notebook.pack(fill='both', expand=True)
        
        # Overview tab
        self.overview_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(self.overview_frame, text="Overview")
        
        self.overview_text = tk.Text(
            self.overview_frame,
            height=8,
            wrap='word',
            state='disabled',
            font=('Consolas', 9)
        )
        overview_scrollbar = ttk.Scrollbar(self.overview_frame, orient='vertical', command=self.overview_text.yview)
        self.overview_text.configure(yscrollcommand=overview_scrollbar.set)
        
        self.overview_text.pack(side='left', fill='both', expand=True)
        overview_scrollbar.pack(side='right', fill='y')
        
        # Test Data tab
        self.test_data_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(self.test_data_frame, text="Test Data")
        
        self.test_data_text = tk.Text(
            self.test_data_frame,
            height=8,
            wrap='word',
            state='disabled',
            font=('Consolas', 9)
        )
        test_data_scrollbar = ttk.Scrollbar(self.test_data_frame, orient='vertical', command=self.test_data_text.yview)
        self.test_data_text.configure(yscrollcommand=test_data_scrollbar.set)
        
        self.test_data_text.pack(side='left', fill='both', expand=True)
        test_data_scrollbar.pack(side='right', fill='y')
        
        # Credentials tab
        self.credentials_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(self.credentials_frame, text="Credentials")
        
        self.credentials_text = tk.Text(
            self.credentials_frame,
            height=8,
            wrap='word',
            state='disabled',
            font=('Consolas', 9)
        )
        credentials_scrollbar = ttk.Scrollbar(self.credentials_frame, orient='vertical', command=self.credentials_text.yview)
        self.credentials_text.configure(yscrollcommand=credentials_scrollbar.set)
        
        self.credentials_text.pack(side='left', fill='both', expand=True)
        credentials_scrollbar.pack(side='right', fill='y')
        
        # Status label
        self.status_label = ttk.Label(self.main_frame, text="No environment selected", foreground='gray')
        self.status_label.pack(pady=(10, 0))
        
    def _load_environments(self):
        """Load available environments"""
        try:
            environments = self.environment_manager.load_available_environments()
            
            # Update combobox
            env_names = [f"{env['name']} ({env['id']})" for env in environments]
            self.environment_combo['values'] = env_names
            
            # Store environment data for lookup
            self.environments_data = {f"{env['name']} ({env['id']})": env for env in environments}
            
            if env_names:
                self.environment_combo.set(env_names[0])
                self._on_environment_selected(None)
            else:
                self._show_no_environments_message()
                
        except Exception as e:
            self.logger.error(f"Failed to load environments: {str(e)}")
            messagebox.showerror("Error", f"Failed to load environments: {str(e)}")
            
    def _show_no_environments_message(self):
        """Show message when no environments are available"""
        self.status_label.config(text="No environments found", foreground='red')
        self._clear_details()
        
    def _clear_details(self):
        """Clear all detail displays"""
        for text_widget in [self.overview_text, self.test_data_text, self.credentials_text]:
            text_widget.config(state='normal')
            text_widget.delete(1.0, tk.END)
            text_widget.config(state='disabled')
            
    def _on_environment_selected(self, event):
        """Handle environment selection"""
        selected = self.environment_var.get()
        if not selected or selected not in self.environments_data:
            return
            
        env_data = self.environments_data[selected]
        env_id = env_data['id']
        
        try:
            # Load environment configuration
            if self.environment_manager.load_environment(env_id):
                self.current_environment = env_id
                self._display_environment_details()
                self.status_label.config(text=f"Environment loaded: {env_data['name']}", foreground='green')
                
                # Notify parent component
                if self.on_environment_changed:
                    self.on_environment_changed(env_id, self.environment_manager.get_environment_data())
            else:
                self.status_label.config(text=f"Failed to load environment: {env_data['name']}", foreground='red')
                
        except Exception as e:
            self.logger.error(f"Failed to select environment: {str(e)}")
            self.status_label.config(text=f"Error loading environment: {str(e)}", foreground='red')
            
    def _display_environment_details(self):
        """Display environment details in tabs"""
        env_data = self.environment_manager.get_environment_data()
        
        # Overview tab
        overview_text = f"Environment: {env_data.get('environment_name', 'Unknown')}\n"
        overview_text += f"ID: {env_data.get('environment_id', 'Unknown')}\n"
        overview_text += f"Description: {env_data.get('description', 'No description')}\n\n"
        overview_text += f"Base URL: {env_data.get('base_url', 'Not configured')}\n\n"
        
        # Timeout settings
        timeout_settings = env_data.get('timeout_settings', {})
        overview_text += "Timeout Settings:\n"
        for key, value in timeout_settings.items():
            overview_text += f"  {key}: {value}s\n"
        overview_text += "\n"
        
        # Browser settings
        browser_settings = env_data.get('browser_settings', {})
        overview_text += "Browser Settings:\n"
        for key, value in browser_settings.items():
            if isinstance(value, dict):
                overview_text += f"  {key}:\n"
                for sub_key, sub_value in value.items():
                    overview_text += f"    {sub_key}: {sub_value}\n"
            else:
                overview_text += f"  {key}: {value}\n"
        overview_text += "\n"
        
        # Feature flags
        feature_flags = env_data.get('feature_flags', {})
        overview_text += "Feature Flags:\n"
        for key, value in feature_flags.items():
            status = "✓ Enabled" if value else "✗ Disabled"
            overview_text += f"  {key}: {status}\n"
            
        self._update_text_widget(self.overview_text, overview_text)
        
        # Test Data tab
        test_data = env_data.get('test_data', {})
        test_data_text = "Test Data Summary:\n\n"
        
        for category, items in test_data.items():
            if isinstance(items, list):
                test_data_text += f"{category.title()}: {len(items)} items\n"
                for i, item in enumerate(items[:3]):  # Show first 3 items
                    if isinstance(item, dict):
                        name = item.get('name') or item.get('id') or f"Item {i+1}"
                        test_data_text += f"  • {name}\n"
                if len(items) > 3:
                    test_data_text += f"  ... and {len(items) - 3} more\n"
                test_data_text += "\n"
            else:
                test_data_text += f"{category.title()}: {items}\n\n"
                
        self._update_text_widget(self.test_data_text, test_data_text)
        
        # Credentials tab
        credentials = env_data.get('credentials', {})
        credentials_text = "Credentials Configuration:\n\n"
        
        for cred_type, cred_data in credentials.items():
            credentials_text += f"{cred_type.replace('_', ' ').title()}:\n"
            if isinstance(cred_data, dict):
                for key, value in cred_data.items():
                    # Mask sensitive data
                    if 'password' in key.lower() or 'key' in key.lower():
                        masked_value = '*' * min(len(str(value)), 8) if value else 'Not set'
                        credentials_text += f"  {key}: {masked_value}\n"
                    else:
                        credentials_text += f"  {key}: {value}\n"
            else:
                # Mask sensitive data
                if 'password' in cred_type.lower() or 'key' in cred_type.lower():
                    masked_value = '*' * min(len(str(cred_data)), 8) if cred_data else 'Not set'
                    credentials_text += f"  Value: {masked_value}\n"
                else:
                    credentials_text += f"  Value: {cred_data}\n"
            credentials_text += "\n"
            
        self._update_text_widget(self.credentials_text, credentials_text)
        
    def _update_text_widget(self, widget: tk.Text, content: str):
        """Update text widget content"""
        widget.config(state='normal')
        widget.delete(1.0, tk.END)
        widget.insert(1.0, content)
        widget.config(state='disabled')
        
    def _validate_environment(self):
        """Validate current environment configuration"""
        if not self.current_environment:
            messagebox.showwarning("Warning", "No environment selected")
            return
            
        try:
            validation_result = self.environment_manager.validate_environment_config(self.current_environment)
            
            if validation_result['valid']:
                message = "Environment configuration is valid!"
                if validation_result['warnings']:
                    message += "\n\nWarnings:\n" + "\n".join(f"• {w}" for w in validation_result['warnings'])
                messagebox.showinfo("Validation Result", message)
            else:
                message = "Environment configuration has errors:\n\n"
                message += "\n".join(f"• {e}" for e in validation_result['errors'])
                if validation_result['warnings']:
                    message += "\n\nWarnings:\n" + "\n".join(f"• {w}" for w in validation_result['warnings'])
                messagebox.showerror("Validation Failed", message)
                
        except Exception as e:
            self.logger.error(f"Validation failed: {str(e)}")
            messagebox.showerror("Error", f"Validation failed: {str(e)}")
            
    def _refresh_environments(self):
        """Refresh environments list"""
        self._load_environments()
        
    def set_environment_changed_callback(self, callback: Callable[[str, Dict[str, Any]], None]):
        """Set callback for environment changes"""
        self.on_environment_changed = callback
        
    def get_current_environment(self) -> Optional[str]:
        """Get current environment ID"""
        return self.current_environment
        
    def get_environment_manager(self) -> EnvironmentManager:
        """Get environment manager instance"""
        return self.environment_manager