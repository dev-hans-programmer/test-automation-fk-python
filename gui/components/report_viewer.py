"""
Report Viewer Component
GUI component for viewing and analyzing test reports
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

from framework.utils.logger import Logger
from gui.components.video_player import VideoPlayer


class ReportViewer:
    def __init__(self, parent: tk.Widget, selection_callback: Optional[callable] = None):
        """Initialize Report Viewer"""
        self.parent = parent
        self.selection_callback = selection_callback
        self.logger = Logger()
        
        # Data
        self.reports = []
        self.current_report = None
        
        # Create UI
        self._create_ui()
        self._load_reports()
    
    def _create_ui(self):
        """Create the user interface"""
        # Main container
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(self.main_frame, text="Test Reports", font=('Arial', 14, 'bold'))
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Create paned window for layout
        self.paned_window = ttk.PanedWindow(self.main_frame, orient='horizontal')
        self.paned_window.pack(fill='both', expand=True)
        
        # Left panel - Reports list
        left_panel = ttk.Frame(self.paned_window)
        self.paned_window.add(left_panel, weight=1)
        
        # Reports list frame
        reports_frame = ttk.LabelFrame(left_panel, text="Reports", padding=10)
        reports_frame.pack(fill='both', expand=True)
        
        # Control buttons
        control_frame = ttk.Frame(reports_frame)
        control_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Button(control_frame, text="Refresh", command=self._refresh_reports).pack(side='left', padx=(0, 5))
        ttk.Button(control_frame, text="Open Report", command=self._open_report_file).pack(side='left', padx=(0, 5))
        ttk.Button(control_frame, text="Delete", command=self._delete_report).pack(side='left', padx=(0, 5))
        ttk.Button(control_frame, text="Export", command=self._export_report).pack(side='left')
        
        # Filter frame
        filter_frame = ttk.Frame(reports_frame)
        filter_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(filter_frame, text="Filter:").pack(side='left')
        self.filter_var = tk.StringVar()
        self.filter_var.trace('w', self._on_filter_changed)
        filter_entry = ttk.Entry(filter_frame, textvariable=self.filter_var, width=20)
        filter_entry.pack(side='left', padx=(5, 10))
        
        # Sort options
        ttk.Label(filter_frame, text="Sort by:").pack(side='left')
        self.sort_var = tk.StringVar(value="date")
        sort_combo = ttk.Combobox(
            filter_frame, 
            textvariable=self.sort_var, 
            values=["date", "name", "status", "duration"],
            width=10,
            state="readonly"
        )
        sort_combo.pack(side='left', padx=(5, 0))
        sort_combo.bind('<<ComboboxSelected>>', self._on_sort_changed)
        
        # Reports tree
        tree_frame = ttk.Frame(reports_frame)
        tree_frame.pack(fill='both', expand=True)
        
        columns = ('Name', 'Date', 'Status', 'Scenarios', 'Duration')
        self.reports_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=12)
        
        # Configure columns
        self.reports_tree.heading('Name', text='Report Name')
        self.reports_tree.heading('Date', text='Date/Time')
        self.reports_tree.heading('Status', text='Status')
        self.reports_tree.heading('Scenarios', text='Scenarios')
        self.reports_tree.heading('Duration', text='Duration')
        
        self.reports_tree.column('Name', width=200)
        self.reports_tree.column('Date', width=150)
        self.reports_tree.column('Status', width=80)
        self.reports_tree.column('Scenarios', width=100)
        self.reports_tree.column('Duration', width=80)
        
        # Scrollbars for tree
        tree_v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.reports_tree.yview)
        tree_h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.reports_tree.xview)
        self.reports_tree.configure(yscrollcommand=tree_v_scrollbar.set, xscrollcommand=tree_h_scrollbar.set)
        
        # Pack tree and scrollbars
        self.reports_tree.pack(side='left', fill='both', expand=True)
        tree_v_scrollbar.pack(side='right', fill='y')
        tree_h_scrollbar.pack(side='bottom', fill='x')
        
        # Bind tree events
        self.reports_tree.bind('<Double-1>', self._on_report_double_click)
        self.reports_tree.bind('<<TreeviewSelect>>', self._on_report_select)
        
        # Right panel - Report details
        right_panel = ttk.Frame(self.paned_window)
        self.paned_window.add(right_panel, weight=2)
        
        # Create notebook for report details
        self.details_notebook = ttk.Notebook(right_panel)
        self.details_notebook.pack(fill='both', expand=True)
        
        # Summary tab
        self.summary_tab = ttk.Frame(self.details_notebook)
        self.details_notebook.add(self.summary_tab, text="Summary")
        self._create_summary_tab()
        
        # Scenarios tab
        self.scenarios_tab = ttk.Frame(self.details_notebook)
        self.details_notebook.add(self.scenarios_tab, text="Scenarios")
        self._create_scenarios_tab()
        
        # Raw data tab
        self.raw_data_tab = ttk.Frame(self.details_notebook)
        self.details_notebook.add(self.raw_data_tab, text="Raw Data")
        self._create_raw_data_tab()
        
        # Video playback tab
        self.video_tab = ttk.Frame(self.details_notebook)
        self.details_notebook.add(self.video_tab, text="Videos")
        self._create_video_tab()
    
    def _create_summary_tab(self):
        """Create summary tab content"""
        # Summary frame with scrollbar
        summary_frame = ttk.Frame(self.summary_tab)
        summary_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Report info frame
        info_frame = ttk.LabelFrame(summary_frame, text="Report Information", padding=10)
        info_frame.pack(fill='x', pady=(0, 10))
        
        # Info grid
        self.info_labels = {}
        info_fields = [
            ('Execution ID:', 'execution_id'),
            ('Start Time:', 'start_time'),
            ('End Time:', 'end_time'),
            ('Duration:', 'duration'),
            ('Status:', 'status'),
            ('Total Scenarios:', 'total_scenarios'),
            ('Passed Scenarios:', 'passed_scenarios'),
            ('Failed Scenarios:', 'failed_scenarios'),
            ('Success Rate:', 'success_rate')
        ]
        
        for i, (label_text, key) in enumerate(info_fields):
            row = i // 2
            col = (i % 2) * 2
            
            ttk.Label(info_frame, text=label_text).grid(row=row, column=col, sticky='w', padx=(0, 10), pady=2)
            label = ttk.Label(info_frame, text="N/A", font=('Arial', 9, 'bold'))
            label.grid(row=row, column=col+1, sticky='w', padx=(0, 30), pady=2)
            self.info_labels[key] = label
        
        # Charts frame (placeholder for future charts)
        charts_frame = ttk.LabelFrame(summary_frame, text="Execution Charts", padding=10)
        charts_frame.pack(fill='both', expand=True)
        
        charts_label = ttk.Label(charts_frame, text="Visual charts will be available in future version", 
                                font=('Arial', 10, 'italic'))
        charts_label.pack(expand=True)
    
    def _create_scenarios_tab(self):
        """Create scenarios tab content"""
        scenarios_frame = ttk.Frame(self.scenarios_tab)
        scenarios_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Scenarios tree
        scenarios_tree_frame = ttk.Frame(scenarios_frame)
        scenarios_tree_frame.pack(fill='both', expand=True)
        
        columns = ('Scenario', 'Status', 'Duration', 'Steps', 'Passed Steps', 'Failed Steps')
        self.scenarios_tree = ttk.Treeview(scenarios_tree_frame, columns=columns, show='headings')
        
        # Configure columns
        for col in columns:
            self.scenarios_tree.heading(col, text=col)
            self.scenarios_tree.column(col, width=100)
        
        # Scrollbars
        scenarios_v_scrollbar = ttk.Scrollbar(scenarios_tree_frame, orient='vertical', 
                                            command=self.scenarios_tree.yview)
        scenarios_h_scrollbar = ttk.Scrollbar(scenarios_tree_frame, orient='horizontal', 
                                            command=self.scenarios_tree.xview)
        self.scenarios_tree.configure(yscrollcommand=scenarios_v_scrollbar.set, 
                                    xscrollcommand=scenarios_h_scrollbar.set)
        
        # Pack scenarios tree
        self.scenarios_tree.pack(side='left', fill='both', expand=True)
        scenarios_v_scrollbar.pack(side='right', fill='y')
        scenarios_h_scrollbar.pack(side='bottom', fill='x')
        
        # Bind scenario selection
        self.scenarios_tree.bind('<<TreeviewSelect>>', self._on_scenario_select)
        
        # Steps details frame
        steps_frame = ttk.LabelFrame(scenarios_frame, text="Step Details", padding=10)
        steps_frame.pack(fill='x', pady=(10, 0))
        
        # Steps text widget
        self.steps_text = tk.Text(steps_frame, height=8, wrap=tk.WORD, state='disabled')
        steps_scrollbar = ttk.Scrollbar(steps_frame, orient='vertical', command=self.steps_text.yview)
        self.steps_text.configure(yscrollcommand=steps_scrollbar.set)
        
        self.steps_text.pack(side='left', fill='both', expand=True)
        steps_scrollbar.pack(side='right', fill='y')
    
    def _create_raw_data_tab(self):
        """Create raw data tab content"""
        raw_frame = ttk.Frame(self.raw_data_tab)
        raw_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Raw data text widget with scrollbar
        self.raw_text = tk.Text(raw_frame, wrap=tk.WORD, state='disabled', font=('Consolas', 9))
        raw_scrollbar = ttk.Scrollbar(raw_frame, orient='vertical', command=self.raw_text.yview)
        self.raw_text.configure(yscrollcommand=raw_scrollbar.set)
        
        self.raw_text.pack(side='left', fill='both', expand=True)
        raw_scrollbar.pack(side='right', fill='y')
    
    def _create_video_tab(self):
        """Create video playback tab content"""
        # Initialize video player component
        self.video_player = VideoPlayer(self.video_tab)
    
    def _load_reports(self):
        """Load reports from reports directory"""
        try:
            reports_dir = "reports"
            if not os.path.exists(reports_dir):
                os.makedirs(reports_dir, exist_ok=True)
                self.logger.info("Created reports directory")
                return
            
            self.reports = []
            
            for filename in os.listdir(reports_dir):
                if filename.endswith('.json') and filename.startswith('test_report_'):
                    filepath = os.path.join(reports_dir, filename)
                    try:
                        with open(filepath, 'r') as file:
                            report_data = json.load(file)
                        
                        # Extract report metadata
                        report_info = {
                            'filename': filename,
                            'filepath': filepath,
                            'data': report_data,
                            'created': datetime.fromtimestamp(os.path.getctime(filepath)),
                            'size': os.path.getsize(filepath)
                        }
                        
                        self.reports.append(report_info)
                        
                    except Exception as e:
                        self.logger.error(f"Failed to load report {filename}: {str(e)}")
            
            self._populate_reports_tree()
            
        except Exception as e:
            self.logger.error(f"Failed to load reports: {str(e)}")
    
    def _populate_reports_tree(self):
        """Populate reports tree with data"""
        # Clear existing items
        for item in self.reports_tree.get_children():
            self.reports_tree.delete(item)
        
        # Sort reports based on selected criteria
        sort_key = self.sort_var.get()
        if sort_key == "date":
            self.reports.sort(key=lambda x: x['created'], reverse=True)
        elif sort_key == "name":
            self.reports.sort(key=lambda x: x['filename'])
        elif sort_key == "status":
            self.reports.sort(key=lambda x: x['data'].get('execution_summary', {}).get('status', ''))
        elif sort_key == "duration":
            self.reports.sort(key=lambda x: x['data'].get('execution_summary', {}).get('duration', 0), reverse=True)
        
        # Apply filter
        filter_text = self.filter_var.get().lower()
        
        for report in self.reports:
            # Apply filter
            if filter_text and filter_text not in report['filename'].lower():
                continue
            
            # Extract display data
            summary = report['data'].get('execution_summary', {})
            name = report['filename'].replace('.json', '')
            date_str = report['created'].strftime('%Y-%m-%d %H:%M')
            status = summary.get('status', 'unknown')
            total_scenarios = summary.get('total_scenarios', 0)
            passed_scenarios = summary.get('passed_scenarios', 0)
            duration = summary.get('duration', 0)
            
            scenarios_text = f"{passed_scenarios}/{total_scenarios}"
            duration_text = f"{duration:.1f}s" if duration else "0s"
            
            # Insert into tree
            item_id = self.reports_tree.insert('', 'end', values=(
                name, date_str, status, scenarios_text, duration_text
            ))
            
            # Color coding based on status
            if status == 'completed':
                if passed_scenarios == total_scenarios and total_scenarios > 0:
                    self.reports_tree.item(item_id, tags=('success',))
                elif passed_scenarios > 0:
                    self.reports_tree.item(item_id, tags=('partial',))
                else:
                    self.reports_tree.item(item_id, tags=('failed',))
            else:
                self.reports_tree.item(item_id, tags=('error',))
        
        # Configure tags
        self.reports_tree.tag_configure('success', background='#e8f5e8')
        self.reports_tree.tag_configure('partial', background='#fff3cd')
        self.reports_tree.tag_configure('failed', background='#f8d7da')
        self.reports_tree.tag_configure('error', background='#f5c6cb')
    
    def _on_filter_changed(self, *args):
        """Handle filter change"""
        self._populate_reports_tree()
    
    def _on_sort_changed(self, event):
        """Handle sort change"""
        self._populate_reports_tree()
    
    def _on_report_select(self, event):
        """Handle report selection"""
        selected_items = self.reports_tree.selection()
        if selected_items:
            item = selected_items[0]
            index = self.reports_tree.index(item)
            
            # Find the report based on the filtered/sorted list
            filtered_reports = []
            filter_text = self.filter_var.get().lower()
            
            for report in self.reports:
                if not filter_text or filter_text in report['filename'].lower():
                    filtered_reports.append(report)
            
            # Sort the filtered reports
            sort_key = self.sort_var.get()
            if sort_key == "date":
                filtered_reports.sort(key=lambda x: x['created'], reverse=True)
            elif sort_key == "name":
                filtered_reports.sort(key=lambda x: x['filename'])
            elif sort_key == "status":
                filtered_reports.sort(key=lambda x: x['data'].get('execution_summary', {}).get('status', ''))
            elif sort_key == "duration":
                filtered_reports.sort(key=lambda x: x['data'].get('execution_summary', {}).get('duration', 0), reverse=True)
            
            if 0 <= index < len(filtered_reports):
                self.current_report = filtered_reports[index]
                self._display_report_details(self.current_report)
                
                if self.selection_callback:
                    self.selection_callback(self.current_report['filepath'])
    
    def _on_report_double_click(self, event):
        """Handle report double click - open in external application"""
        if self.current_report:
            try:
                import subprocess
                import platform
                
                filepath = self.current_report['filepath']
                
                if platform.system() == 'Windows':
                    os.startfile(filepath)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.call(['open', filepath])
                else:  # Linux
                    subprocess.call(['xdg-open', filepath])
                    
            except Exception as e:
                messagebox.showerror("Open Error", f"Failed to open report: {str(e)}")
    
    def _display_report_details(self, report_info: Dict[str, Any]):
        """Display detailed report information"""
        report_data = report_info['data']
        summary = report_data.get('execution_summary', {})
        
        # Update summary info
        info_mapping = {
            'execution_id': summary.get('execution_id', 'N/A'),
            'start_time': summary.get('start_time', 'N/A'),
            'end_time': summary.get('end_time', 'N/A'),
            'duration': f"{summary.get('duration', 0):.1f}s",
            'status': summary.get('status', 'N/A'),
            'total_scenarios': str(summary.get('total_scenarios', 0)),
            'passed_scenarios': str(summary.get('passed_scenarios', 0)),
            'failed_scenarios': str(summary.get('failed_scenarios', 0)),
            'success_rate': f"{summary.get('success_rate', 0):.1f}%"
        }
        
        for key, value in info_mapping.items():
            if key in self.info_labels:
                self.info_labels[key].config(text=value)
        
        # Update scenarios tree
        self._populate_scenarios_tree(report_data.get('scenarios', []))
        
        # Update raw data
        self._display_raw_data(report_data)
    
    def _populate_scenarios_tree(self, scenarios: List[Dict[str, Any]]):
        """Populate scenarios tree with data"""
        # Clear existing items
        for item in self.scenarios_tree.get_children():
            self.scenarios_tree.delete(item)
        
        for scenario in scenarios:
            name = scenario.get('scenario_name', 'Unknown')
            status = scenario.get('status', 'unknown')
            duration = f"{scenario.get('duration', 0):.1f}s"
            
            steps = scenario.get('steps', [])
            total_steps = len(steps)
            passed_steps = len([s for s in steps if s.get('status') == 'passed'])
            failed_steps = len([s for s in steps if s.get('status') == 'failed'])
            
            item_id = self.scenarios_tree.insert('', 'end', values=(
                name, status, duration, total_steps, passed_steps, failed_steps
            ))
            
            # Color coding
            if status == 'passed':
                self.scenarios_tree.item(item_id, tags=('passed',))
            else:
                self.scenarios_tree.item(item_id, tags=('failed',))
        
        # Configure tags
        self.scenarios_tree.tag_configure('passed', background='#e8f5e8')
        self.scenarios_tree.tag_configure('failed', background='#f8d7da')
    
    def _on_scenario_select(self, event):
        """Handle scenario selection in tree"""
        selected_items = self.scenarios_tree.selection()
        if selected_items and self.current_report:
            item = selected_items[0]
            index = self.scenarios_tree.index(item)
            
            scenarios = self.current_report['data'].get('scenarios', [])
            if 0 <= index < len(scenarios):
                scenario = scenarios[index]
                self._display_scenario_steps(scenario)
                
                # Check if scenario has associated video and update video player
                if hasattr(self, 'video_player') and scenario.get('video_path'):
                    self.video_player.set_video_path(scenario['video_path'])
    
    def _display_scenario_steps(self, scenario: Dict[str, Any]):
        """Display scenario step details"""
        steps_text = f"Scenario: {scenario.get('scenario_name', 'Unknown')}\n"
        steps_text += f"Status: {scenario.get('status', 'unknown')}\n"
        steps_text += f"Duration: {scenario.get('duration', 0):.1f}s\n"
        
        # Add video information if available
        if scenario.get('video_path'):
            video_name = os.path.basename(scenario['video_path'])
            steps_text += f"Video: {video_name} 🎥\n"
            steps_text += f"Video Path: {scenario['video_path']}\n"
        
        if scenario.get('error'):
            steps_text += f"Error: {scenario['error']}\n"
        
        steps_text += "\n" + "="*50 + "\nSTEPS:\n" + "="*50 + "\n\n"
        
        for step in scenario.get('steps', []):
            step_id = step.get('step_id', '?')
            step_name = step.get('step_name', 'Unknown Step')
            status = step.get('status', 'unknown')
            duration = step.get('duration', 0)
            action = step.get('action', 'N/A')
            target = step.get('target', 'N/A')
            value = step.get('value', 'N/A')
            
            status_symbol = "✓" if status == 'passed' else "✗"
            
            steps_text += f"Step {step_id}: {step_name}\n"
            steps_text += f"  Status: {status_symbol} {status.upper()}\n"
            steps_text += f"  Duration: {duration:.2f}s\n"
            steps_text += f"  Action: {action}\n"
            steps_text += f"  Target: {target}\n"
            steps_text += f"  Value: {value}\n"
            
            if step.get('error'):
                steps_text += f"  Error: {step['error']}\n"
            
            if step.get('screenshot_path'):
                steps_text += f"  Screenshot: {step['screenshot_path']}\n"
            
            steps_text += "\n"
        
        # Update steps text widget
        self.steps_text.config(state='normal')
        self.steps_text.delete(1.0, tk.END)
        self.steps_text.insert(1.0, steps_text)
        self.steps_text.config(state='disabled')
    
    def _display_raw_data(self, report_data: Dict[str, Any]):
        """Display raw JSON data"""
        try:
            raw_json = json.dumps(report_data, indent=2, ensure_ascii=False)
            
            self.raw_text.config(state='normal')
            self.raw_text.delete(1.0, tk.END)
            self.raw_text.insert(1.0, raw_json)
            self.raw_text.config(state='disabled')
            
        except Exception as e:
            self.logger.error(f"Failed to display raw data: {str(e)}")
    
    def _refresh_reports(self):
        """Refresh reports list"""
        self._load_reports()
    
    def _open_report_file(self):
        """Open report file dialog"""
        file_path = filedialog.askopenfilename(
            title="Open Report File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    report_data = json.load(file)
                
                # Create temporary report info
                temp_report = {
                    'filename': os.path.basename(file_path),
                    'filepath': file_path,
                    'data': report_data,
                    'created': datetime.fromtimestamp(os.path.getctime(file_path)),
                    'size': os.path.getsize(file_path)
                }
                
                self.current_report = temp_report
                self._display_report_details(temp_report)
                
            except Exception as e:
                messagebox.showerror("Open Error", f"Failed to open report: {str(e)}")
    
    def _delete_report(self):
        """Delete selected report"""
        if not self.current_report:
            messagebox.showinfo("No Selection", "Please select a report to delete")
            return
        
        result = messagebox.askyesno(
            "Delete Report",
            f"Are you sure you want to delete the report '{self.current_report['filename']}'?\n\n"
            "This action cannot be undone."
        )
        
        if result:
            try:
                os.remove(self.current_report['filepath'])
                self.logger.info(f"Deleted report: {self.current_report['filename']}")
                self._refresh_reports()
                messagebox.showinfo("Delete Complete", "Report deleted successfully")
                
            except Exception as e:
                messagebox.showerror("Delete Error", f"Failed to delete report: {str(e)}")
    
    def _export_report(self):
        """Export report to different location"""
        if not self.current_report:
            messagebox.showinfo("No Selection", "Please select a report to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Report",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                import shutil
                shutil.copy2(self.current_report['filepath'], file_path)
                messagebox.showinfo("Export Complete", f"Report exported to: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export report: {str(e)}")
    
    def refresh_reports(self):
        """Public method to refresh reports"""
        self._refresh_reports()
    
    def export_reports(self, directory: str):
        """Export all reports to specified directory"""
        try:
            import shutil
            exported_count = 0
            
            for report in self.reports:
                dest_path = os.path.join(directory, report['filename'])
                shutil.copy2(report['filepath'], dest_path)
                exported_count += 1
            
            self.logger.info(f"Exported {exported_count} reports to {directory}")
            
        except Exception as e:
            self.logger.error(f"Failed to export reports: {str(e)}")
            raise
