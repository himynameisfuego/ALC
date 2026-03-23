"""Audio I/O helpers for the Adaptive Loudness Compensation package."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from numpy.typing import NDArray
from scipy.io import wavfile


Array1D = NDArray[np.float64]


def write_audio(file_path: str | Path, sample_rate: int, signal: Array1D) -> None:
    """Write a mono float waveform to 16-bit PCM WAV."""

    if sample_rate <= 0:
        raise ValueError("sample_rate must be strictly positive.")

    waveform = np.asarray(signal, dtype=np.float64).reshape(-1)
    clipped = np.clip(waveform, -1.0, 1.0)
    pcm16 = np.round(clipped * np.iinfo(np.int16).max).astype(np.int16)
    wavfile.write(str(file_path), sample_rate, pcm16)
