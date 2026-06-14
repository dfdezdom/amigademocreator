from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .analyzer import AudioAnalysis


@dataclass
class BeatTimeline:
    bpm: float
    total_beats: int
    beat_times: np.ndarray
    duration_sec: float

    @classmethod
    def from_analysis(cls, analysis: AudioAnalysis) -> BeatTimeline:
        bpm = analysis.bpm
        duration = analysis.duration_sec
        interval = 60.0 / bpm if bpm > 0 else 0.5
        total = int(duration / interval) + 1
        times = np.arange(total, dtype=np.float64) * interval
        return cls(
            bpm=bpm,
            total_beats=total,
            beat_times=times,
            duration_sec=duration,
        )

    def get_beat_phase(self, time_sec: float) -> float:
        interval = 60.0 / self.bpm if self.bpm > 0 else 0.5
        if interval <= 0:
            return 0.0
        _, phase = np.modf(time_sec / interval)
        return float(phase)

    def get_beat_index(self, time_sec: float) -> int:
        interval = 60.0 / self.bpm if self.bpm > 0 else 0.5
        if interval <= 0:
            return 0
        return int(time_sec / interval)
