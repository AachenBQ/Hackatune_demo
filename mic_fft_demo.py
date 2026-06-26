import argparse
import math
import os
import sys
import numpy as np
import sounddevice as sd
from logger import logger

NOTE_NAMES = [
    "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"
]


def frequency_to_note_name(freq: float) -> str:
    if freq <= 0:
        return "?"
    midi = 69 + 12 * math.log2(freq / 440.0)
    midi_rounded = int(round(midi))
    note_name = NOTE_NAMES[midi_rounded % 12]
    octave = midi_rounded // 12 - 1
    return f"{note_name}{octave}"


def compute_spectrum(data: np.ndarray, sample_rate: int):
    window = np.hanning(len(data))
    spectrum = np.fft.rfft(data * window)
    freqs = np.fft.rfftfreq(len(data), d=1.0 / sample_rate)
    magnitudes = np.abs(spectrum)
    return freqs, magnitudes


def compute_peak_frequency(freqs: np.ndarray, magnitudes: np.ndarray, min_freq: float = 50.0) -> float:
    mask = (freqs >= min_freq) & (freqs <= 2000.0)
    if not np.any(mask):
        return 0.0
    peak_index = np.argmax(magnitudes[mask])
    return freqs[mask][peak_index]


def spectrum_to_waterfall_row(freqs: np.ndarray, magnitudes: np.ndarray, width: int = 80, min_freq: float = 50.0, max_freq: float = 2000.0) -> str:
    mask = (freqs >= min_freq) & (freqs <= max_freq)
    if not np.any(mask):
        return "-" * width

    freqs_masked = freqs[mask]
    mags_masked = magnitudes[mask]
    if len(freqs_masked) < 2:
        return "#" * width

    bins = np.interp(np.linspace(min_freq, max_freq, width), freqs_masked, mags_masked)
    bins = np.clip(bins, 1e-9, None)
    log_vals = np.log10(bins)
    log_vals = (log_vals - np.min(log_vals)) / (np.ptp(log_vals) + 1e-9)
    log_vals = np.clip(log_vals, 0.0, 1.0)

    chars = " .:-=+*#%@"
    row_chars = []
    for value in log_vals:
        idx = int(value * (len(chars) - 1))
        row_chars.append(chars[idx])
    return "".join(row_chars)


def render_waterfall(history, peak_freq: float, note: str, sample_rate: int, block_size: int, channels: int, frame_count: int) -> None:
    try:
        cols = os.get_terminal_size().columns
    except OSError:
        cols = 100
    width = max(40, min(100, cols - 20))
    header = f"Mic FFT waterfall | sr={sample_rate}Hz block={block_size} ch={channels} frame={frame_count}"
    info = f"Peak {peak_freq:6.1f} Hz | Note {note}"
    lines = [header, info]
    lines.extend(history[-20:])
    pad = max(0, 20 - len(lines))
    for _ in range(pad):
        lines.append(" " * width)

    sys.stdout.write("\033[2J\033[H")
    sys.stdout.write("\n".join(lines[:22]) + "\n")
    sys.stdout.flush()


def main(duration: float, sample_rate: int, block_size: int, channels: int) -> None:
    logger.info("=" * 60)
    logger.info("Mic FFT Waterfall Demo Starting")
    logger.info("=" * 60)
    logger.info(f"Configuration: sample_rate={sample_rate}Hz, block_size={block_size}, channels={channels}, duration={duration}s")
    print("Mic FFT waterfall demo starting...")
    print("Press Ctrl+C to stop.")
    print(f"Sample rate: {sample_rate} Hz, Block size: {block_size}, Channels: {channels}")

    history = []
    frame_count = 0
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    def callback(indata, frames, time, status):
        nonlocal frame_count
        if status:
            logger.warning(f"Audio input status: {status}")
        mono = np.mean(indata, axis=1)
        freqs, magnitudes = compute_spectrum(mono, sample_rate)
        peak_freq = compute_peak_frequency(freqs, magnitudes)
        note = frequency_to_note_name(peak_freq)
        row = spectrum_to_waterfall_row(freqs, magnitudes, width=80, min_freq=50.0, max_freq=sample_rate / 2)
        history.append(row)
        if len(history) > 24:
            history.pop(0)
        frame_count += 1
        render_waterfall(history, peak_freq, note, sample_rate, block_size, channels, frame_count)

    try:
        logger.info("Starting audio stream")
        with sd.InputStream(
            samplerate=sample_rate,
            blocksize=block_size,
            channels=channels,
            callback=callback,
        ):
            sd.sleep(int(duration * 1000))
        logger.info(f"Completed {frame_count} frames in {duration}s")
    except KeyboardInterrupt:
        logger.info("Stopped by user (Ctrl+C)")
        print("\nStopped by user.")
    except Exception as exc:
        logger.error(f"Error during execution: {exc}", exc_info=True)
        print(f"\nError: {exc}")
    finally:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
        logger.info("=" * 60)
        logger.info("Mic FFT Demo Closed")
        logger.info("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Microphone FFT waterfall demo")
    parser.add_argument("--duration", type=float, default=30.0, help="Recording duration in seconds")
    parser.add_argument("--samplerate", type=int, default=44100, help="Audio sample rate")
    parser.add_argument("--blocksize", type=int, default=4096, help="Input block size for FFT")
    parser.add_argument("--channels", type=int, default=1, help="Number of input channels")
    args = parser.parse_args()
    
    try:
        main(args.duration, args.samplerate, args.blocksize, args.channels)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
