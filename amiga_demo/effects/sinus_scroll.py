from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from ..audio.sync import BeatTimeline
from .base import Effect


class SinusScroll(Effect):
    def __init__(
        self,
        width: int = 640,
        height: int = 512,
        fps: int = 60,
        text: str = "Amiga Demo",
        font_size: int = 32,
        speed: float = 80.0,
        amplitude: int = 40,
        wave_count: int = 3,
        rainbow: bool = True,
    ):
        super().__init__(width, height, fps)
        self.text = text
        self.font_size = font_size
        self.speed = speed
        self.amplitude = amplitude
        self.wave_count = wave_count
        self.rainbow = rainbow

        self._cached_text_w = 0
        self._cached_text_h = 0
        self._cached_text_arr: np.ndarray | None = None

        try:
            self.font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except Exception:
            self.font = ImageFont.load_default()

        self._render_text()

    def set_text(self, text: str) -> None:
        self.text = text
        self._render_text()

    def _render_text(self) -> None:
        img = Image.new("RGB", (1, 1))
        draw = ImageDraw.Draw(img)
        bbox = draw.textbbox((0, 0), self.text, font=self.font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        if text_w < 1 or text_h < 1:
            self._cached_text_w = 0
            self._cached_text_h = 0
            self._cached_text_arr = np.zeros((1, 1, 3), dtype=np.uint8)
            return
        text_img = Image.new("RGB", (text_w, text_h), (0, 0, 0))
        text_draw = ImageDraw.Draw(text_img)
        text_draw.text((0, 0), self.text, font=self.font, fill=(255, 255, 255))
        self._cached_text_w = text_w
        self._cached_text_h = text_h
        self._cached_text_arr = np.array(text_img, dtype=np.uint8)

    def render_frame(self, time_sec: float, beat_timeline: BeatTimeline) -> Image.Image:
        frame = self._new_frame()
        text_w = self._cached_text_w
        text_h = self._cached_text_h
        if text_w < 1 or self._cached_text_arr is None:
            return self._to_image(frame)

        middle_y = self.height // 2
        total_width = text_w + self.width
        x_offset = int(time_sec * self.speed) % total_width
        x = self.width - x_offset

        beat_phase = beat_timeline.get_beat_phase(time_sec)
        beat_pulse = 0.7 + 0.3 * math.sin(beat_phase * math.pi)

        cols = np.arange(text_w, dtype=np.int32)
        sin_offsets = np.zeros(text_w, dtype=np.float64)
        for w in range(self.wave_count):
            freq = self.amplitude * (0.03 + w * 0.015)
            phase_shift = w * math.pi * 0.7 + time_sec * (1.0 + w * 0.3)
            sin_offsets += self.amplitude / self.wave_count * beat_pulse * np.sin((x + cols + time_sec * self.speed * 0.3) * freq + phase_shift)

        screen_y = (middle_y - text_h // 2 + sin_offsets).astype(np.int32)

        pulse = 0.7 + 0.3 * np.sin(time_sec * 4 + (x + cols) * 0.1)
        text_arr = self._cached_text_arr

        for i in range(text_w):
            sx = x + i
            if sx < 0 or sx >= self.width:
                continue
            sy = screen_y[i]
            if sy < 0 or sy + text_h >= self.height:
                continue

            if self.rainbow:
                hue = (time_sec * 2.0 + i * 0.05) % 1.0
                r = int(127 + 127 * math.sin(hue * 2 * math.pi))
                g = int(127 + 127 * math.sin(hue * 2 * math.pi + 2.094))
                b = int(127 + 127 * math.sin(hue * 2 * math.pi + 4.189))
            else:
                r, g, b = 255, 255, 255

            col = text_arr[:, i, :].astype(np.float64)
            col[:, 0] = col[:, 0] * pulse[i] * (r / 255.0)
            col[:, 1] = col[:, 1] * pulse[i] * (g / 255.0)
            col[:, 2] = col[:, 2] * pulse[i] * (b / 255.0)
            col = np.clip(col, 0, 255).astype(np.uint8)
            non_black = col[:, 0] > 10
            if non_black.any():
                frame[sy:sy + text_h, sx, :][non_black] = col[non_black]

        return self._to_image(frame)
