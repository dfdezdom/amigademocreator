from __future__ import annotations

import math

import numpy as np
from PIL import Image

from ..audio.sync import BeatTimeline
from ..utils.palette import quantize_to_amiga
from .base import Effect


class DotField(Effect):
    def __init__(
        self,
        width: int = 640,
        height: int = 512,
        fps: int = 60,
        dot_count: int = 300,
        speed: float = 200.0,
        lifetime: float = 1.5,
        colors: tuple[int, int, int] = (255, 255, 255),
    ):
        super().__init__(width, height, fps)
        self.dot_count = dot_count
        self.speed = speed
        self.max_life = lifetime
        self.colors = np.array(colors, dtype=np.uint8)

        self.cx = width / 2.0
        self.cy = height / 2.0

        self.px = np.zeros(dot_count, dtype=np.float32)
        self.py = np.zeros(dot_count, dtype=np.float32)
        self.pz = np.ones(dot_count, dtype=np.float32)
        self.age = np.full(dot_count, lifetime, dtype=np.float32)
        self.vx = np.zeros(dot_count, dtype=np.float32)
        self.vy = np.zeros(dot_count, dtype=np.float32)
        self.vz = np.zeros(dot_count, dtype=np.float32)

        self._reset_dots(np.arange(dot_count), 0)

    def _reset_dots(self, indices: np.ndarray, seed: int) -> None:
        n = len(indices)
        rng = np.random.RandomState(seed)
        angle = rng.uniform(0, 2 * math.pi, n).astype(np.float32)
        phi = rng.uniform(-math.pi * 0.4, math.pi * 0.4, n).astype(np.float32)
        vel = rng.uniform(40, 120, n).astype(np.float32)

        self.vx[indices] = np.cos(phi) * np.cos(angle) * vel
        self.vy[indices] = np.cos(phi) * np.sin(angle) * vel
        self.vz[indices] = (np.sin(phi) * 0.3 + 1.0) * vel
        self.px[indices] = self.cx
        self.py[indices] = self.cy
        self.pz[indices] = 0.5
        self.age[indices] = 0

    def render_frame(self, time_sec: float, beat_timeline: BeatTimeline) -> Image.Image:
        frame = self._new_frame()
        dt = 1.0 / self.fps
        beat_phase = beat_timeline.get_beat_phase(time_sec)
        beat_idx = beat_timeline.get_beat_index(time_sec)

        speed_mod = self.speed / 60.0
        self.age += dt
        self.px += self.vx * dt * speed_mod
        self.py += self.vy * dt * speed_mod
        self.pz += self.vz * dt * speed_mod

        dead = self.age >= self.max_life
        dead_count = dead.sum()

        burst = beat_phase < 0.06
        if burst and dead_count > 0:
            n_reset = min(dead_count, self.dot_count // 4)
            dead_idx = np.where(dead)[0][:n_reset]
            self._reset_dots(dead_idx, int(time_sec * 10000) + beat_idx)

        inv_z = np.clip(1.0 / self.pz, 0.01, 3.0)
        fade = np.clip(1.0 - self.age / self.max_life, 0, 1)

        px_2d = (self.cx + (self.px - self.cx) * inv_z).astype(np.int32)
        py_2d = (self.cy + (self.py - self.cy) * inv_z).astype(np.int32)

        alive = self.age < self.max_life
        mask = alive & (px_2d >= 0) & (px_2d < self.width) & (py_2d >= 0) & (py_2d < self.height)
        px_m, py_m = px_2d[mask], py_2d[mask]
        fade_m = fade[mask]

        brightness = (fade_m * 255).astype(np.uint8)
        for c in range(3):
            val = ((self.colors[c].astype(np.uint16)) * brightness // 255).astype(np.uint8)
            existing = frame[py_m, px_m, c]
            frame[py_m, px_m, c] = np.where(val > existing, val, existing)

        if self.amiga_palette:
            frame = quantize_to_amiga(frame)
        return self._to_image(frame)
