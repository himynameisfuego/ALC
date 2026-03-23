"""Core signal-processing routines for Adaptive Loudness Compensation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray
from scipy.io import wavfile
from scipy.signal import lfilter


Array1D = NDArray[np.float64]

_ISO_226_FREQUENCIES = np.array(
    [
        20,
        25,
        31.5,
        40,
        50,
        63,
        80,
        100,
        125,
        160,
        200,
        250,
        315,
        400,
        500,
        630,
        800,
        1000,
        1250,
        1600,
        2000,
        2500,
        3150,
        4000,
        5000,
        6300,
        8000,
        10000,
        12500,
    ],
    dtype=np.float64,
)

_ISO_226_AF = np.array(
    [
        0.532,
        0.506,
        0.480,
        0.455,
        0.432,
        0.409,
        0.387,
        0.367,
        0.349,
        0.330,
        0.315,
        0.301,
        0.288,
        0.276,
        0.267,
        0.259,
        0.253,
        0.250,
        0.246,
        0.244,
        0.243,
        0.243,
        0.243,
        0.242,
        0.242,
        0.245,
        0.254,
        0.271,
        0.301,
    ],
    dtype=np.float64,
)

_ISO_226_LU = np.array(
    [
        -31.6,
        -27.2,
        -23.0,
        -19.1,
        -15.9,
        -13.0,
        -10.3,
        -8.1,
        -6.2,
        -4.5,
        -3.1,
        -2.0,
        -1.1,
        -0.4,
        0.0,
        0.3,
        0.5,
        0.0,
        -2.7,
        -4.1,
        -1.0,
        1.7,
        2.5,
        1.2,
        -2.1,
        -7.1,
        -11.2,
        -10.7,
        -3.1,
    ],
    dtype=np.float64,
)

_ISO_226_TF = np.array(
    [
        78.5,
        68.7,
        59.5,
        51.1,
        44.0,
        37.5,
        31.5,
        26.5,
        22.1,
        17.9,
        14.4,
        11.4,
        8.6,
        6.2,
        4.4,
        3.0,
        2.2,
        2.4,
        3.5,
        1.7,
        -1.3,
        -4.2,
        -6.0,
        -5.4,
        -1.5,
        6.0,
        12.6,
        13.9,
        12.3,
    ],
    dtype=np.float64,
)


@dataclass(frozen=True)
class AdaptiveLoudnessResult:
    """Container for the loudness compensation output."""

    sample_rate: int
    compensated: Array1D
    attenuated: Array1D


def equal_loudness_contour(phon: float | Array1D) -> tuple[NDArray[np.float64], Array1D]:
    """Return ISO 226:2003 equal-loudness contours for one or more phon values."""

    phon_values = np.atleast_1d(np.asarray(phon, dtype=np.float64))
    if np.any((phon_values < 0) | (phon_values > 90)):
        raise ValueError("phon must be within the inclusive range [0, 90].")

    af_term = 4.47e-3 * (10 ** (0.025 * phon_values[:, None]) - 1.15)
    threshold_term = (0.4 * 10 ** (((_ISO_226_TF + _ISO_226_LU) / 10) - 9)) ** _ISO_226_AF
    acoustic_field = af_term + threshold_term
    spl = ((10 / _ISO_226_AF) * np.log10(acoustic_field)) - _ISO_226_LU + 94
    return spl, _ISO_226_FREQUENCIES.copy()


def trace_loudness(mastering_level: float, listening_level: float = 30) -> tuple[Array1D, Array1D]:
    """Return the compensation trace derived from the equal-loudness contours."""

    if not 20 <= mastering_level <= 90:
        raise ValueError("mastering_level must be within the inclusive range [20, 90] phon.")
    if not 20 <= listening_level <= 90:
        raise ValueError("listening_level must be within the inclusive range [20, 90] phon.")

    phon_grid = np.arange(20, 91, 10, dtype=np.float64)
    spl, frequencies = equal_loudness_contour(phon_grid)

    master_curve = np.array(
        [np.interp(mastering_level, phon_grid, spl[:, index]) for index in range(spl.shape[1])],
        dtype=np.float64,
    )
    listen_curve = np.array(
        [np.interp(listening_level, phon_grid, spl[:, index]) for index in range(spl.shape[1])],
        dtype=np.float64,
    )

    difference_curve = master_curve - listen_curve - mastering_level + listening_level
    return -difference_curve, frequencies


def shelf1low(gain: float, normalized_angular_frequency: float) -> tuple[Array1D, Array1D]:
    """Return first-order low-shelf filter coefficients."""

    if gain <= 0:
        raise ValueError("gain must be strictly positive.")

    tangent = np.tan(normalized_angular_frequency / 2)
    root_gain = np.sqrt(gain)

    a0 = tangent + root_gain
    a1 = tangent - root_gain
    b0 = gain * tangent + root_gain
    b1 = gain * tangent - root_gain

    denominator = np.array([a0, a1], dtype=np.float64)
    numerator = np.array([b0, b1], dtype=np.float64)
    return numerator, denominator


def overlap_add(frames: NDArray[np.float64], hop_size: int) -> Array1D:
    """Reconstruct a 1-D signal from overlapped frames using count normalization."""

    if frames.ndim != 2:
        raise ValueError("frames must be a 2-D array with shape (frame_size, n_frames).")
    if hop_size <= 0:
        raise ValueError("hop_size must be strictly positive.")

    frame_size, frame_count = frames.shape
    signal_length = (frame_count - 1) * hop_size + frame_size

    output = np.zeros(signal_length, dtype=np.float64)
    counts = np.zeros(signal_length, dtype=np.float64)

    for index in range(frame_count):
        start = index * hop_size
        stop = start + frame_size
        output[start:stop] += frames[:, index]
        counts[start:stop] += 1.0

    if np.any(counts == 0):
        raise RuntimeError("internal overlap-add normalization failure.")

    return output / counts


def read_audio_mono(file_path: str | Path) -> tuple[int, Array1D]:
    """Read an audio file and return a mono float64 waveform."""

    sample_rate, audio = wavfile.read(str(file_path))
    audio_array = np.asarray(audio)

    if np.issubdtype(audio_array.dtype, np.integer):
        max_magnitude = float(max(abs(np.iinfo(audio_array.dtype).min), np.iinfo(audio_array.dtype).max))
        normalized = audio_array.astype(np.float64) / max_magnitude
    elif np.issubdtype(audio_array.dtype, np.floating):
        normalized = audio_array.astype(np.float64)
    else:
        raise TypeError(f"Unsupported audio dtype: {audio_array.dtype}")

    if normalized.ndim == 1:
        mono = normalized
    elif normalized.ndim == 2:
        mono = normalized.mean(axis=1)
    else:
        raise ValueError(f"Unsupported audio shape: {normalized.shape}")

    return int(sample_rate), mono


def _frame_signal(signal: Array1D, frame_size: int, hop_size: int) -> NDArray[np.float64]:
    """Split a signal into zero-padded overlapping frames."""

    if frame_size <= 0:
        raise ValueError("frame_size must be strictly positive.")
    if hop_size <= 0:
        raise ValueError("hop_size must be strictly positive.")

    signal_array = np.asarray(signal, dtype=np.float64).reshape(-1)
    if signal_array.size == 0:
        raise ValueError("signal must not be empty.")

    frame_count = int(np.ceil(max(signal_array.size - frame_size, 0) / hop_size)) + 1
    padded_length = (frame_count - 1) * hop_size + frame_size

    padded_signal = np.zeros(padded_length, dtype=np.float64)
    padded_signal[: signal_array.size] = signal_array

    frames = np.zeros((frame_size, frame_count), dtype=np.float64)
    for index in range(frame_count):
        start = index * hop_size
        stop = start + frame_size
        frames[:, index] = padded_signal[start:stop]

    return frames


def adaptive_loudness_compensation(
    file_path: str | Path,
    mastering_level: float,
    listening_level: float,
    *,
    frame_size: int = 4096,
    hop_size: int = 2048,
    shelf_crossover_hz: float = 122.0552,
    gain_adjustment_db: float = 0.4851,
) -> AdaptiveLoudnessResult:
    """Apply the MATLAB adaptive loudness compensation workflow to an audio file."""

    sample_rate, audio = read_audio_mono(file_path)
    compensation_trace, _ = trace_loudness(mastering_level, listening_level)

    gain = 10 ** ((compensation_trace[0] + gain_adjustment_db) / 20)
    angular_frequency = 2 * np.pi * shelf_crossover_hz / sample_rate
    numerator, denominator = shelf1low(gain, angular_frequency)

    attenuation = 10 ** ((listening_level - mastering_level) / 20)
    attenuated = attenuation * audio

    frames = _frame_signal(attenuated, frame_size=frame_size, hop_size=hop_size)
    filtered_frames = np.zeros_like(frames)

    for index in range(frames.shape[1]):
        filtered_frames[:, index] = lfilter(numerator, denominator, frames[:, index])

    compensated = overlap_add(filtered_frames, hop_size=hop_size)[: attenuated.size]
    return AdaptiveLoudnessResult(
        sample_rate=sample_rate,
        compensated=compensated,
        attenuated=attenuated,
    )
