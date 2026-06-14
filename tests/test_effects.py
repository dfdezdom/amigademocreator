from __future__ import annotations

import numpy as np
import pytest
from PIL import Image

from amiga_demo.audio.sync import BeatTimeline
from amiga_demo.effects.bouncing_ball import BouncingBall
from amiga_demo.effects.copper_bars import CopperBars
from amiga_demo.effects.dotfield import DotField
from amiga_demo.effects.landscape import Landscape
from amiga_demo.effects.metaballs import MetaBalls
from amiga_demo.effects.plasma import Plasma
from amiga_demo.effects.rotozoom import Rotozoom
from amiga_demo.effects.scroller import SineScroller
from amiga_demo.effects.sinus_scroll import SinusScroll
from amiga_demo.effects.spectrum import SpectrumAnalyzer
from amiga_demo.effects.tunnel import Tunnel
from amiga_demo.effects.vector_objects import VectorObjects


@pytest.fixture
def beat_timeline() -> BeatTimeline:
    import numpy as np
    return BeatTimeline(
        bpm=120.0,
        total_beats=100,
        beat_times=np.arange(0, 50.0, 0.5),
        duration_sec=50.0,
    )


def test_plasma_renders(beat_timeline: BeatTimeline) -> None:
    effect = Plasma(width=320, height=256, fps=60)
    img = effect.render_frame(1.0, beat_timeline)
    assert isinstance(img, Image.Image)
    assert img.size == (320, 256)


def test_bouncing_ball_renders(beat_timeline: BeatTimeline) -> None:
    effect = BouncingBall(width=320, height=256, fps=60)
    img = effect.render_frame(0.5, beat_timeline)
    assert isinstance(img, Image.Image)
    assert img.size == (320, 256)


def test_copper_bars_renders(beat_timeline: BeatTimeline) -> None:
    effect = CopperBars(width=320, height=256, fps=60)
    img = effect.render_frame(0.0, beat_timeline)
    assert isinstance(img, Image.Image)
    assert img.size == (320, 256)


def test_scroller_renders(beat_timeline: BeatTimeline) -> None:
    effect = SineScroller(width=320, height=256, fps=60, text="Test")
    img = effect.render_frame(0.0, beat_timeline)
    assert isinstance(img, Image.Image)
    assert img.size == (320, 256)


def test_rotozoom_renders(beat_timeline: BeatTimeline) -> None:
    effect = Rotozoom(width=320, height=256, fps=60)
    img = effect.render_frame(0.0, beat_timeline)
    assert isinstance(img, Image.Image)
    assert img.size == (320, 256)


def test_tunnel_renders(beat_timeline: BeatTimeline) -> None:
    effect = Tunnel(width=320, height=256, fps=60)
    img = effect.render_frame(1.0, beat_timeline)
    assert isinstance(img, Image.Image)
    assert img.size == (320, 256)


def test_vector_objects_renders(beat_timeline: BeatTimeline) -> None:
    effect = VectorObjects(width=320, height=256, fps=60)
    img = effect.render_frame(1.0, beat_timeline)
    assert isinstance(img, Image.Image)
    assert img.size == (320, 256)


def test_spectrum_renders(beat_timeline: BeatTimeline) -> None:
    effect = SpectrumAnalyzer(width=320, height=256, fps=60, band_count=8)
    img = effect.render_frame(1.0, beat_timeline)
    assert isinstance(img, Image.Image)
    assert img.size == (320, 256)


def test_metaballs_renders(beat_timeline: BeatTimeline) -> None:
    effect = MetaBalls(width=320, height=256, fps=60, ball_count=4)
    img = effect.render_frame(1.0, beat_timeline)
    assert isinstance(img, Image.Image)
    assert img.size == (320, 256)


def test_dotfield_renders(beat_timeline: BeatTimeline) -> None:
    effect = DotField(width=320, height=256, fps=60, dot_count=100)
    img = effect.render_frame(1.0, beat_timeline)
    assert isinstance(img, Image.Image)
    assert img.size == (320, 256)


def test_sinus_scroll_renders(beat_timeline: BeatTimeline) -> None:
    effect = SinusScroll(width=320, height=256, fps=60, text="Test", wave_count=2)
    img = effect.render_frame(0.0, beat_timeline)
    assert isinstance(img, Image.Image)
    assert img.size == (320, 256)


def test_landscape_renders(beat_timeline: BeatTimeline) -> None:
    effect = Landscape(width=320, height=256, fps=60)
    img = effect.render_frame(1.0, beat_timeline)
    assert isinstance(img, Image.Image)
    assert img.size == (320, 256)
