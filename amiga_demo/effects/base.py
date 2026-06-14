from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np
from PIL import Image

from ..audio.sync import BeatTimeline


class Effect(ABC):
    def __init__(self, width: int = 640, height: int = 512, fps: int = 60):
        self.width = width
        self.height = height
        self.fps = fps
        self.amiga_palette = True

    @abstractmethod
    def render_frame(self, time_sec: float, beat_timeline: BeatTimeline) -> Image.Image:
        ...

    def _new_frame(self) -> np.ndarray:
        return np.zeros((self.height, self.width, 3), dtype=np.uint8)

    def _to_image(self, array: np.ndarray) -> Image.Image:
        return Image.fromarray(np.clip(array, 0, 255).astype(np.uint8))
