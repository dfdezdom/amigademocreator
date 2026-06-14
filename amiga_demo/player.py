from __future__ import annotations

import os
import tempfile
import time

import librosa
import numpy as np
import pygame
from scipy.io import wavfile

from .audio.analyzer import AudioAnalysis
from .audio.sync import BeatTimeline
from .renderer.output import _render_single_frame
from .renderer.scene import DemoConfig, TEXT_EFFECT_REGISTRY


class LivePlayer:
    def __init__(self, config: DemoConfig):
        self.config = config
        self.amiga_w, self.amiga_h = 640, 512
        self.fps = config.fps

        print("Analyzing audio...")
        self.analysis = AudioAnalysis(config.audio)
        self.timeline = BeatTimeline.from_analysis(self.analysis)
        beat_times = self.timeline.beat_times
        self.beat_interval = beat_times[1] - beat_times[0] if len(beat_times) > 1 else 0.5
        self.total_sec = self.timeline.duration_sec
        if config.max_duration_sec is not None:
            self.total_sec = min(self.total_sec, config.max_duration_sec)

        self.effect_cache: dict = {}

        self.text_scrollers = {}
        for t in config.texts:
            start_sec = t.start_beat * self.beat_interval
            end_sec = (t.start_beat + t.duration_beats) * self.beat_interval
            effect_cls = TEXT_EFFECT_REGISTRY.get(t.effect)
            if effect_cls is not None:
                scroller = effect_cls(
                    width=self.amiga_w, height=self.amiga_h,
                    fps=self.fps, text=t.text,
                )
                self.text_scrollers[(start_sec, end_sec)] = scroller

        self.transition_state = {
            "active": False,
            "progress": 0.0,
            "duration_frames": 1,
            "prev_frame": None,
        }

        print("Loading audio for playback...")
        self._load_audio()

        pygame.init()
        pygame.display.set_caption("Amiga Demo Creator — Live Player")
        self.screen = pygame.display.set_mode((self.amiga_w, self.amiga_h))
        self.clock = pygame.time.Clock()

        self.paused = False
        self.running = True
        self.audio_offset = 0.0
        self.pause_offset = 0.0
        self.play_start_tick = 0

    def _load_audio(self):
        y, sr = librosa.load(self.config.audio, sr=None, mono=False)
        if y.ndim == 1:
            y = y[np.newaxis, :]
        y_int16 = (y * 32767).clip(-32768, 32767).astype(np.int16)
        self._temp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        self._temp_wav_path = self._temp_wav.name
        self._temp_wav.close()
        wavfile.write(self._temp_wav_path, sr, y_int16.T)
        pygame.mixer.init(frequency=sr)
        pygame.mixer.music.load(self._temp_wav_path)

    def _cleanup(self):
        pygame.mixer.music.stop()
        pygame.quit()
        if hasattr(self, '_temp_wav_path') and os.path.exists(self._temp_wav_path):
            try:
                os.unlink(self._temp_wav_path)
            except OSError:
                pass

    def _get_audio_time(self) -> float:
        if self.paused:
            return self.pause_offset
        if not pygame.mixer.music.get_busy():
            return self.total_sec
        elapsed = (pygame.time.get_ticks() - self.play_start_tick) / 1000.0
        return self.audio_offset + elapsed

    def _start_playback(self):
        pygame.mixer.music.play()
        self.play_start_tick = pygame.time.get_ticks()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self._toggle_pause()
                elif event.key == pygame.K_r:
                    self._restart()
                elif event.key == pygame.K_LEFT:
                    self._seek(-5)
                elif event.key == pygame.K_RIGHT:
                    self._seek(5)

    def _toggle_pause(self):
        if self.paused:
            self.paused = False
            self.audio_offset = self.pause_offset
            self._start_playback()
        else:
            self.paused = True
            self.pause_offset = self._get_audio_time()
            pygame.mixer.music.stop()

    def _restart(self):
        self.paused = False
        self.audio_offset = 0.0
        pygame.mixer.music.stop()
        self._start_playback()

    def _seek(self, delta: float):
        current = self._get_audio_time()
        new_time = max(0.0, min(self.total_sec, current + delta))
        if self.paused:
            self.pause_offset = new_time
        else:
            pygame.mixer.music.stop()
            self.audio_offset = new_time
            self._start_playback()

    def _render_frame(self, time_sec: float) -> np.ndarray:
        return _render_single_frame(
            0, time_sec, self.fps, self.amiga_w, self.amiga_h,
            self.config.scenes, [], self.beat_interval, self.timeline,
            preview=True, crt_filter=False, effect_cache=self.effect_cache,
            text_scrollers=self.text_scrollers,
            transition_state=self.transition_state,
            audio_analysis=self.analysis,
            amiga_palette=self.config.amiga_palette,
            transition_sec=self.config.transition_sec,
        )

    def run(self):
        print(f"Duration: {self.total_sec:.1f}s  FPS target: {self.fps}")
        print("Space=pause  R=restart  <- ->=seek 5s  Esc/Q=quit")
        print()

        self._start_playback()

        frame_count = 0
        fps_last_time = time.time()

        while self.running:
            self._handle_events()
            if not self.running:
                break

            audio_time = self._get_audio_time()

            if audio_time >= self.total_sec:
                pygame.mixer.music.stop()
                break

            if not self.paused:
                arr = self._render_frame(audio_time)
                surf = pygame.surfarray.make_surface(arr.transpose(1, 0, 2))
                self.screen.blit(surf, (0, 0))
                pygame.display.flip()

                frame_count += 1
                now = time.time()
                elapsed = now - fps_last_time
                if elapsed >= 1.0:
                    display_fps = frame_count / elapsed
                    frame_count = 0
                    fps_last_time = now
                    pygame.display.set_caption(
                        f"Amiga Demo — {display_fps:.0f} FPS  "
                        f"Time: {audio_time:.1f}/{self.total_sec:.0f}s"
                    )

            self.clock.tick(self.fps)

        self._cleanup()
