from __future__ import annotations

import math

import numpy as np
from PIL import Image

from ..audio.sync import BeatTimeline
from ..utils.palette import quantize_to_amiga
from .base import Effect


class Rotozoom(Effect):
    def __init__(
        self,
        width: int = 640,
        height: int = 512,
        fps: int = 60,
        zoom_speed: float = 0.5,
        rotation_speed: float = 0.3,
    ):
        super().__init__(width, height, fps)
        self.zoom_speed = zoom_speed
        self.rotation_speed = rotation_speed
        self._build_checkerboard()

    def _build_checkerboard(self, size: int = 128, checks: int = 8) -> None:
        self.tex_size = size
        self.texture = np.zeros((size, size, 3), dtype=np.uint8)
        check_size = size // checks
        for y in range(size):
            for x in range(size):
                if (x // check_size + y // check_size) % 2 == 0:
                    self.texture[y, x] = (180, 60, 180)
                else:
                    self.texture[y, x] = (40, 20, 60)

    def render_frame(self, time_sec: float, beat_timeline: BeatTimeline) -> Image.Image:
        frame = self._new_frame()
        beat_phase = beat_timeline.get_beat_phase(time_sec)

        cx, cy = self.width // 2, self.height // 2
        angle = time_sec * self.rotation_speed
        zoom = 1.0 + 0.5 * math.sin(time_sec * self.zoom_speed + beat_phase * math.pi * 0.5)

        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        half_w = self.width * 0.5 * zoom
        half_h = self.height * 0.5 * zoom

        y_coords, x_coords = np.mgrid[0:self.height, 0:self.width]
        dx = x_coords - cx
        dy = y_coords - cy

        tx = (dx * cos_a - dy * sin_a) / half_w * self.tex_size * 0.5 + self.tex_size // 2
        ty = (dx * sin_a + dy * cos_a) / half_h * self.tex_size * 0.5 + self.tex_size // 2

        tx_i = np.clip(np.floor(tx).astype(int), 0, self.tex_size - 1)
        ty_i = np.clip(np.floor(ty).astype(int), 0, self.tex_size - 1)

        frame[:, :] = self.texture[ty_i, tx_i]

        if self.amiga_palette:
            frame = quantize_to_amiga(frame)
        return self._to_image(frame)
