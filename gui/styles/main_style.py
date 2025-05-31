"""
Style Manager
Manages GUI styling and themes for the Test Automation Framework
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any


class StyleManager:
    def __init__(self):
        """Initialize Style Manager"""
        self.style = ttk.Style()
        self.theme_name = "clam"  # Default theme
        
        # Define color scheme
        self.colors = {
            'primary': '#2563eb',      # Blue
            'primary_dark': '#1d4ed8',
            'primary_light': '#3b82f6',
            'secondary': '#64748b',    # Slate
            'secondary_dark': '#475569',
            'secondary_light': '#94a3b8',
            'success': '#059669',      # Green
            'success_light': '#d1fae5',
            'warning': '#d97706',      # Orange
            'warning_light': '#fef3c7',
            'error': '#dc2626',        # Red
            'error_light': '#fee2e2',
            'background': '#f8fafc',   # Light gray
            'surface': '#ffffff',      # White
            'surface_dark': '#f1f5f9',
            'text': '#1e293b',         # Dark gray
            'text_light': '#64748b',
            'border': '#e2e8f0',       # Light border
            'border_dark': '#cbd5e1'
        }
        
        # Define fonts
        self.fonts = {
            'default': ('Segoe UI', 9),
            'heading': ('Segoe UI', 12, 'bold'),
            'subheading': ('Segoe UI', 10, 'bold'),
            'monospace': ('Consolas', 9),
            'small': ('Segoe UI', 8),
            'large': ('Segoe UI', 11)
        }
    
    def apply_styles(self):
        """Apply custom styles to the application"""
        # Set the theme
        self.style.theme_use(self.theme_name)
        
        # Configure general styles
        self._configure_general_styles()
        
        # Configure button styles
        self._configure_button_styles()
        
        # Configure frame styles
        self._configure_frame_styles()
        
        # Configure notebook styles
        self._configure_notebook_styles()
        
        # Configure treeview styles
        self._configure_treeview_styles()
        
        # Configure entry styles
        self._configure_entry_styles()
        
        # Configure progress bar styles
        self._configure_progressbar_styles()
        
        # Configure label styles
        self._configure_label_styles()
    
    def _configure_general_styles(self):
        """Configure general application styles"""
        # Configure default font
        self.style.configure('.', font=self.fonts['default'])
        
        # Configure background colors
        self.style.configure('TFrame', background=self.colors['background'])
        self.style.configure('TLabelFrame', background=self.colors['background'])
        self.style.configure('TLabelFrame.Label', background=self.colors['background'])
    
    def _configure_button_styles(self):
        """Configure button styles"""
        # Default button
        self.style.configure(
            'TButton',
            padding=(10, 6),
            font=self.fonts['default'],
            focuscolor='none'
        )
        
        # Accent button (primary action)
        self.style.configure(
            'Accent.TButton',
            background=self.colors['primary'],
            foreground='white',
            padding=(12, 8),
            font=self.fonts['default']
        )
        
        self.style.map(
            'Accent.TButton',
            background=[
                ('active', self.colors['primary_light']),
                ('pressed', self.colors['primary_dark'])
            ]
        )
        
        # Success button
        self.style.configure(
            'Success.TButton',
            background=self.colors['success'],
            foreground='white',
            padding=(10, 6)
        )
        
        # Warning button
        self.style.configure(
            'Warning.TButton',
            background=self.colors['warning'],
            foreground='white',
            padding=(10, 6)
        )
        
        # Error button
        self.style.configure(
            'Error.TButton',
            background=self.colors['error'],
            foreground='white',
            padding=(10, 6)
        )
        
        # Small button
        self.style.configure(
            'Small.TButton',
            padding=(6, 4),
            font=self.fonts['small']
        )
        
        # Large button
        self.style.configure(
            'Large.TButton',
            padding=(15, 10),
            font=self.fonts['large']
        )
    
    def _configure_frame_styles(self):
        """Configure frame styles"""
        # Card frame (elevated appearance)
        self.style.configure(
            'Card.TFrame',
            background=self.colors['surface'],
            relief='solid',
            borderwidth=1
        )
        
        # Header frame
        self.style.configure(
            'Header.TFrame',
            background=self.colors['primary'],
            relief='flat'
        )
        
        # Sidebar frame
        self.style.configure(
            'Sidebar.TFrame',
            background=self.colors['surface_dark'],
            relief='solid',
            borderwidth=1
        )
        
        # Status frame
        self.style.configure(
            'Status.TFrame',
            background=self.colors['surface_dark'],
            relief='sunken',
            borderwidth=1
        )
    
    def _configure_notebook_styles(self):
        """Configure notebook (tab) styles"""
        # Main notebook
        self.style.configure(
            'TNotebook',
            background=self.colors['background'],
            tabmargins=[2, 5, 2, 0]
        )
        
        self.style.configure(
            'TNotebook.Tab',
            background=self.colors['surface_dark'],
            foreground=self.colors['text'],
            padding=[15, 8],
            font=self.fonts['default']
        )
        
        self.style.map(
            'TNotebook.Tab',
            background=[
                ('selected', self.colors['surface']),
                ('active', self.colors['primary_light'])
            ],
            foreground=[
                ('selected', self.colors['text']),
                ('active', 'white')
            ]
        )
    
    def _configure_treeview_styles(self):
        """Configure treeview styles"""
        # Main treeview
        self.style.configure(
            'Treeview',
            background=self.colors['surface'],
            foreground=self.colors['text'],
            fieldbackground=self.colors['surface'],
            font=self.fonts['default'],
            rowheight=25
        )
        
        # Treeview headings
        self.style.configure(
            'Treeview.Heading',
            background=self.colors['surface_dark'],
            foreground=self.colors['text'],
            font=self.fonts['subheading'],
            relief='flat',
            borderwidth=1
        )
        
        self.style.map(
            'Treeview.Heading',
            background=[('active', self.colors['primary_light'])],
            foreground=[('active', 'white')]
        )
        
        # Selected items
        self.style.map(
            'Treeview',
            background=[('selected', self.colors['primary'])],
            foreground=[('selected', 'white')]
        )
    
    def _configure_entry_styles(self):
        """Configure entry widget styles"""
        # Default entry
        self.style.configure(
            'TEntry',
            padding=(8, 6),
            font=self.fonts['default'],
            fieldbackground=self.colors['surface']
        )
        
        # Search entry
        self.style.configure(
            'Search.TEntry',
            padding=(10, 8),
            font=self.fonts['default']
        )
        
        # Error entry
        self.style.configure(
            'Error.TEntry',
            fieldbackground=self.colors['error_light'],
            bordercolor=self.colors['error']
        )
        
        # Combobox
        self.style.configure(
            'TCombobox',
            padding=(8, 6),
            font=self.fonts['default'],
            fieldbackground=self.colors['surface']
        )
    
    def _configure_progressbar_styles(self):
        """Configure progress bar styles"""
        # Default progress bar
        self.style.configure(
            'TProgressbar',
            background=self.colors['primary'],
            troughcolor=self.colors['surface_dark'],
            borderwidth=0,
            lightcolor=self.colors['primary_light'],
            darkcolor=self.colors['primary_dark']
        )
        
        # Success progress bar
        self.style.configure(
            'Success.TProgressbar',
            background=self.colors['success'],
            troughcolor=self.colors['success_light']
        )
        
        # Warning progress bar
        self.style.configure(
            'Warning.TProgressbar',
            background=self.colors['warning'],
            troughcolor=self.colors['warning_light']
        )
        
        # Error progress bar
        self.style.configure(
            'Error.TProgressbar',
            background=self.colors['error'],
            troughcolor=self.colors['error_light']
        )
    
    def _configure_label_styles(self):
        """Configure label styles"""
        # Default label
        self.style.configure(
            'TLabel',
            background=self.colors['background'],
            foreground=self.colors['text'],
            font=self.fonts['default']
        )
        
        # Heading labels
        self.style.configure(
            'Heading.TLabel',
            font=self.fonts['heading'],
            foreground=self.colors['text']
        )
        
        # Subheading labels
        self.style.configure(
            'Subheading.TLabel',
            font=self.fonts['subheading'],
            foreground=self.colors['text']
        )
        
        # Success label
        self.style.configure(
            'Success.TLabel',
            foreground=self.colors['success'],
            font=self.fonts['subheading']
        )
        
        # Warning label
        self.style.configure(
            'Warning.TLabel',
            foreground=self.colors['warning'],
            font=self.fonts['subheading']
        )
        
        # Error label
        self.style.configure(
            'Error.TLabel',
            foreground=self.colors['error'],
            font=self.fonts['subheading']
        )
        
        # Info label
        self.style.configure(
            'Info.TLabel',
            foreground=self.colors['primary'],
            font=self.fonts['default']
        )
        
        # Secondary label
        self.style.configure(
            'Secondary.TLabel',
            foreground=self.colors['text_light'],
            font=self.fonts['default']
        )
        
        # Small label
        self.style.configure(
            'Small.TLabel',
            font=self.fonts['small'],
            foreground=self.colors['text_light']
        )
        
        # Monospace label (for code/data)
        self.style.configure(
            'Monospace.TLabel',
            font=self.fonts['monospace'],
            foreground=self.colors['text']
        )
    
    def set_theme(self, theme_name: str):
        """Set the application theme"""
        try:
            available_themes = self.style.theme_names()
            if theme_name in available_themes:
                self.theme_name = theme_name
                self.style.theme_use(theme_name)
                self.apply_styles()  # Reapply custom styles
            else:
                raise ValueError(f"Theme '{theme_name}' is not available")
        except Exception as e:
            print(f"Failed to set theme: {str(e)}")
    
    def get_available_themes(self) -> list:
        """Get list of available themes"""
        return list(self.style.theme_names())
    
    def get_current_theme(self) -> str:
        """Get current theme name"""
        return self.theme_name
    
    def get_color(self, color_name: str) -> str:
        """Get color value by name"""
        return self.colors.get(color_name, '#000000')
    
    def get_font(self, font_name: str) -> tuple:
        """Get font by name"""
        return self.fonts.get(font_name, self.fonts['default'])
    
    def configure_widget_style(self, widget_type: str, style_name: str, **options):
        """Configure custom widget style"""
        self.style.configure(f'{style_name}.{widget_type}', **options)
    
    def apply_dark_theme(self):
        """Apply dark theme colors"""
        # Update colors for dark theme
        dark_colors = {
            'primary': '#3b82f6',
            'primary_dark': '#2563eb',
            'primary_light': '#60a5fa',
            'secondary': '#64748b',
            'secondary_dark': '#475569',
            'secondary_light': '#94a3b8',
            'success': '#10b981',
            'success_light': '#064e3b',
            'warning': '#f59e0b',
            'warning_light': '#78350f',
            'error': '#ef4444',
            'error_light': '#7f1d1d',
            'background': '#0f172a',    # Dark blue-gray
            'surface': '#1e293b',       # Slightly lighter
            'surface_dark': '#334155',
            'text': '#f1f5f9',          # Light text
            'text_light': '#94a3b8',
            'border': '#475569',
            'border_dark': '#334155'
        }
        
        self.colors.update(dark_colors)
        self.apply_styles()
    
    def apply_light_theme(self):
        """Apply light theme colors (default)"""
        # Reset to original light colors
        light_colors = {
            'primary': '#2563eb',
            'primary_dark': '#1d4ed8',
            'primary_light': '#3b82f6',
            'secondary': '#64748b',
            'secondary_dark': '#475569',
            'secondary_light': '#94a3b8',
            'success': '#059669',
            'success_light': '#d1fae5',
            'warning': '#d97706',
            'warning_light': '#fef3c7',
            'error': '#dc2626',
            'error_light': '#fee2e2',
            'background': '#f8fafc',
            'surface': '#ffffff',
            'surface_dark': '#f1f5f9',
            'text': '#1e293b',
            'text_light': '#64748b',
            'border': '#e2e8f0',
            'border_dark': '#cbd5e1'
        }
        
        self.colors.update(light_colors)
        self.apply_styles()
    
    def create_status_styles(self):
        """Create status-specific styles for various states"""
        # Running status
        self.style.configure(
            'Running.TLabel',
            foreground=self.colors['primary'],
            font=self.fonts['subheading']
        )
        
        # Completed status
        self.style.configure(
            'Completed.TLabel',
            foreground=self.colors['success'],
            font=self.fonts['subheading']
        )
        
        # Failed status
        self.style.configure(
            'Failed.TLabel',
            foreground=self.colors['error'],
            font=self.fonts['subheading']
        )
        
        # Stopped status
        self.style.configure(
            'Stopped.TLabel',
            foreground=self.colors['warning'],
            font=self.fonts['subheading']
        )
        
        # Ready status
        self.style.configure(
            'Ready.TLabel',
            foreground=self.colors['text'],
            font=self.fonts['subheading']
        )
    
    def configure_tooltip_style(self):
        """Configure tooltip styles"""
        # Note: This would require a custom tooltip implementation
        # as tkinter doesn't have built-in tooltip styling
        pass
    
    def get_style_config(self) -> Dict[str, Any]:
        """Get current style configuration"""
        return {
            'theme': self.theme_name,
            'colors': self.colors.copy(),
            'fonts': self.fonts.copy()
        }
    
    def apply_custom_config(self, config: Dict[str, Any]):
        """Apply custom style configuration"""
        if 'theme' in config:
            self.theme_name = config['theme']
        
        if 'colors' in config:
            self.colors.update(config['colors'])
        
        if 'fonts' in config:
            self.fonts.update(config['fonts'])
        
        self.apply_styles()


# Convenience functions for common styling operations
def create_styled_frame(parent, style_name: str = None) -> ttk.Frame:
    """Create a styled frame"""
    if style_name:
        return ttk.Frame(parent, style=f'{style_name}.TFrame')
    return ttk.Frame(parent)


def create_styled_button(parent, text: str, style_name: str = None, **kwargs) -> ttk.Button:
    """Create a styled button"""
    if style_name:
        return ttk.Button(parent, text=text, style=f'{style_name}.TButton', **kwargs)
    return ttk.Button(parent, text=text, **kwargs)


def create_styled_label(parent, text: str, style_name: str = None, **kwargs) -> ttk.Label:
    """Create a styled label"""
    if style_name:
        return ttk.Label(parent, text=text, style=f'{style_name}.TLabel', **kwargs)
    return ttk.Label(parent, text=text, **kwargs)


def create_styled_entry(parent, style_name: str = None, **kwargs) -> ttk.Entry:
    """Create a styled entry"""
    if style_name:
        return ttk.Entry(parent, style=f'{style_name}.TEntry', **kwargs)
    return ttk.Entry(parent, **kwargs)
