from __future__ import annotations

import math

import numpy as np
from PIL import Image

from ..audio.sync import BeatTimeline
from ..utils.palette import quantize_to_amiga
from .base import Effect


class Tunnel(Effect):
    def __init__(
        self,
        width: int = 640,
        height: int = 512,
        fps: int = 60,
        speed: float = 1.0,
        rotation_speed: float = 0.5,
        texture: str = "checkerboard",
    ):
        super().__init__(width, height, fps)
        self.speed = speed
        self.rotation_speed = rotation_speed
        self.tex_size = 256
        self._build_texture(texture)

        cx, cy = width // 2, height // 2
        y_coords, x_coords = np.mgrid[0:height, 0:width]
        dx = x_coords - cx
        dy = y_coords - cy
        self.dist = np.sqrt(dx**2 + dy**2).astype(np.float32)
        self.angle = np.arctan2(dy, dx).astype(np.float32)
        self.max_dist = float(np.sqrt(cx**2 + cy**2))

    def _build_texture(self, texture: str) -> None:
        s = self.tex_size
        tex = np.zeros((s, s, 3), dtype=np.uint8)
        if texture == "checkerboard":
            for y in range(s):
                for x in range(s):
                    if (x // 16 + y // 16) % 2 == 0:
                        tex[y, x] = (180, 60, 180)
                    else:
                        tex[y, x] = (40, 20, 60)
        elif texture == "lines":
            for y in range(s):
                val = 80 + 80 * math.sin(y * 0.1)
                tex[y, :] = (int(val), int(val * 0.5), int(val * 0.8))
        else:
            for y in range(s):
                for x in range(s):
                    tex[y, x] = (x * 255 // s, y * 255 // s, (x + y) * 128 // s)
        self.texture = tex

    def render_frame(self, time_sec: float, beat_timeline: BeatTimeline) -> Image.Image:
        beat_phase = beat_timeline.get_beat_phase(time_sec)

        scroll = time_sec * self.speed * 60
        rot = time_sec * self.rotation_speed + beat_phase * math.pi * 0.3

        r_norm = self.dist / self.max_dist
        u = (r_norm * self.tex_size * 0.5 + scroll) % self.tex_size
        v = ((self.angle / (2 * math.pi) + 0.5) * self.tex_size + rot * self.tex_size / (2 * math.pi)) % self.tex_size

        u_i = np.clip(u.astype(np.int32), 0, self.tex_size - 1)
        v_i = np.clip(v.astype(np.int32), 0, self.tex_size - 1)

        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        frame[:, :, 0] = self.texture[v_i, u_i, 0]
        frame[:, :, 1] = self.texture[v_i, u_i, 1]
        frame[:, :, 2] = self.texture[v_i, u_i, 2]

        vignette = np.clip(1.0 - r_norm * 0.5, 0.3, 1.0)
        frame = (frame.astype(np.float32) * vignette[:, :, np.newaxis]).astype(np.uint8)

        if self.amiga_palette:
            frame = quantize_to_amiga(frame)
        return self._to_image(frame)
