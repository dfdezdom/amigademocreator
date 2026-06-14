from __future__ import annotations

import math

import numpy as np
from PIL import Image

from ..audio.sync import BeatTimeline
from ..utils.palette import quantize_to_amiga
from .base import Effect


class SpectrumAnalyzer(Effect):
    def __init__(
        self,
        width: int = 640,
        height: int = 512,
        fps: int = 60,
        band_count: int = 16,
        bar_width: int = 30,
        color: tuple[int, int, int] = (0, 200, 255),
        falloff: float = 0.3,
        audio_analysis: object | None = None,
    ):
        super().__init__(width, height, fps)
        self.band_count = band_count
        self.bar_width = bar_width
        self.base_color = np.array(color, dtype=np.float32)
        self.falloff = falloff
        self.audio_analysis = audio_analysis
        self._heights = np.zeros(band_count, dtype=np.float32)

        total_bars_width = band_count * (bar_width + 4)
        self.start_x = (width - total_bars_width) // 2

    def render_frame(self, time_sec: float, beat_timeline: BeatTimeline) -> Image.Image:
        frame = self._new_frame()
        beat_phase = beat_timeline.get_beat_phase(time_sec)

        if self.audio_analysis is not None and hasattr(self.audio_analysis, 'get_spectrum_at'):
            bands = self.audio_analysis.get_spectrum_at(time_sec, self.band_count)
        else:
            bands = np.random.uniform(0.1, 1.0, self.band_count).astype(np.float32)
            bands *= 0.5 + 0.5 * np.sin(time_sec * 3 + np.arange(self.band_count) * 0.5)

        beat_mod = 1.0 + 0.5 * math.sin(beat_phase * math.pi)
        bands = np.minimum(bands * beat_mod, 1.0)

        self._heights = self._heights * self.falloff + bands * (1.0 - self.falloff)

        for i in range(self.band_count):
            bar_h = int(self._heights[i] * self.height * 0.8)
            if bar_h < 1:
                continue
            x = self.start_x + i * (self.bar_width + 4)
            if x + self.bar_width > self.width:
                break

            brightness = 0.6 + 0.4 * self._heights[i]
            r = int(self.base_color[0] * brightness)
            g = int(self.base_color[1] * brightness)
            b = int(self.base_color[2] * brightness)
            color = (min(r, 255), min(g, 255), min(b, 255))

            y_start = self.height - bar_h
            frame[y_start:, x:x + self.bar_width, 0] = color[0]
            frame[y_start:, x:x + self.bar_width, 1] = color[1]
            frame[y_start:, x:x + self.bar_width, 2] = color[2]

        if self.amiga_palette:
            frame = quantize_to_amiga(frame)
        return self._to_image(frame)
