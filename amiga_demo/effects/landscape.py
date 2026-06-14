from __future__ import annotations

import math

import numpy as np
from PIL import Image

from ..audio.sync import BeatTimeline
from ..utils.palette import amiga_fire_palette
from .base import Effect


class Landscape(Effect):
    def __init__(
        self,
        width: int = 640,
        height: int = 512,
        fps: int = 60,
        speed: float = 120.0,
        height_scale: float = 80.0,
        detail: float = 0.02,
        horizon: float = 0.4,
        palette: str = "fire",
    ):
        super().__init__(width, height, fps)
        self.speed = speed
        self.height_scale = height_scale
        self.horizon_y = int(height * horizon)
        self.sky_grad_size = self.horizon_y

        self.hm_size = 2048
        x_vals = np.arange(self.hm_size, dtype=np.float64) * detail
        self.heightmap = (
            np.sin(x_vals * 1.3) * 0.6 +
            np.sin(x_vals * 0.7 + 1.0) * 0.4 +
            np.sin(x_vals * 2.1 + 0.5) * 0.3 +
            np.sin(x_vals * 0.3 - 0.7) * 0.5 +
            np.sin(x_vals * 1.7 + 2.0) * 0.2
        ).astype(np.float64)
        self.heightmap = (self.heightmap - self.heightmap.min()) / (self.heightmap.max() - self.heightmap.min() + 1e-8)

        colors = amiga_fire_palette(64)
        self.palette_r = np.array([c[0] for c in colors], dtype=np.uint8)
        self.palette_g = np.array([c[1] for c in colors], dtype=np.uint8)
        self.palette_b = np.array([c[2] for c in colors], dtype=np.uint8)
        self.palette_size = len(colors)

    def render_frame(self, time_sec: float, beat_timeline: BeatTimeline) -> Image.Image:
        frame = self._new_frame()
        beat_phase = beat_timeline.get_beat_phase(time_sec)

        cam_x = (time_sec * self.speed) % self.hm_size
        hm_cols = ((cam_x + np.arange(self.width, dtype=np.float64) * 0.8) % self.hm_size).astype(np.int32)
        heights = self.heightmap[hm_cols] * self.height_scale
        ground_ys = (self.horizon_y + (1.0 - heights / self.height_scale) * (self.height - self.horizon_y)).astype(np.int32)
        ground_ys = np.clip(ground_ys, self.horizon_y, self.height - 1)

        for col in range(self.width):
            gy = ground_ys[col]
            if gy <= self.horizon_y:
                continue

            num_rows = gy - self.horizon_y
            t = np.linspace(0, 1, num_rows, dtype=np.float64)
            t = np.clip(t * 0.8, 0, 1)
            color_idx = (t * (self.palette_size - 1)).astype(np.int32)

            frame[self.horizon_y:gy, col, 0] = self.palette_r[color_idx]
            frame[self.horizon_y:gy, col, 1] = self.palette_g[color_idx]
            frame[self.horizon_y:gy, col, 2] = self.palette_b[color_idx]

        return self._to_image(frame)
