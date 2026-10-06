from __future__ import annotations

import numpy as np


def synthetic_pulse_signal(length: int, fps: float = 30.0, bpm: float = 72.0) -> np.ndarray:
    """Placeholder rPPG trace for demos until real ROI extraction is wired."""
    t = np.arange(length) / fps
    omega = 2.0 * np.pi * (bpm / 60.0)
    return np.sin(omega * t) + 0.05 * np.random.default_rng(0).standard_normal(length)
