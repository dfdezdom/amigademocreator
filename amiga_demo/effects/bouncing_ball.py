from __future__ import annotations

import math

import numpy as np
from PIL import Image

from ..audio.sync import BeatTimeline
from ..utils.palette import quantize_to_amiga
from .base import Effect


class BouncingBall(Effect):
    def __init__(
        self,
        width: int = 640,
        height: int = 512,
        fps: int = 60,
        ball_size: int = 60,
        rotation_speed: float = 1.0,
    ):
        super().__init__(width, height, fps)
        self.ball_size = ball_size
        self.rotation_speed = rotation_speed
        self._build_ball_texture()

    def _build_ball_texture(self) -> None:
        r = self.ball_size
        x = np.arange(-r, r + 1, dtype=np.float32)
        y = np.arange(-r, r + 1, dtype=np.float32)
        xx, yy = np.meshgrid(x, y)
        dist = np.sqrt(xx**2 + yy**2)

        self.ball_mask = dist <= r
        self.ball_tex = np.zeros((2 * r + 1, 2 * r + 1), dtype=np.float32)
        z = np.sqrt(np.clip(r**2 - dist**2, 0, None))
        nx = xx / r
        ny = yy / r
        nz = z / r

        angle = np.arctan2(ny, nx)
        self.ball_tex = (np.sin(angle * 4) + 1) / 2
        self.ball_tex *= (nz * 0.8 + 0.4)
        self.ball_tex[~self.ball_mask] = 0

    def render_frame(self, time_sec: float, beat_timeline: BeatTimeline) -> Image.Image:
        frame = self._new_frame()

        beat_phase = beat_timeline.get_beat_phase(time_sec)
        beat_idx = beat_timeline.get_beat_index(time_sec)

        px = int(self.width // 2 + math.sin(time_sec * 1.5) * self.width * 0.3)
        bounce = abs(math.sin(time_sec * math.pi * (0.5 + 0.2 * math.sin(beat_phase * math.pi))))
        py = int(self.height // 2 + (bounce - 0.5) * self.height * 0.35)

        r = self.ball_size
        x1 = max(0, px - r)
        x2 = min(self.width, px + r + 1)
        y1 = max(0, py - r)
        y2 = min(self.height, py + r + 1)

        bx1 = x1 - (px - r)
        bx2 = bx1 + (x2 - x1)
        by1 = y1 - (py - r)
        by2 = by1 + (y2 - y1)

        tex = self.ball_tex[by1:by2, bx1:bx2]
        mask = self.ball_mask[by1:by2, bx1:bx2]

        color_val = int(120 + 100 * (0.5 + 0.5 * math.sin(time_sec * 2)))
        color = (color_val, color_val // 3, color_val // 3)

        for c in range(3):
            frame[y1:y2, x1:x2, c] = np.where(
                mask & (tex > 0.05),
                (tex * color[c]).astype(np.uint8),
                frame[y1:y2, x1:x2, c],
            )

        if self.amiga_palette:
            frame = quantize_to_amiga(frame)
        return self._to_image(frame)
