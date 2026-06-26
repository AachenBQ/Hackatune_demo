import argparse
import math
import queue
import threading
import time
import sys
import cv2
import numpy as np
import sounddevice as sd
import tkinter as tk
from PIL import Image, ImageTk
from logger import logger

# Try to import virtual camera generator if available
try:
    from virtual_camera_gen import VirtualCameraGenerator
    HAS_VIRTUAL_CAMERA = True
except ImportError:
    HAS_VIRTUAL_CAMERA = False

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def frequency_to_note_name(freq: float) -> str:
    if freq <= 0:
        return "?"
    midi = 69 + 12 * math.log2(freq / 440.0)
    midi_rounded = int(round(midi))
    return f"{NOTE_NAMES[midi_rounded % 12]}{midi_rounded // 12 - 1}"


def compute_spectrum(data: np.ndarray, sample_rate: int):
    window = np.hanning(len(data))
    spectrum = np.fft.rfft(data * window)
    freqs = np.fft.rfftfreq(len(data), d=1.0 / sample_rate)
    mags = np.abs(spectrum)
    return freqs, mags


class AudioVisualizer:
    def __init__(self, sample_rate=44100, block_size=4096, channels=1, use_virtual_camera=False, gesture_mode="swipe"):
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.channels = channels
        self.use_virtual_camera = use_virtual_camera
        self.gesture_mode = gesture_mode
        self.audio_queue = queue.Queue()
        self.frame_queue = queue.Queue(maxsize=2)
        self.running = True
        self.peak_freq = 0.0
        self.note = "?"
        self.current_frame = None
        self.gesture = "idle"
        self.emotion = "neutral"
        self.music_result = "standby"
        self.hand_trackers = {}
        self.last_freqs = np.array([])
        self.last_mags = np.array([])
        self.last_tap_time = 0.0
        self.last_loop_check = 0.0

        self.root = tk.Tk()
        self.root.title("Mic + Gesture Music Visualizer")
        self.root.geometry("1400x760")
        self.canvas = tk.Canvas(self.root, width=1400, height=760, bg="black")
        self.canvas.pack(fill="both", expand=True)
        self.root.protocol("WM_DELETE_WINDOW", self.stop)
        self.photo = None

        # Initialize camera - try real camera first, fall back to virtual if needed
        self.cap = None
        if use_virtual_camera and HAS_VIRTUAL_CAMERA:
            logger.info("Using virtual camera generator for testing")
            self.cap = VirtualCameraGenerator(width=640, height=480, fps=30)
            self.cap.start(gesture_mode=gesture_mode)
            self.camera_ready = True
        else:
            logger.info("Attempting to use real camera device")
            self.cap = cv2.VideoCapture(0)
            self.camera_ready = False

    def start(self):
        logger.info("Starting AudioVisualizer - audio threads")
        audio_thread = threading.Thread(target=self._audio_loop, daemon=True)
        audio_thread.start()
        camera_thread = threading.Thread(target=self._camera_loop, daemon=True)
        camera_thread.start()
        logger.info("GUI window initialized and rendering started")
        self.root.after(30, self._render_loop)
        self.root.mainloop()

    def stop(self):
        logger.info("Stopping AudioVisualizer application")
        self.running = False
        if self.cap is not None:
            if self.use_virtual_camera and HAS_VIRTUAL_CAMERA:
                self.cap.stop()
            else:
                self.cap.release()
        self.root.destroy()
        logger.info("AudioVisualizer stopped successfully")

    def _audio_loop(self):
        def callback(indata, frames, time_info, status):
            if status:
                logger.error(f"Audio callback status: {status}")
            mono = np.mean(indata, axis=1)
            freqs, mags = compute_spectrum(mono, self.sample_rate)
            mask = (freqs >= 80.0) & (freqs <= 2000.0)
            if not np.any(mask):
                return
            freqs = freqs[mask]
            mags = mags[mask]
            mag_max = np.max(mags) if np.max(mags) > 0 else 1.0
            mags = mags / mag_max
            peak_idx = int(np.argmax(mags))
            peak_freq = freqs[peak_idx]
            note = frequency_to_note_name(peak_freq)
            self.last_freqs = freqs
            self.last_mags = mags
            self.audio_queue.put((freqs, mags, peak_freq, note))

        with sd.InputStream(
            samplerate=self.sample_rate,
            blocksize=self.block_size,
            channels=self.channels,
            callback=callback,
        ):
            while self.running:
                time.sleep(0.05)

    def _camera_loop(self):
        while self.running:
            if self.cap is None:
                time.sleep(0.1)
                continue
                
            # Handle both real and virtual cameras
            if self.use_virtual_camera and HAS_VIRTUAL_CAMERA:
                is_open = self.cap.isOpened()
            else:
                is_open = self.cap.isOpened()
            
            if not is_open:
                time.sleep(0.1)
                continue
                
            ret, frame = self.cap.read()
            if not ret:
                self.camera_ready = False
                placeholder = np.zeros((360, 520, 3), dtype=np.uint8)
                cv2.putText(placeholder, "Camera unavailable", (20, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                try:
                    self.frame_queue.put_nowait((placeholder, "camera unavailable", "neutral", "standby"))
                except queue.Full:
                    pass
                time.sleep(0.1)
                continue

            self.camera_ready = True
            frame = cv2.flip(frame, 1)
            gesture, emotion, music = self._detect_gesture(frame)
            self.gesture = gesture
            self.emotion = emotion
            self.music_result = music

            overlay = frame.copy()
            cv2.putText(
                overlay,
                f"Gesture: {gesture}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2,
            )
            cv2.putText(
                overlay,
                f"Emotion: {emotion}",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 0),
                2,
            )
            cv2.putText(
                overlay,
                f"Music: {music}",
                (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 180, 80),
                2,
            )

            try:
                self.frame_queue.put_nowait((overlay, gesture, emotion, music))
            except queue.Full:
                pass

    def _render_loop(self):
        try:
            freqs, mags, peak_freq, note = self.audio_queue.get_nowait()
            self.peak_freq = peak_freq
            self.note = note
        except queue.Empty:
            pass

        try:
            frame, gesture, emotion, music = self.frame_queue.get_nowait()
            self.current_frame = frame
            self.gesture = gesture
            self.emotion = emotion
            self.music_result = music
        except queue.Empty:
            pass

        self._render_view()
        if self.running:
            self.root.after(30, self._render_loop)

    def _render_view(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, 1400, 760, fill="#0d1117", outline="")
        self.canvas.create_text(20, 20, text="Mic + Gesture Music Visualizer", anchor="nw", fill="white", font=("Consolas", 24, "bold"))
        self.canvas.create_text(20, 55, text=f"Peak: {self.peak_freq:6.1f} Hz   Note: {self.note}", anchor="nw", fill="#8ed0ff", font=("Consolas", 16))
        self.canvas.create_text(20, 80, text=f"Gesture: {self.gesture}   Emotion: {self.emotion}", anchor="nw", fill="#ffdf70", font=("Consolas", 16))
        self.canvas.create_text(20, 105, text=f"Music result: {self.music_result}", anchor="nw", fill="#90ee90", font=("Consolas", 16))

        if self.current_frame is not None:
            rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(rgb)
            image = image.resize((520, 360))
            self.photo = ImageTk.PhotoImage(image=image)
            self.canvas.create_image(20, 140, anchor="nw", image=self.photo)
            self.canvas.create_text(20, 510, text="Webcam: hand gestures -> emotion -> music action", anchor="nw", fill="#d0d7de", font=("Consolas", 14))

        self._draw_fft_panel()

    def _draw_fft_panel(self):
        left = 580
        top = 140
        width = 760
        height = 520
        self.canvas.create_rectangle(left, top, left + width, top + height, outline="#4b5563", width=2)
        self.canvas.create_text(left + 20, top + 20, text="Realtime FFT Spectrum (80Hz - 2kHz)", anchor="nw", fill="white", font=("Consolas", 18, "bold"))
        self.canvas.create_line(left + 20, top + 60, left + width - 20, top + 60, fill="#2f363d")

        try:
            freqs, mags, peak_freq, note = self.audio_queue.get_nowait()
            self.peak_freq = peak_freq
            self.note = note
        except queue.Empty:
            pass

        if self.peak_freq <= 0:
            self.canvas.create_text(left + 20, top + 90, text="Waiting for audio input...", anchor="nw", fill="#8b949e", font=("Consolas", 14))
            return

        self.canvas.create_text(left + 20, top + 90, text=f"Peak: {self.peak_freq:6.1f} Hz   Note: {self.note}", anchor="nw", fill="#8ed0ff", font=("Consolas", 14))

        if len(self.last_freqs) < 3 or len(self.last_mags) < 3:
            return

        mask = (self.last_freqs >= 80.0) & (self.last_freqs <= 2000.0)
        if not np.any(mask):
            return
        freqs = self.last_freqs[mask]
        mags = self.last_mags[mask]
        if len(freqs) < 3:
            return

        graph_left = left + 20
        graph_top = top + 120
        graph_right = left + width - 20
        graph_bottom = top + height - 20
        self.canvas.create_rectangle(graph_left, graph_top, graph_right, graph_bottom, outline="#444444", width=1)

        xs = np.linspace(0, len(freqs) - 1, graph_right - graph_left).astype(int)
        sampled = mags[xs]
        sampled = np.clip(sampled, 0.0, 1.0)
        for i, amp in enumerate(sampled):
            bar_height = amp * (graph_bottom - graph_top - 10)
            x0 = graph_left + i
            y0 = graph_bottom - bar_height
            x1 = graph_left + i + 1
            y1 = graph_bottom
            color = self._color_for_amp(amp)
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")

    def _detect_gesture(self, frame):
        if frame is None:
            return "idle", "neutral", "standby"

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower = np.array([0, 40, 80], dtype=np.uint8)
        upper = np.array([25, 255, 255], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower, upper)
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = [c for c in contours if cv2.contourArea(c) > 2000]
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        if len(contours) < 1:
            return "idle", "neutral", "standby"

        h, w = frame.shape[:2]
        hand_regions = []
        for contour in contours[:2]:
            x, y, ww, hh = cv2.boundingRect(contour)
            center = ((x + ww / 2.0) / w, (y + hh / 2.0) / h)
            hand_regions.append((center, x, y, ww, hh, contour))

        if len(hand_regions) >= 2:
            c1 = hand_regions[0][0]
            c2 = hand_regions[1][0]
            dist = math.hypot(c1[0] - c2[0], c1[1] - c2[1])
            if dist < 0.22:
                return "double close", "tense", "chords tighten"
            if dist > 0.42:
                return "double open", "relieved", "enter chorus / drop"

        center, x, y, ww, hh, contour = hand_regions[0]
        tracker = self.hand_trackers.get("main", {"center": center, "trajectory": []})
        prev_center = tracker["center"]
        dx = center[0] - prev_center[0]
        dy = center[1] - prev_center[1]
        tracker["center"] = center
        tracker["trajectory"].append(center)
        if len(tracker["trajectory"]) > 16:
            tracker["trajectory"].pop(0)
        self.hand_trackers["main"] = tracker

        hull = cv2.convexHull(contour, returnPoints=False)
        defects = []
        if len(hull) >= 3:
            defects = cv2.convexityDefects(contour, hull)
        finger_count = 1
        if defects is not None:
            finger_count += sum(1 for d in defects if d[0][3] > 10000)

        if finger_count <= 1:
            return "fist", "calm", "music stops"
        if finger_count >= 4 and dy < -0.06 and abs(dx) < 0.08:
            return "open up", "anticipation", "filter opens / volume rises"
        if abs(dx) > 0.12 and abs(dx) > 2.0 * abs(dy):
            if dx > 0:
                return "fast swipe", "excited", "drums get denser and brighter"
            return "fast swipe", "focused", "increase energy"
        if self._is_tap(tracker):
            return "tap", "playful", "add kick / snare"
        if self._is_circle(tracker):
            return "circle", "focused", "loop current pattern"
        return "idle", "neutral", "standby"

    def _is_tap(self, tracker):
        now = time.time()
        if now - self.last_tap_time < 0.6:
            return False
        if len(tracker["trajectory"]) < 3:
            return False
        displacement = 0.0
        for i in range(1, len(tracker["trajectory"])):
            prev = tracker["trajectory"][i - 1]
            curr = tracker["trajectory"][i]
            displacement += math.hypot(curr[0] - prev[0], curr[1] - prev[1])
        if displacement < 0.04:
            self.last_tap_time = now
            return True
        return False

    def _is_circle(self, tracker):
        points = tracker["trajectory"]
        if len(points) < 10:
            return False
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        area = 0.0
        for i in range(len(points) - 1):
            area += xs[i] * ys[i + 1] - xs[i + 1] * ys[i]
        area = abs(area) / 2.0
        return area > 0.06

    def _color_for_amp(self, amp: float):
        amp = max(0.0, min(1.0, amp))
        r = int(255 * amp)
        g = int(180 * amp)
        b = int(80 + 120 * amp)
        return f"#{r:02x}{g:02x}{b:02x}"


def main():
    parser = argparse.ArgumentParser(description="Mic + gesture music visualizer")
    parser.add_argument("--samplerate", type=int, default=44100)
    parser.add_argument("--blocksize", type=int, default=4096)
    parser.add_argument("--channels", type=int, default=1)
    parser.add_argument("--virtual-camera", action="store_true", help="Use virtual camera for testing (no hardware camera required)")
    parser.add_argument("--gesture", type=str, default="swipe", choices=["swipe", "circle", "tap", "fist"], help="Virtual camera gesture mode")
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Hackatune - Mic + Gesture Music Visualizer Starting")
    logger.info("=" * 60)
    logger.info(f"Config: sample_rate={args.samplerate}, block_size={args.blocksize}, channels={args.channels}")
    logger.info(f"Camera mode: {'virtual' if args.virtual_camera else 'real'}")
    if args.virtual_camera:
        logger.info(f"Virtual camera gesture mode: {args.gesture}")

    vis = AudioVisualizer(
        sample_rate=args.samplerate, 
        block_size=args.blocksize, 
        channels=args.channels,
        use_virtual_camera=args.virtual_camera,
        gesture_mode=args.gesture
    )
    try:
        vis.start()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user (Ctrl+C)")
        vis.stop()
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        vis.stop()
        raise
    finally:
        logger.info("=" * 60)
        logger.info("Application terminated")
        logger.info("=" * 60)


if __name__ == "__main__":
    main()
