from __future__ import annotations

import math

import numpy as np
from PIL import Image

from ..audio.sync import BeatTimeline
from ..utils.palette import amiga_fire_palette, amiga_ocean_palette
from .base import Effect


class MetaBalls(Effect):
    def __init__(
        self,
        width: int = 640,
        height: int = 512,
        fps: int = 60,
        ball_count: int = 6,
        speed: float = 60.0,
        threshold: float = 1.0,
        radius: float = 80.0,
        palette: str = "fire",
    ):
        super().__init__(width, height, fps)
        self.ball_count = ball_count
        self.speed = speed
        self.threshold = threshold
        self.radius = radius

        rng = np.random.RandomState(42)
        self.bx = rng.uniform(radius, width - radius, ball_count).astype(np.float32)
        self.by = rng.uniform(radius, height - radius, ball_count).astype(np.float32)
        angle = rng.uniform(0, 2 * math.pi, ball_count).astype(np.float32)
        vel = rng.uniform(30, 80, ball_count).astype(np.float32) * speed / 60.0
        self.vx = (np.cos(angle) * vel).astype(np.float32)
        self.vy = (np.sin(angle) * vel).astype(np.float32)

        if palette == "ocean":
            colors = amiga_ocean_palette(64)
        else:
            colors = amiga_fire_palette(64)
        self.palette_r = np.array([c[0] for c in colors], dtype=np.uint8)
        self.palette_g = np.array([c[1] for c in colors], dtype=np.uint8)
        self.palette_b = np.array([c[2] for c in colors], dtype=np.uint8)
        self.palette_size = len(colors)

        y, x = np.mgrid[0:height, 0:width].astype(np.float32)
        self.x_coords = x
        self.y_coords = y

    def render_frame(self, time_sec: float, beat_timeline: BeatTimeline) -> Image.Image:
        dt = 1.0 / self.fps
        beat_phase = beat_timeline.get_beat_phase(time_sec)

        pulse = 1.0 + 0.3 * math.sin(beat_phase * math.pi * 2)
        r_effective = self.radius * pulse

        self.bx += self.vx * dt * pulse
        self.by += self.vy * dt * pulse

        for i in range(self.ball_count):
            if self.bx[i] < r_effective:
                self.bx[i] = r_effective
                self.vx[i] = abs(self.vx[i])
            elif self.bx[i] > self.width - r_effective:
                self.bx[i] = self.width - r_effective
                self.vx[i] = -abs(self.vx[i])
            if self.by[i] < r_effective:
                self.by[i] = r_effective
                self.vy[i] = abs(self.vy[i])
            elif self.by[i] > self.height - r_effective:
                self.by[i] = self.height - r_effective
                self.vy[i] = -abs(self.vy[i])

        field = np.zeros((self.height, self.width), dtype=np.float32)
        r_sq = r_effective ** 2

        for i in range(self.ball_count):
            dx = self.x_coords - self.bx[i]
            dy = self.y_coords - self.by[i]
            dist_sq = dx * dx + dy * dy
            influence = np.clip(r_sq / (dist_sq + 1.0), 0, 1.0)
            field += influence

        field = np.clip(field / self.threshold, 0, 1)
        indices = (field * (self.palette_size - 1)).astype(np.uint16)

        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        frame[:, :, 0] = self.palette_r[indices]
        frame[:, :, 1] = self.palette_g[indices]
        frame[:, :, 2] = self.palette_b[indices]

        return self._to_image(frame)
