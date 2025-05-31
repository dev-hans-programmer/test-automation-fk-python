#!/usr/bin/env python3
"""
Simple test script to verify video recording functionality
"""

import json
import time
from framework.reporting.video_recorder import VideoRecorder

def test_video_recording():
    """Test basic video recording functionality"""
    
    # Load configuration
    with open('config/master_config.json', 'r') as f:
        config = json.load(f)
    
    # Initialize video recorder
    video_recorder = VideoRecorder(config)
    
    print("Testing video recording...")
    
    # Check if video recording is available
    status = video_recorder.get_recording_status()
    print(f"Video recording available: {status}")
    
    # Test short recording
    print("Starting 5-second test recording...")
    recording_started = video_recorder.start_recording("test_scenario")
    
    if recording_started:
        print("Recording started successfully!")
        
        # Record for 5 seconds
        time.sleep(5)
        
        # Stop recording
        video_path = video_recorder.stop_recording()
        
        if video_path:
            print(f"Recording completed successfully!")
            print(f"Video saved to: {video_path}")
        else:
            print("Failed to save recording")
    else:
        print("Failed to start recording")
        print("This might be due to missing video recording dependencies.")
        print("Video recording requires opencv-python, ffmpeg-python, and PIL.")

if __name__ == "__main__":
    test_video_recording()