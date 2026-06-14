from __future__ import annotations

import math

import numpy as np
from PIL import Image

from ..audio.sync import BeatTimeline
from ..utils.palette import amiga_fire_palette, amiga_ocean_palette
from .base import Effect


class Plasma(Effect):
    def __init__(
        self,
        width: int = 640,
        height: int = 512,
        fps: int = 60,
        speed: float = 1.0,
        palette: str = "fire",
    ):
        super().__init__(width, height, fps)
        self.speed = speed
        self.palette_name = palette
        self._build_palette()

        y, x = np.mgrid[0:height, 0:width]
        self.x_norm = x / width * 2.0 * math.pi
        self.y_norm = y / height * 2.0 * math.pi

    def _build_palette(self) -> None:
        if self.palette_name == "ocean":
            colors = amiga_ocean_palette(64)
        else:
            colors = amiga_fire_palette(64)
        self.palette_r = np.array([c[0] for c in colors], dtype=np.uint8)
        self.palette_g = np.array([c[1] for c in colors], dtype=np.uint8)
        self.palette_b = np.array([c[2] for c in colors], dtype=np.uint8)
        self.palette_size = len(colors)

    def render_frame(self, time_sec: float, beat_timeline: BeatTimeline) -> Image.Image:
        t = time_sec * self.speed
        v1 = np.sin(self.x_norm * 0.5 + self.y_norm * 0.3 + t * 1.3)
        v2 = np.sin(self.x_norm * 0.8 - self.y_norm * 0.5 + t * 0.7 + 1.0)
        v3 = np.sin(self.x_norm * 1.2 + self.y_norm * 0.9 - t * 0.5 + math.sin(t * 0.3) * 2)
        v4 = np.sin((self.x_norm + self.y_norm) * 0.4 + t * 1.1)
        plasma = v1 + v2 + v3 + v4
        plasma = (plasma + 4) / 8.0
        plasma = np.clip(plasma, 0, 1)
        indices = (plasma * (self.palette_size - 1)).astype(np.uint16)

        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        frame[:, :, 0] = self.palette_r[indices]
        frame[:, :, 1] = self.palette_g[indices]
        frame[:, :, 2] = self.palette_b[indices]

        return self._to_image(frame)
