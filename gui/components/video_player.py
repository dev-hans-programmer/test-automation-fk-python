"""
Video Player Component
GUI component for playing back test execution videos
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import subprocess
import platform
from typing import Dict, Any, Optional, List

from framework.utils.logger import Logger


class VideoPlayer:
    def __init__(self, parent: tk.Widget):
        """Initialize Video Player"""
        self.parent = parent
        self.logger = Logger()
        
        # Video data
        self.current_video_path = None
        self.available_videos = []
        
        # Create UI
        self._create_ui()
        self._load_videos()
    
    def _create_ui(self):
        """Create the video player interface"""
        # Main container
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(self.main_frame, text="Video Playback", font=('Arial', 14, 'bold'))
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Control frame
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(fill='x', pady=(0, 10))
        
        # Refresh button
        ttk.Button(control_frame, text="Refresh Videos", command=self._refresh_videos).pack(side='left', padx=(0, 5))
        
        # Open video folder button
        ttk.Button(control_frame, text="Open Video Folder", command=self._open_video_folder).pack(side='left', padx=(0, 5))
        
        # Clear old videos button
        ttk.Button(control_frame, text="Clear Old Videos", command=self._clear_old_videos).pack(side='left')
        
        # Videos list frame
        videos_frame = ttk.LabelFrame(self.main_frame, text="Available Videos", padding=10)
        videos_frame.pack(fill='both', expand=True)
        
        # Videos tree
        tree_frame = ttk.Frame(videos_frame)
        tree_frame.pack(fill='both', expand=True)
        
        columns = ('Session', 'Video Name', 'Size', 'Created', 'Duration')
        self.videos_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=10)
        
        # Configure columns
        self.videos_tree.heading('Session', text='Session')
        self.videos_tree.heading('Video Name', text='Video Name')
        self.videos_tree.heading('Size', text='Size (KB)')
        self.videos_tree.heading('Created', text='Created')
        self.videos_tree.heading('Duration', text='Duration')
        
        self.videos_tree.column('Session', width=150)
        self.videos_tree.column('Video Name', width=250)
        self.videos_tree.column('Size', width=80)
        self.videos_tree.column('Created', width=150)
        self.videos_tree.column('Duration', width=80)
        
        # Scrollbars for tree
        tree_v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.videos_tree.yview)
        tree_h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.videos_tree.xview)
        self.videos_tree.configure(yscrollcommand=tree_v_scrollbar.set, xscrollcommand=tree_h_scrollbar.set)
        
        # Pack tree and scrollbars
        self.videos_tree.pack(side='left', fill='both', expand=True)
        tree_v_scrollbar.pack(side='right', fill='y')
        tree_h_scrollbar.pack(side='bottom', fill='x')
        
        # Bind tree events
        self.videos_tree.bind('<Double-1>', self._on_video_double_click)
        self.videos_tree.bind('<<TreeviewSelect>>', self._on_video_select)
        
        # Video controls frame
        controls_frame = ttk.Frame(videos_frame)
        controls_frame.pack(fill='x', pady=(10, 0))
        
        # Play button
        self.play_button = ttk.Button(
            controls_frame, 
            text="▶ Play Video", 
            command=self._play_selected_video,
            state='disabled'
        )
        self.play_button.pack(side='left', padx=(0, 5))
        
        # Play with external player button
        self.external_play_button = ttk.Button(
            controls_frame, 
            text="🎬 Open with System Player", 
            command=self._play_with_external_player,
            state='disabled'
        )
        self.external_play_button.pack(side='left', padx=(0, 5))
        
        # Delete video button
        self.delete_button = ttk.Button(
            controls_frame, 
            text="🗑 Delete Video", 
            command=self._delete_selected_video,
            state='disabled'
        )
        self.delete_button.pack(side='left', padx=(0, 5))
        
        # Video info frame
        info_frame = ttk.LabelFrame(videos_frame, text="Video Information", padding=5)
        info_frame.pack(fill='x', pady=(10, 0))
        
        self.info_text = tk.Text(info_frame, height=4, wrap=tk.WORD, state='disabled')
        info_scrollbar = ttk.Scrollbar(info_frame, orient='vertical', command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=info_scrollbar.set)
        
        self.info_text.pack(side='left', fill='both', expand=True)
        info_scrollbar.pack(side='right', fill='y')
    
    def _load_videos(self):
        """Load available videos from the videos directory"""
        try:
            videos_dir = "./videos"
            if not os.path.exists(videos_dir):
                return
            
            self.available_videos = []
            
            # Scan all session directories
            for session_dir in os.listdir(videos_dir):
                session_path = os.path.join(videos_dir, session_dir)
                if os.path.isdir(session_path) and session_dir.startswith('session_'):
                    
                    # Get videos in this session
                    for filename in os.listdir(session_path):
                        if filename.endswith(('.avi', '.mp4', '.mov', '.mkv')):
                            filepath = os.path.join(session_path, filename)
                            stat = os.stat(filepath)
                            
                            video_info = {
                                'session': session_dir.replace('session_', ''),
                                'filename': filename,
                                'filepath': filepath,
                                'size_kb': round(stat.st_size / 1024, 1),
                                'created': stat.st_ctime,
                                'created_str': self._format_timestamp(stat.st_ctime)
                            }
                            
                            self.available_videos.append(video_info)
            
            # Sort by creation time (newest first)
            self.available_videos.sort(key=lambda x: x['created'], reverse=True)
            
            self._populate_videos_tree()
            
        except Exception as e:
            self.logger.error(f"Failed to load videos: {str(e)}")
    
    def _populate_videos_tree(self):
        """Populate videos tree with data"""
        # Clear existing items
        for item in self.videos_tree.get_children():
            self.videos_tree.delete(item)
        
        # Add videos to tree
        for video in self.available_videos:
            # Estimate duration (placeholder - would need video analysis for real duration)
            duration = "~5-30s"
            
            # Clean up filename for display
            display_name = video['filename'].replace('_compressed', '').replace('.mp4', '').replace('.avi', '')
            
            self.videos_tree.insert('', 'end', values=(
                video['session'],
                display_name,
                video['size_kb'],
                video['created_str'],
                duration
            ))
    
    def _format_timestamp(self, timestamp: float) -> str:
        """Format timestamp for display"""
        import datetime
        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M")
    
    def _on_video_select(self, event):
        """Handle video selection"""
        selected_items = self.videos_tree.selection()
        if selected_items:
            item = selected_items[0]
            index = self.videos_tree.index(item)
            
            if index < len(self.available_videos):
                video = self.available_videos[index]
                self.current_video_path = video['filepath']
                
                # Enable buttons
                self.play_button.config(state='normal')
                self.external_play_button.config(state='normal')
                self.delete_button.config(state='normal')
                
                # Update info panel
                self._update_video_info(video)
        else:
            self.current_video_path = None
            self.play_button.config(state='disabled')
            self.external_play_button.config(state='disabled')
            self.delete_button.config(state='disabled')
            self._clear_video_info()
    
    def _on_video_double_click(self, event):
        """Handle double-click on video (play with external player)"""
        self._play_with_external_player()
    
    def _update_video_info(self, video: Dict[str, Any]):
        """Update video information panel"""
        self.info_text.config(state='normal')
        self.info_text.delete('1.0', tk.END)
        
        info_text = f"""File: {video['filename']}
