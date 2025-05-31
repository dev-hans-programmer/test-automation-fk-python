"""
Scenario Selector Component
GUI component for selecting and managing test scenarios
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from typing import List, Dict, Any, Callable

from framework.utils.logger import Logger


class ScenarioSelector:
    def __init__(self, parent: tk.Widget, selection_callback: Callable[[List[Dict]], None]):
        """Initialize Scenario Selector"""
        self.parent = parent
        self.selection_callback = selection_callback
        self.logger = Logger()
        
        # Data
        self.scenarios = []
        self.selected_scenarios = []
        
        # Create UI
        self._create_ui()
        self._load_scenarios()
    
    def _create_ui(self):
        """Create the user interface"""
        # Main container
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(self.main_frame, text="Test Scenarios", font=('Arial', 14, 'bold'))
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Control frame
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(fill='x', pady=(0, 10))
        
        # Buttons
        ttk.Button(control_frame, text="Refresh", command=self._refresh_scenarios).pack(side='left', padx=(0, 5))
        ttk.Button(control_frame, text="Select All", command=self._select_all).pack(side='left', padx=(0, 5))
        ttk.Button(control_frame, text="Select None", command=self._select_none).pack(side='left', padx=(0, 5))
        ttk.Button(control_frame, text="Toggle Execution", command=self._toggle_execution).pack(side='left', padx=(0, 5))
        
        # Search frame
        search_frame = ttk.Frame(self.main_frame)
        search_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").pack(side='left')
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search_changed)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side='left', padx=(5, 0))
        
        # Scenarios frame with scrollbar
        scenarios_frame = ttk.Frame(self.main_frame)
        scenarios_frame.pack(fill='both', expand=True)
        
        # Create Treeview for scenarios
        columns = ('Name', 'Execute', 'Priority', 'Status', 'File')
        self.tree = ttk.Treeview(scenarios_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.tree.heading('Name', text='Scenario Name')
        self.tree.heading('Execute', text='Execute')
        self.tree.heading('Priority', text='Priority')
        self.tree.heading('Status', text='Status')
        self.tree.heading('File', text='Scenario File')
        
        self.tree.column('Name', width=200)
        self.tree.column('Execute', width=80)
        self.tree.column('Priority', width=80)
        self.tree.column('Status', width=100)
        self.tree.column('File', width=200)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(scenarios_frame, orient='vertical', command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(scenarios_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Bind events
        self.tree.bind('<Double-1>', self._on_item_double_click)
        self.tree.bind('<Button-1>', self._on_item_select)
        self.tree.bind('<space>', self._on_space_pressed)
        
        # Details frame
        details_frame = ttk.LabelFrame(self.main_frame, text="Scenario Details", padding=10)
        details_frame.pack(fill='x', pady=(10, 0))
        
        # Details text widget
        self.details_text = tk.Text(details_frame, height=8, wrap=tk.WORD, state='disabled')
        details_scrollbar = ttk.Scrollbar(details_frame, orient='vertical', command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=details_scrollbar.set)
        
        self.details_text.pack(side='left', fill='both', expand=True)
        details_scrollbar.pack(side='right', fill='y')
        
        # Status frame
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill='x', pady=(10, 0))
        
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.pack(side='left')
        
        self.selected_count_label = ttk.Label(status_frame, text="Selected: 0")
        self.selected_count_label.pack(side='right')
    
    def _load_scenarios(self):
        """Load scenarios from configuration"""
        try:
            config_path = "config/master_config.json"
            if os.path.exists(config_path):
                with open(config_path, 'r') as file:
                    config = json.load(file)
                
                self.scenarios = config.get('test_scenarios', [])
                self._populate_tree()
                self.status_label.config(text=f"Loaded {len(self.scenarios)} scenarios")
            else:
                self.status_label.config(text="Configuration file not found")
                
        except Exception as e:
            error_msg = f"Failed to load scenarios: {str(e)}"
            self.logger.error(error_msg)
            self.status_label.config(text="Error loading scenarios")
            messagebox.showerror("Load Error", error_msg)
    
    def _populate_tree(self):
        """Populate treeview with scenarios"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add scenarios
        for i, scenario in enumerate(self.scenarios):
            name = scenario.get('name', f'Scenario {i+1}')
            execute = scenario.get('execute', 'n')
            priority = scenario.get('priority', 999)
            status = self._get_scenario_status(scenario)
            file_path = scenario.get('scenario_file', 'N/A')
            
            item_id = self.tree.insert('', 'end', values=(name, execute, priority, status, file_path))
            
            # Color code based on execution status
            if execute.lower() == 'y':
                self.tree.set(item_id, 'Execute', '✓ Yes')
                self.tree.item(item_id, tags=('enabled',))
            else:
                self.tree.set(item_id, 'Execute', '✗ No')
                self.tree.item(item_id, tags=('disabled',))
        
        # Configure tags
        self.tree.tag_configure('enabled', background='#e8f5e8')
        self.tree.tag_configure('disabled', background='#f5e8e8')
        
        self._update_selected_count()
    
    def _get_scenario_status(self, scenario: Dict[str, Any]) -> str:
        """Get scenario validation status"""
        try:
            scenario_file = scenario.get('scenario_file', '')
            test_data_file = scenario.get('test_data_file', '')
            
            if not os.path.exists(scenario_file):
                return "Missing Scenario File"
            elif not os.path.exists(test_data_file):
                return "Missing Test Data"
            else:
                return "Ready"
        except:
            return "Error"
    
    def _refresh_scenarios(self):
        """Refresh scenarios list"""
        self.status_label.config(text="Refreshing...")
        self._load_scenarios()
    
    def _select_all(self):
        """Select all scenarios for execution"""
        for i, scenario in enumerate(self.scenarios):
            scenario['execute'] = 'y'
        self._save_scenarios()
        self._populate_tree()
    
    def _select_none(self):
        """Deselect all scenarios"""
        for i, scenario in enumerate(self.scenarios):
            scenario['execute'] = 'n'
        self._save_scenarios()
        self._populate_tree()
    
    def _toggle_execution(self):
        """Toggle execution for selected scenarios"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showinfo("No Selection", "Please select scenarios to toggle")
            return
        
        for item in selected_items:
            index = self.tree.index(item)
            scenario = self.scenarios[index]
            current_execute = scenario.get('execute', 'n')
            scenario['execute'] = 'n' if current_execute.lower() == 'y' else 'y'
        
        self._save_scenarios()
        self._populate_tree()
    
    def _save_scenarios(self):
        """Save scenarios back to configuration"""
        try:
            config_path = "config/master_config.json"
            with open(config_path, 'r') as file:
                config = json.load(file)
            
            config['test_scenarios'] = self.scenarios
            
            with open(config_path, 'w') as file:
                json.dump(config, file, indent=4)
            
            self.logger.info("Scenarios configuration saved")
            
        except Exception as e:
            error_msg = f"Failed to save scenarios: {str(e)}"
            self.logger.error(error_msg)
            messagebox.showerror("Save Error", error_msg)
    
    def _on_search_changed(self, *args):
        """Handle search text change"""
        search_text = self.search_var.get().lower()
        
        # Clear and repopulate with filtered results
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for i, scenario in enumerate(self.scenarios):
            name = scenario.get('name', '').lower()
            file_path = scenario.get('scenario_file', '').lower()
            
            if search_text in name or search_text in file_path:
                name_display = scenario.get('name', f'Scenario {i+1}')
                execute = scenario.get('execute', 'n')
                priority = scenario.get('priority', 999)
                status = self._get_scenario_status(scenario)
                file_path_display = scenario.get('scenario_file', 'N/A')
                
                item_id = self.tree.insert('', 'end', values=(name_display, execute, priority, status, file_path_display))
                
                if execute.lower() == 'y':
                    self.tree.set(item_id, 'Execute', '✓ Yes')
                    self.tree.item(item_id, tags=('enabled',))
                else:
                    self.tree.set(item_id, 'Execute', '✗ No')
                    self.tree.item(item_id, tags=('disabled',))
    
    def _on_item_select(self, event):
        """Handle item selection"""
        selected_items = self.tree.selection()
        if selected_items:
            item = selected_items[0]
            index = self.tree.index(item)
            self._show_scenario_details(self.scenarios[index])
        
        self._update_selected_scenarios()
    
    def _on_item_double_click(self, event):
        """Handle item double click"""
        selected_items = self.tree.selection()
        if selected_items:
            self._toggle_execution()
    
    def _on_space_pressed(self, event):
        """Handle space key press"""
        self._toggle_execution()
    
    def _show_scenario_details(self, scenario: Dict[str, Any]):
        """Show detailed information about scenario"""
        details = f"Scenario Name: {scenario.get('name', 'N/A')}\n"
        details += f"Scenario File: {scenario.get('scenario_file', 'N/A')}\n"
        details += f"Test Data File: {scenario.get('test_data_file', 'N/A')}\n"
        details += f"Execute: {scenario.get('execute', 'N/A')}\n"
        details += f"Priority: {scenario.get('priority', 'N/A')}\n\n"
        
        # Load scenario file details if available
        try:
            scenario_file = scenario.get('scenario_file', '')
            if os.path.exists(scenario_file):
                with open(scenario_file, 'r') as file:
                    scenario_data = json.load(file)
                
                scenario_info = scenario_data.get('scenario_info', {})
                details += f"Description: {scenario_info.get('description', 'N/A')}\n"
                details += f"URL: {scenario_info.get('url', 'N/A')}\n"
                details += f"Expected Duration: {scenario_info.get('expected_duration', 'N/A')} seconds\n"
                details += f"Tags: {', '.join(scenario_info.get('tags', []))}\n"
                details += f"Total Steps: {len(scenario_data.get('test_steps', []))}\n"
                
        except Exception as e:
            details += f"\nError loading scenario details: {str(e)}\n"
        
        # Update details text widget
        self.details_text.config(state='normal')
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(1.0, details)
        self.details_text.config(state='disabled')
    
    def _update_selected_scenarios(self):
        """Update list of selected scenarios"""
        self.selected_scenarios = []
        selected_items = self.tree.selection()
        
        for item in selected_items:
            index = self.tree.index(item)
            self.selected_scenarios.append(self.scenarios[index])
        
        # Notify callback
        if self.selection_callback:
            self.selection_callback(self.selected_scenarios)
        
        self._update_selected_count()
    
    def _update_selected_count(self):
        """Update selected scenarios count"""
        enabled_count = len([s for s in self.scenarios if s.get('execute', 'n').lower() == 'y'])
        selected_count = len(self.selected_scenarios)
        
        self.selected_count_label.config(
            text=f"Enabled: {enabled_count} | Selected: {selected_count}"
        )
    
    def update_scenarios(self, scenarios: List[Dict[str, Any]]):
        """Update scenarios list from external source"""
        self.scenarios = scenarios
        self._populate_tree()
    
    def get_enabled_scenarios(self) -> List[Dict[str, Any]]:
        """Get list of scenarios enabled for execution"""
        return [s for s in self.scenarios if s.get('execute', 'n').lower() == 'y']
    
    def get_selected_scenarios(self) -> List[Dict[str, Any]]:
        """Get list of currently selected scenarios"""
        return self.selected_scenarios
