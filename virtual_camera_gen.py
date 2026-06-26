#!/usr/bin/env python3
"""
Virtual Camera Generator - For testing gesture recognition
Generates simulated hand movement video frames
"""
import cv2
import numpy as np
import time
import threading
import queue
from logger import logger

class VirtualCameraGenerator:
    def __init__(self, width=640, height=480, fps=30):
        self.width = width
        self.height = height
        self.fps = fps
        self.frame_queue = queue.Queue(maxsize=10)
        self.running = False
        self.thread = None
        self.frame_count = 0
        self.gesture_mode = "swipe"  # Options: swipe, circle, tap, fist
        
    def generate_hand_frame(self):
        """Generate virtual frame with hand"""
        frame = np.ones((self.height, self.width, 3), dtype=np.uint8) * 200
        
        # Calculate hand position - varies with time
        t = time.time()
        cycle = (t % 4) / 4  # 4-second cycle
        
        if self.gesture_mode == "swipe":
            # Left-right swipe gesture
            hand_x = int(100 + cycle * 400)
            hand_y = 240
            gesture_text = "SWIPE"
        elif self.gesture_mode == "circle":
            # Circular motion
            angle = cycle * 2 * np.pi
            hand_x = int(320 + 120 * np.cos(angle))
            hand_y = int(240 + 120 * np.sin(angle))
            gesture_text = "CIRCLE"
        elif self.gesture_mode == "tap":
            # Tap (up-down movement)
            hand_y = int(240 + (cycle * 2 - 1) * 80)
            hand_x = 320
            gesture_text = "TAP"
        else:  # fist
            # Fist (size change)
            size_factor = 0.5 + 0.5 * abs(np.sin(cycle * np.pi))
            hand_x = 320
            hand_y = 240
            gesture_text = "FIST"
            
            # Draw fist (scaled circle)
            radius = int(60 * size_factor)
            cv2.circle(frame, (hand_x, hand_y), radius, (50, 50, 200), -1)
            cv2.circle(frame, (hand_x, hand_y), radius, (0, 0, 0), 2)
            
            # Draw text information
            cv2.putText(frame, gesture_text, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2)
            cv2.putText(frame, f"Frame: {self.frame_count}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
            return frame
        
        if self.gesture_mode != "fist":
            # Draw hand (simple skin-colored circle + fingers)
            # Main hand position
            cv2.circle(frame, (hand_x, hand_y), 50, (150, 120, 80), -1)  # skin color
            cv2.circle(frame, (hand_x, hand_y), 50, (0, 0, 0), 2)
            
            # Draw fingers
            finger_offsets = [
                (-30, -50), (-10, -60), (10, -60), (30, -50),  # 4 fingers above
                (-40, 20)  # thumb
            ]
            for fx, fy in finger_offsets:
                cv2.circle(frame, (hand_x + fx, hand_y + fy), 15, (150, 120, 80), -1)
                cv2.circle(frame, (hand_x + fx, hand_y + fy), 15, (0, 0, 0), 1)
        
        # Draw text information
        cv2.putText(frame, gesture_text, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2)
        cv2.putText(frame, f"Frame: {self.frame_count}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        cv2.putText(frame, f"Gesture: {self.gesture_mode.upper()}", (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        
        return frame
    
    def _generation_loop(self):
        """Continuously generate frames"""
        while self.running:
            frame = self.generate_hand_frame()
            self.frame_count += 1
            
            try:
                self.frame_queue.put(frame, block=False)
            except queue.Full:
                # Discard oldest frame, add new frame
                try:
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    pass
                self.frame_queue.put(frame)
            
            time.sleep(1.0 / self.fps)
    
    def start(self, gesture_mode="swipe"):
        """Start virtual camera"""
        self.gesture_mode = gesture_mode
        self.running = True
        self.thread = threading.Thread(target=self._generation_loop, daemon=True)
        self.thread.start()
        logger.info(f"Virtual camera started - gesture mode: {gesture_mode}")
    
    def stop(self):
        """Stop virtual camera"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        logger.info("Virtual camera stopped")
    
    def read(self):
        """Similar to cv2.VideoCapture.read() interface"""
        try:
            frame = self.frame_queue.get(timeout=0.5)
            return True, frame
        except queue.Empty:
            return False, None
    
    def isOpened(self):
        """Check if running"""
        return self.running


if __name__ == "__main__":
    # Demo: generate virtual camera and display
    gen = VirtualCameraGenerator(width=640, height=480, fps=30)
    
    gestures = ["swipe", "circle", "tap", "fist"]
    gesture_idx = 0
    
    gen.start(gesture_mode=gestures[gesture_idx])
    
    try:
        frame_count = 0
        while True:
            ret, frame = gen.read()
            if ret:
                frame_count += 1
                if frame_count % 30 == 0:  # Print once per second
                    logger.info(f"Generated frame {gen.frame_count}, gesture: {gen.gesture_mode}")
            else:
                time.sleep(0.01)
                
            # Optional: display frames if display environment available
            if frame_count >= 60:
                break
                
    except KeyboardInterrupt:
        pass
    finally:
        gen.stop()
        logger.info("Demo completed")
