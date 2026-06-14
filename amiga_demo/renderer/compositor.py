from __future__ import annotations

import math

import numpy as np
from PIL import Image


def crossfade(frame_a: Image.Image, frame_b: Image.Image, t: float) -> Image.Image:
    a = np.array(frame_a, dtype=np.float32)
    b = np.array(frame_b, dtype=np.float32)
    blended = a * (1.0 - t) + b * t
    return Image.fromarray(np.clip(blended, 0, 255).astype(np.uint8))


def fade_to_black(frame: Image.Image, t: float) -> Image.Image:
    arr = np.array(frame, dtype=np.float32)
    arr *= 1.0 - t
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def fade_from_black(frame: Image.Image, t: float) -> Image.Image:
    arr = np.array(frame, dtype=np.float32)
    arr *= t
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def add_scanlines(frame: Image.Image, intensity: float = 0.25) -> Image.Image:
    arr = np.array(frame, dtype=np.float32)
    arr[1::2] *= 1.0 - intensity
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
