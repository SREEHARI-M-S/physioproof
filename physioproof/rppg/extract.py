from __future__ import annotations

import numpy as np


def synthetic_pulse_signal(length: int, fps: float = 30.0, bpm: float = 72.0) -> np.ndarray:
    """Placeholder rPPG trace for demos until real ROI extraction is wired."""
    t = np.arange(length) / fps
    omega = 2.0 * np.pi * (bpm / 60.0)
    return np.sin(omega * t) + 0.05 * np.random.default_rng(0).standard_normal(length)


def estimate_dominant_bpm(signal: np.ndarray, fps: float = 30.0) -> float:
    """Estimate pulse rate from a 1-D rPPG-like trace via FFT peak in 40–180 BPM."""
    if signal.size < 8:
        return 0.0
    centered = signal - np.mean(signal)
    spectrum = np.abs(np.fft.rfft(centered))
    freqs = np.fft.rfftfreq(centered.size, d=1.0 / fps)
    mask = (freqs >= 40.0 / 60.0) & (freqs <= 180.0 / 60.0)
    if not np.any(mask):
        return 0.0
    idx = int(np.argmax(spectrum[mask]))
    peak_hz = freqs[mask][idx]
    return float(peak_hz * 60.0)
