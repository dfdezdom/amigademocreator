# AmigaDemoCreator

Generates Amiga-style demo videos synchronized to `.wav` / `.aiff` music input.

## Architecture

```
main.py → amiga_demo/cli.py → renderer/output.py
                                ├── audio/analyzer.py  (librosa beat/BPM detection)
                                ├── audio/sync.py      (BeatTimeline)
                                ├── effects/*.py       (10 effects: starfield, plasma, bouncing_ball, copper_bars, scroller, rotozoom, fire, tunnel, particles, vector_objects)
                                └── renderer/          (scene, compositor, upscaler CRT, moviepy output via FFmpeg)
```

## Key constraints

- **Render pipeline**: 640×512 internal (2× Amiga OCS) → upscale to 1920×1080 with CRT scanlines
- **Amiga palette**: 32-color OCS palette enforced via `quantize_to_amiga()` in `utils/palette.py`
- **Audio sync**: pre-analyze `.wav` / `.aiff` with librosa (macOS Core Audio backend) → `BeatTimeline` → effects sync via `get_beat_phase(time)` / `get_beat_index(time)`
- **Memory**: frames written to disk as PNGs during render (not kept in RAM), enabling long videos
- **Crossfade**: `transition_sec` config for smooth scene transitions (default 1.0s)
- **Parallel render**: `--workers N` or `workers: N` in YAML for multiprocess frame rendering

## Commands

```sh
pip install -e .                           # install in editable mode
pip install -e ".[fast]"                   # install with OpenCV (faster upscale)
python main.py examples/demo_timeline.yaml # render a demo
python main.py --preview examples/demo_timeline.yaml # fast preview (30fps, no upscale)
python main.py --workers 4 examples/demo_timeline.yaml # parallel render (4 workers)
python -m pytest tests/ -v                 # run tests (12 tests, all effects + palette)
```

## Adding an effect

1. Create `amiga_demo/effects/your_effect.py` subclassing `Effect` (base.py)
2. Implement `render_frame(time_sec, beat_timeline) → PIL.Image`
3. Register in `renderer/scene.py` `EFFECT_REGISTRY`

## Dependencies

Python ≥3.10, librosa, numpy, Pillow, moviepy, pyyaml, scipy.

Requires FFmpeg on `$PATH` for video encoding.

## Timeline format (`examples/demo_timeline.yaml`)

```yaml
audio: "music.wav"   # .wav and .aiff both supported
output: "demo.mp4"
fps: 60
amiga_palette: true
crt_filter: true
max_duration_sec: 20  # optional: render only first N seconds

texts:
  - text: "Amiga Demo"
    start_beat: 0
    duration_beats: 8
    effect: sine_scroll

scenes:
  - effect: starfield
    start_beat: 0
    duration_beats: 16
    params: { star_count: 200, speed: 2.5 }
```

## Performance

- Effects render at ~6-70 fps (starfield is slowest at ~70ms/frame)
- Upscale + scanlines add ~60ms/frame
- Use `max_duration_sec` in YAML to preview short clips quickly
- Use `--preview` CLI flag or `preview: true` in YAML for fast preview at 30fps (no upscale/scanlines) — ~2-3x faster

## Optional OpenCV

Install with `pip install -e ".[fast]"` to use `opencv-python-headless` for ~2x faster upscale resize.

## Tests

```
tests/
├── test_effects.py   # smoke test each effect renders at 320×256
└── test_palette.py   # palette size + quantization
```

All pass: `pytest tests/ -v`
