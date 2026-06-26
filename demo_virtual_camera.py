#!/usr/bin/env python3
"""
Quick demo script - Shows system functionality
"""
import sys
sys.path.insert(0, '/home/bowen/Hackatune')

from virtual_camera_gen import VirtualCameraGenerator
from logger import logger
import time

def demo_virtual_camera():
    """Demo various gestures with virtual camera"""
    print("=" * 60)
    print("Virtual Camera Demo System")
    print("=" * 60)
    logger.info("Starting virtual camera demo")
    print()
    
    gestures = ["swipe", "circle", "tap", "fist"]
    
    for gesture in gestures:
        print(f"\nDemonstrating gesture: {gesture.upper()}")
        print("-" * 40)
        
        gen = VirtualCameraGenerator(width=640, height=480, fps=30)
        gen.start(gesture_mode=gesture)
        logger.info(f"Started demo for gesture: {gesture}")
        
        # Read 2 seconds of frames (60 frames @ 30fps)
        frame_count = 0
        for i in range(60):
            ret, frame = gen.read()
            if ret:
                frame_count += 1
            time.sleep(1/30)  # 30 FPS
        
        gen.stop()
        print(f"✓ Generated {frame_count} frames")
        logger.info(f"Demo completed for {gesture} - generated {frame_count} frames")
        time.sleep(0.5)
    
    print()
    print("=" * 60)
    print("Demo completed!")
    logger.info("Virtual camera demo completed")
    print()
    print("Now you can run the complete program:")
    print("  .venv/bin/python mic_fft_demo_gui.py --virtual-camera --gesture swipe")
    print()
    print("Or use the startup script:")
    print("  ./run_virtual_camera.sh")
    print("=" * 60)


if __name__ == "__main__":
    try:
        demo_virtual_camera()
    except KeyboardInterrupt:
        logger.warning("Demo interrupted by user")
        print("\nDemo interrupted")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