Path: {video['filepath']}
Size: {video['size_kb']} KB
Created: {video['created_str']}
Session: {video['session']}

Double-click to play with system default player."""
        
        self.info_text.insert('1.0', info_text)
        self.info_text.config(state='disabled')
    
    def _clear_video_info(self):
        """Clear video information panel"""
        self.info_text.config(state='normal')
        self.info_text.delete('1.0', tk.END)
        self.info_text.config(state='disabled')
    
    def _play_selected_video(self):
        """Play selected video in embedded player (basic implementation)"""
        if not self.current_video_path:
            messagebox.showwarning("No Video", "Please select a video to play")
            return
        
        if not os.path.exists(self.current_video_path):
            messagebox.showerror("File Not Found", "Video file not found")
            return
        
        # For now, use external player (embedded player would require additional libraries)
        self._play_with_external_player()
    
    def _play_with_external_player(self):
        """Play video with system default player"""
        if not self.current_video_path:
            messagebox.showwarning("No Video", "Please select a video to play")
            return
        
        if not os.path.exists(self.current_video_path):
            messagebox.showerror("File Not Found", "Video file not found")
            return
        
        try:
            # Open with system default player
            if platform.system() == 'Windows':
                os.startfile(self.current_video_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', self.current_video_path])
            else:  # Linux and others
                subprocess.run(['xdg-open', self.current_video_path])
            
            self.logger.info(f"Opened video with system player: {self.current_video_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to open video: {str(e)}")
            messagebox.showerror("Playback Error", f"Failed to open video:\n{str(e)}")
    
    def _delete_selected_video(self):
        """Delete selected video file"""
        if not self.current_video_path:
            messagebox.showwarning("No Video", "Please select a video to delete")
            return
        
        # Confirm deletion
        result = messagebox.askyesno(
            "Confirm Delete", 
            f"Are you sure you want to delete this video?\n\n{os.path.basename(self.current_video_path)}"
        )
        
        if result:
            try:
                os.remove(self.current_video_path)
                self.logger.info(f"Deleted video: {self.current_video_path}")
                messagebox.showinfo("Success", "Video deleted successfully")
                
                # Refresh the list
                self._refresh_videos()
                
            except Exception as e:
                self.logger.error(f"Failed to delete video: {str(e)}")
                messagebox.showerror("Delete Error", f"Failed to delete video:\n{str(e)}")
    
    def _refresh_videos(self):
        """Refresh video list"""
        self._load_videos()
        self.current_video_path = None
        self.play_button.config(state='disabled')
        self.external_play_button.config(state='disabled')
        self.delete_button.config(state='disabled')
        self._clear_video_info()
    
    def _open_video_folder(self):
        """Open videos folder in file explorer"""
        try:
            videos_dir = os.path.abspath("./videos")
            
            if platform.system() == 'Windows':
                os.startfile(videos_dir)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', videos_dir])
            else:  # Linux and others
                subprocess.run(['xdg-open', videos_dir])
            
            self.logger.info(f"Opened videos folder: {videos_dir}")
            
        except Exception as e:
            self.logger.error(f"Failed to open videos folder: {str(e)}")
            messagebox.showerror("Error", f"Failed to open videos folder:\n{str(e)}")
    
    def _clear_old_videos(self):
        """Clear old video files"""
        result = messagebox.askyesno(
            "Clear Old Videos", 
            "This will delete video files older than 7 days.\nAre you sure?"
        )
        
        if result:
            try:
                from framework.reporting.video_recorder import VideoRecorder
                config = {'reporting': {'video_directory': './videos'}}
                recorder = VideoRecorder(config)
                recorder.cleanup_old_videos(7)
                
                messagebox.showinfo("Success", "Old videos cleared successfully")
                self._refresh_videos()
                
            except Exception as e:
                self.logger.error(f"Failed to clear old videos: {str(e)}")
                messagebox.showerror("Error", f"Failed to clear old videos:\n{str(e)}")
    
    def set_video_path(self, video_path: str):
        """Set specific video path for playback"""
        if os.path.exists(video_path):
            self.current_video_path = video_path
            self.play_button.config(state='normal')
            self.external_play_button.config(state='normal')
            self.delete_button.config(state='normal')
            
            # Find and select this video in the tree
            for i, video in enumerate(self.available_videos):
                if video['filepath'] == video_path:
                    item = self.videos_tree.get_children()[i]
                    self.videos_tree.selection_set(item)
                    self.videos_tree.focus(item)
                    self._update_video_info(video)
                    break