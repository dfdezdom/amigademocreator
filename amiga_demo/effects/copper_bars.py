from __future__ import annotations

import math

import numpy as np
from PIL import Image

from ..audio.sync import BeatTimeline
from ..utils.palette import quantize_to_amiga
from .base import Effect


class CopperBars(Effect):
    def __init__(
        self,
        width: int = 640,
        height: int = 512,
        fps: int = 60,
        bar_count: int = 32,
        color_cycle_speed: float = 1.0,
    ):
        super().__init__(width, height, fps)
        self.bar_count = bar_count
        self.color_cycle_speed = color_cycle_speed
        self.bar_height = max(1, height // bar_count)

    def render_frame(self, time_sec: float, beat_timeline: BeatTimeline) -> Image.Image:
        frame = self._new_frame()
        beat_phase = beat_timeline.get_beat_phase(time_sec)

        for i in range(self.bar_count):
            y_start = i * self.bar_height
            y_end = min(self.height, y_start + self.bar_height)
            if y_start >= self.height:
                break

            phase = (i / self.bar_count) * 2 * math.pi + time_sec * self.color_cycle_speed * 2
            r = int(128 + 127 * math.sin(phase))
            g = int(128 + 127 * math.sin(phase + 2.094))
            b = int(128 + 127 * math.sin(phase + 4.189))

            # modulate height by beat for pulsing effect
            pulse = 1.0 + 0.3 * math.sin(time_sec * 4 + i * 0.5)
            current_h = min(self.bar_height, max(1, int(self.bar_height * pulse)))
            y_end = min(self.height, y_start + current_h)

            bar_h = y_end - y_start
            if bar_h > 0:
                ys = np.arange(bar_h)
                brightness = 1.0 - (ys / current_h) * 0.3
                b2d = brightness[:, np.newaxis]
                frame[y_start:y_end, :, 0] = (r * b2d).astype(np.uint8)
                frame[y_start:y_end, :, 1] = (g * b2d).astype(np.uint8)
                frame[y_start:y_end, :, 2] = (b * b2d).astype(np.uint8)

        if self.amiga_palette:
            frame = quantize_to_amiga(frame)
        return self._to_image(frame)
