from __future__ import annotations

import math

import numpy as np


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def smoothstep(t: float) -> float:
    return t * t * (3.0 - 2.0 * t)


def sine_wave(time: float, frequency: float, amplitude: float = 1.0, phase: float = 0.0) -> float:
    return amplitude * math.sin(2.0 * math.pi * frequency * time + phase)


def cosine_wave(time: float, frequency: float, amplitude: float = 1.0, phase: float = 0.0) -> float:
    return amplitude * math.cos(2.0 * math.pi * frequency * time + phase)


def beat_phase(time: float, beat_interval: float) -> float:
    if beat_interval <= 0:
        return 0.0
    _, phase = math.modf(time / beat_interval)
    return phase


def beat_index(time: float, beat_interval: float) -> int:
    if beat_interval <= 0:
        return 0
    return int(time / beat_interval)


def generate_noise(width: int, height: int, seed: int = 0) -> np.ndarray:
    rng = np.random.RandomState(seed)
    return rng.rand(height, width).astype(np.float32)


def smooth_noise(width: int, height: int, scale: float = 4.0, seed: int = 0) -> np.ndarray:
    small_w = max(2, int(width / scale))
    small_h = max(2, int(height / scale))
    rng = np.random.RandomState(seed)
    small = rng.rand(small_h, small_w).astype(np.float32)
    from PIL import Image
    img = Image.fromarray((small * 255).astype(np.uint8), mode="L")
    large = img.resize((width, height), Image.BILINEAR)
    return np.array(large, dtype=np.float32) / 255.0
