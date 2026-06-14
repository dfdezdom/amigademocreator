from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

import yaml

from ..audio.sync import BeatTimeline
from ..effects.base import Effect
from ..effects.bouncing_ball import BouncingBall
from ..effects.copper_bars import CopperBars
from ..effects.dotfield import DotField
from ..effects.landscape import Landscape
from ..effects.metaballs import MetaBalls
from ..effects.plasma import Plasma
from ..effects.rotozoom import Rotozoom
from ..effects.scroller import SineScroller
from ..effects.sinus_scroll import SinusScroll
from ..effects.spectrum import SpectrumAnalyzer
from ..effects.tunnel import Tunnel
from ..effects.vector_objects import VectorObjects

EFFECT_REGISTRY: dict[str, type[Effect]] = {
    "plasma": Plasma,
    "bouncing_ball": BouncingBall,
    "copper_bars": CopperBars,
    "scroller": SineScroller,
    "rotozoom": Rotozoom,
    "tunnel": Tunnel,
    "vector_objects": VectorObjects,
    "spectrum": SpectrumAnalyzer,
    "metaballs": MetaBalls,
    "dotfield": DotField,
    "sinus_scroll": SinusScroll,
    "landscape": Landscape,
}

TEXT_EFFECT_REGISTRY: dict[str, type[Effect]] = {
    "sine_scroll": SineScroller,
    "sinus_scroll": SinusScroll,
}


@dataclass
class TextOverlay:
    text: str
    start_beat: int
    duration_beats: int
    effect: str = "sine_scroll"


@dataclass
class SceneDef:
    effect: str
    start_beat: int
    duration_beats: int
    params: dict[str, Any] = field(default_factory=dict)


@dataclass
class DemoConfig:
    audio: str
    output: str
    fps: int = 60
    amiga_palette: bool = True
    crt_filter: bool = True
    max_duration_sec: float | None = None
    preview: bool = False
    transition_sec: float = 1.0
    workers: int = 1
    resume: bool = False
    texts: list[TextOverlay] = field(default_factory=list)
    scenes: list[SceneDef] = field(default_factory=list)


def load_config(path: str) -> DemoConfig:
    with open(path) as f:
        data = yaml.safe_load(f)

    texts = []
    for t in data.get("texts", []):
        texts.append(TextOverlay(**t))

    scenes = []
    for s in data.get("scenes", []):
        scenes.append(SceneDef(**s))

    return DemoConfig(
        audio=data["audio"],
        output=data["output"],
        fps=data.get("fps", 60),
        amiga_palette=data.get("amiga_palette", True),
        crt_filter=data.get("crt_filter", True),
        max_duration_sec=data.get("max_duration_sec"),
        preview=data.get("preview", False),
        transition_sec=data.get("transition_sec", 1.0),
        workers=data.get("workers", 1),
        resume=data.get("resume", False),
        texts=texts,
        scenes=scenes,
    )


def build_effect(name: str, params: dict[str, Any], fps: int, amiga_palette: bool = True, audio_analysis: object | None = None) -> Effect:
    cls = EFFECT_REGISTRY.get(name)
    if cls is None:
        raise ValueError(f"Unknown effect '{name}'. Available: {list(EFFECT_REGISTRY)}")
    if name == "spectrum" and audio_analysis is not None:
        params = dict(params)
        params["audio_analysis"] = audio_analysis
    effect = cls(fps=fps, **params)
    effect.amiga_palette = amiga_palette
    return effect


def validate_config(config: DemoConfig, yaml_path: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not os.path.exists(config.audio):
        errors.append(f"Audio file not found: {config.audio}")

    if not config.scenes:
        errors.append("No scenes defined in timeline")

    if config.fps < 1:
        errors.append(f"fps must be >= 1, got {config.fps}")

    if config.transition_sec < 0:
        errors.append(f"transition_sec must be >= 0, got {config.transition_sec}")

    if config.workers < 1:
        errors.append(f"workers must be >= 1, got {config.workers}")

    if config.max_duration_sec is not None and config.max_duration_sec <= 0:
        errors.append(f"max_duration_sec must be > 0, got {config.max_duration_sec}")

    valid_effects = set(EFFECT_REGISTRY.keys())
    for i, scene in enumerate(config.scenes):
        if scene.effect not in valid_effects:
            errors.append(f"Scene {i}: unknown effect '{scene.effect}'. Available: {sorted(valid_effects)}")
        if scene.params is None:
            warnings.append(f"Scene {i} ({scene.effect}): no params defined")

    valid_text_effects = set(TEXT_EFFECT_REGISTRY.keys())
    for i, text in enumerate(config.texts):
        if text.effect not in valid_text_effects:
            warnings.append(f"Text {i}: unknown text effect '{text.effect}'. Available: {sorted(valid_text_effects)}")

    if config.workers > 1 and config.transition_sec > 0:
        warnings.append("Crossfade disabled in parallel mode (workers > 1)")

    overlapping = False
    sorted_scenes = sorted(config.scenes, key=lambda s: s.start_beat)
    for i in range(len(sorted_scenes) - 1):
        a = sorted_scenes[i]
        b = sorted_scenes[i + 1]
        a_end = a.start_beat + a.duration_beats
        if a_end > b.start_beat:
            overlapping = True
            break
    if overlapping:
        warnings.append("Overlapping scenes detected (scenes should not overlap in time)")

    return errors, warnings
