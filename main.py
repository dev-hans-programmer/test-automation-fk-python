#!/usr/bin/env python3
"""
Main entry point for the Test Automation Framework
Launches the Tkinter GUI application
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add framework paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow
from framework.utils.logger import Logger

def main():
    """Main application entry point"""
    try:
        # Initialize logger
        logger = Logger()
        logger.info("Starting Test Automation Framework")
        
        # Create main application window
        root = tk.Tk()
        app = MainWindow(root)
        
        # Start GUI event loop
        root.mainloop()
        
    except Exception as e:
        error_msg = f"Failed to start application: {str(e)}"
        print(error_msg)
        messagebox.showerror("Startup Error", error_msg)
        sys.exit(1)

if __name__ == "__main__":
    main()
