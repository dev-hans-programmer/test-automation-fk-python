"""
Video Recorder
Manages video recording during test execution using screen capture
"""

import os
import time
import threading
from datetime import datetime
from typing import Optional, Tuple

try:
    import cv2
    import numpy as np
    from PIL import ImageGrab
    import ffmpeg
    VIDEO_RECORDING_AVAILABLE = True
except ImportError:
    VIDEO_RECORDING_AVAILABLE = False

from framework.utils.logger import Logger


class VideoRecorder:
    def __init__(self, config: dict):
        """Initialize Video Recorder"""
        self.config = config
        self.logger = Logger()
        self.video_dir = config.get('reporting', {}).get('video_directory', './videos')
        
        # Recording settings
        self.fps = config.get('video_config', {}).get('fps', 10)
        self.quality = config.get('video_config', {}).get('quality', 'medium')
        self.compression = config.get('video_config', {}).get('compression', True)
        
        # Recording state
        self.is_recording = False
        self.video_writer = None
        self.recording_thread = None
        self.current_video_path = None
        self.frame_queue = []
        self.screen_size = None
        
        # Create video directory
        os.makedirs(self.video_dir, exist_ok=True)
        
        # Create session directory
        self.session_dir = self._create_session_directory()
        
    def _create_session_directory(self) -> str:
        """Create directory for current recording session"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = os.path.join(self.video_dir, f"session_{timestamp}")
        os.makedirs(session_dir, exist_ok=True)
        return session_dir
    
    def start_recording(self, scenario_name: str) -> bool:
        """Start video recording for a scenario"""
        try:
            if not VIDEO_RECORDING_AVAILABLE:
                self.logger.warning("Video recording not available - missing dependencies")
                return False
                
            if self.is_recording:
                self.logger.warning("Recording already in progress")
                return False
            
            # Generate video filename
            safe_scenario_name = self._sanitize_filename(scenario_name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_{timestamp}_{safe_scenario_name}.avi"
            self.current_video_path = os.path.join(self.session_dir, filename)
            
            # Get screen dimensions
            self.screen_size = self._get_screen_size()
            if not self.screen_size:
                self.logger.error("Failed to get screen size")
                return False
            
            # Setup video writer
            fourcc = cv2.VideoWriter_fourcc(*'XVID')  # type: ignore
            self.video_writer = cv2.VideoWriter(  # type: ignore
                self.current_video_path,
                fourcc,
                self.fps,
                self.screen_size
            )
            
            if not self.video_writer.isOpened():
                self.logger.error("Failed to initialize video writer")
                return False
            
            # Start recording thread
            self.is_recording = True
            self.recording_thread = threading.Thread(target=self._recording_loop)
            self.recording_thread.daemon = True
            self.recording_thread.start()
            
            self.logger.info(f"Started video recording: {self.current_video_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start video recording: {str(e)}")
            return False
    
    def stop_recording(self) -> Optional[str]:
        """Stop video recording and return video path"""
        try:
            if not self.is_recording:
                self.logger.warning("No recording in progress")
                return None
            
            # Stop recording
            self.is_recording = False
            
            # Wait for recording thread to finish
            if self.recording_thread and self.recording_thread.is_alive():
                self.recording_thread.join(timeout=5)
            
            # Release video writer
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None
            
            # Compress video if enabled
            if self.compression and self.current_video_path:
                compressed_path = self._compress_video(self.current_video_path)
                if compressed_path:
                    # Remove original file and use compressed version
                    os.remove(self.current_video_path)
                    self.current_video_path = compressed_path
            
            self.logger.info(f"Stopped video recording: {self.current_video_path}")
            return self.current_video_path
            
        except Exception as e:
            self.logger.error(f"Failed to stop video recording: {str(e)}")
            return None
    
    def _recording_loop(self):
        """Main recording loop that captures frames"""
        try:
            while self.is_recording:
                # Capture screen
                screenshot = ImageGrab.grab()
                
                # Convert to OpenCV format
                frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                
                # Resize if necessary
                if frame.shape[1] != self.screen_size[0] or frame.shape[0] != self.screen_size[1]:
                    frame = cv2.resize(frame, self.screen_size)
                
                # Write frame
                if self.video_writer:
                    self.video_writer.write(frame)
                
                # Control frame rate
                time.sleep(1.0 / self.fps)
                
        except Exception as e:
            self.logger.error(f"Error in recording loop: {str(e)}")
        finally:
            self.is_recording = False
    
    def _get_screen_size(self) -> Optional[Tuple[int, int]]:
        """Get screen size for video recording"""
        try:
            # Get screen dimensions using PIL
            screenshot = ImageGrab.grab()
            width, height = screenshot.size
            
            # Ensure dimensions are even numbers (required for some codecs)
            width = width if width % 2 == 0 else width - 1
            height = height if height % 2 == 0 else height - 1
            
            return (width, height)
            
        except Exception as e:
            self.logger.error(f"Failed to get screen size: {str(e)}")
            return None
    
    def _compress_video(self, input_path: str) -> Optional[str]:
        """Compress video using FFmpeg"""
        try:
            # Generate compressed filename
            base_name = os.path.splitext(input_path)[0]
            compressed_path = f"{base_name}_compressed.mp4"
            
            # Compression settings based on quality
            quality_settings = {
                'low': {'crf': 28, 'preset': 'fast'},
                'medium': {'crf': 23, 'preset': 'medium'},
                'high': {'crf': 18, 'preset': 'slow'}
            }
            
            settings = quality_settings.get(self.quality, quality_settings['medium'])
            
            # Compress using FFmpeg
            (
                ffmpeg
                .input(input_path)
                .output(
                    compressed_path,
                    vcodec='libx264',
                    crf=settings['crf'],
                    preset=settings['preset'],
                    movflags='faststart'
                )
                .overwrite_output()
                .run(quiet=True)
            )
            
            self.logger.info(f"Video compressed: {compressed_path}")
            return compressed_path
            
        except Exception as e:
            self.logger.error(f"Failed to compress video: {str(e)}")
            return None
    
    def capture_step_video_snippet(self, step_name: str, duration: int = 5) -> Optional[str]:
        """Capture a short video snippet for a specific step"""
        try:
            safe_step_name = self._sanitize_filename(step_name)
            timestamp = datetime.now().strftime("%H%M%S")
            filename = f"step_{timestamp}_{safe_step_name}.avi"
            video_path = os.path.join(self.session_dir, filename)
            
            # Get screen size
            screen_size = self._get_screen_size()
            if not screen_size:
                return None
            
            # Setup video writer
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            video_writer = cv2.VideoWriter(video_path, fourcc, self.fps, screen_size)
            
            if not video_writer.isOpened():
                self.logger.error("Failed to initialize step video writer")
                return None
            
            # Record for specified duration
            end_time = time.time() + duration
            while time.time() < end_time:
                screenshot = ImageGrab.grab()
                frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                
                if frame.shape[1] != screen_size[0] or frame.shape[0] != screen_size[1]:
                    frame = cv2.resize(frame, screen_size)
                
                video_writer.write(frame)
                time.sleep(1.0 / self.fps)
            
            video_writer.release()
            
            # Compress if enabled
            if self.compression:
                compressed_path = self._compress_video(video_path)
                if compressed_path:
                    os.remove(video_path)
                    video_path = compressed_path
            
            self.logger.info(f"Step video captured: {video_path}")
            return video_path
            
        except Exception as e:
            self.logger.error(f"Failed to capture step video: {str(e)}")
            return None
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize string for use as filename"""
        invalid_chars = '<>:"/\\|?*'
        sanitized = name
        
        for char in invalid_chars:
            sanitized = sanitized.replace(char, '_')
        
        sanitized = sanitized.replace(' ', '_')
        
        if len(sanitized) > 50:
            sanitized = sanitized[:50]
        
        return sanitized
    
    def get_recording_status(self) -> dict:
        """Get current recording status"""
        return {
            'is_recording': self.is_recording,
            'current_video_path': self.current_video_path,
            'session_dir': self.session_dir,
            'fps': self.fps,
            'quality': self.quality,
            'compression': self.compression
        }
    
    def cleanup_old_videos(self, days_old: int = 7):
        """Clean up videos older than specified days"""
        try:
            cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            deleted_count = 0
            
            for root, dirs, files in os.walk(self.video_dir):
                for file in files:
                    if file.endswith(('.avi', '.mp4', '.mov')):
                        filepath = os.path.join(root, file)
                        if os.path.getctime(filepath) < cutoff_time:
                            os.remove(filepath)
                            deleted_count += 1
            
            self.logger.info(f"Cleaned up {deleted_count} old videos")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old videos: {str(e)}")
    
    def get_session_videos(self) -> list:
        """Get list of videos from current session"""
        try:
            videos = []
            
            for filename in os.listdir(self.session_dir):
                if filename.endswith(('.avi', '.mp4', '.mov')):
                    filepath = os.path.join(self.session_dir, filename)
                    stat = os.stat(filepath)
                    videos.append({
                        'filename': filename,
                        'filepath': filepath,
                        'created': datetime.fromtimestamp(stat.st_ctime),
                        'size': stat.st_size
                    })
            
            videos.sort(key=lambda x: x['created'])
            return videos
            
        except Exception as e:
            self.logger.error(f"Failed to get session videos: {str(e)}")
            return []