from __future__ import annotations

import librosa
import numpy as np


class AudioAnalysis:
    def __init__(
        self,
        filepath: str,
        sr: int = 22050,
        onset_sensitivity: float = 0.5,
        n_fft: int = 2048,
        hop_length: int = 512,
    ):
        self.filepath = filepath
        self.sr: int = sr
        self.y: np.ndarray | None = None
        self.duration_sec: float = 0.0
        self.bpm: float = 0.0
        self.beat_times: np.ndarray | None = None
        self.beat_frames: np.ndarray | None = None
        self.onset_times: np.ndarray | None = None
        self.onset_strength: np.ndarray | None = None
        self.n_fft = n_fft
        self.hop_length = hop_length
        self._stft: np.ndarray | None = None
        self._freqs: np.ndarray | None = None
        self._times: np.ndarray | None = None

        self._analyze(onset_sensitivity)

    def _analyze(self, onset_sensitivity: float) -> None:
        self.y, self.sr = librosa.load(self.filepath, sr=self.sr, mono=True)
        self.duration_sec = librosa.get_duration(y=self.y, sr=self.sr)

        tempo, beat_frames = librosa.beat.beat_track(
            y=self.y, sr=self.sr, units="frames"
        )
        self.bpm = float(tempo)
        self.beat_frames = beat_frames
        self.beat_times = librosa.frames_to_time(beat_frames, sr=self.sr)

        onset_frames = librosa.onset.onset_detect(
            y=self.y,
            sr=self.sr,
            units="frames",
            backtrack=True,
            delta=onset_sensitivity,
        )
        self.onset_times = librosa.frames_to_time(onset_frames, sr=self.sr)

        self.onset_strength = librosa.onset.onset_strength(y=self.y, sr=self.sr)

        D = librosa.stft(y=self.y, n_fft=self.n_fft, hop_length=self.hop_length)
        self._stft = np.abs(D)
        self._freqs = librosa.fft_frequencies(sr=self.sr, n_fft=self.n_fft)
        self._times = librosa.frames_to_time(np.arange(self._stft.shape[1]), sr=self.sr, hop_length=self.hop_length)

    def get_spectrum_at(self, time_sec: float, n_bands: int = 16) -> np.ndarray:
        if self._stft is None:
            return np.zeros(n_bands, dtype=np.float32)
        t_idx = np.argmin(np.abs(self._times - time_sec))
        t_idx = min(t_idx, self._stft.shape[1] - 1)
        spec = self._stft[:, t_idx]
        band_size = len(spec) // n_bands
        bands = np.zeros(n_bands, dtype=np.float32)
        for i in range(n_bands):
            start = i * band_size
            end = len(spec) if i == n_bands - 1 else (i + 1) * band_size
            bands[i] = float(np.mean(spec[start:end]))
        max_val = bands.max()
        if max_val > 0:
            bands /= max_val
        return bands

    def beat_interval_sec(self) -> float:
        return 60.0 / self.bpm if self.bpm > 0 else 0.5

    def is_beat_near(self, time_sec: float, window: float = 0.05) -> bool:
        if self.beat_times is None or len(self.beat_times) == 0:
            return False
        return np.any(np.abs(self.beat_times - time_sec) < window)

    def onset_strength_at(self, time_sec: float) -> float:
        if self.onset_strength is None:
            return 0.0
        idx = int(time_sec * self.sr / 512)
        if idx >= len(self.onset_strength):
            return 0.0
        return float(self.onset_strength[idx])
