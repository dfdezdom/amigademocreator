# AmigaDemoCreator

Generates Amiga-style demo videos synchronized to `.wav` / `.aiff` music input.

## Architecture

```
main.py → amiga_demo/cli.py → renderer/output.py
                                ├── audio/analyzer.py  (librosa beat/BPM detection)
                                ├── audio/sync.py      (BeatTimeline)
                                ├── effects/*.py       (12 effects, see registry below)
                                └── renderer/          (scene, compositor, upscaler CRT, moviepy output via FFmpeg)
```

## Key constraints

- **Render pipeline**: 640×512 internal (2× Amiga OCS) → upscale to 1920×1080 with CRT scanlines
- **Amiga palette**: 32-color OCS palette enforced via `quantize_to_amiga()` in `utils/palette.py`
- **Audio sync**: pre-analyze `.wav` / `.aiff` with librosa (macOS Core Audio backend) → `BeatTimeline` → effects sync via `get_beat_phase(time)` / `get_beat_index(time)`
- **Memory**: frames written to disk as PNGs during render (not kept in RAM), enabling long videos
- **Crossfade**: `transition_sec` config for smooth scene transitions (default 1.0s). **Disabled when `workers > 1`** — parallel mode skips crossfade.
- **Parallel render**: `--workers N` or `workers: N` in YAML for multiprocess frame rendering.
- **Resume**: `--resume` or `resume: true` in YAML skips already-rendered frames. Frame cache is kept in `{output}_frames/` and cleaned up on non-resume runs.

## Commands

```sh
pip install -e .                           # install in editable mode
pip install -e ".[fast]"                   # install with OpenCV (faster upscale)
pip install -e ".[live]"                  # install with pygame (for --live playback)
python main.py examples/demo_timeline.yaml # render a demo
python main.py --preview examples/demo_timeline.yaml # fast preview (30fps, no upscale/CRT)
python main.py --workers 4 examples/demo_timeline.yaml # parallel render (4 workers)
python main.py --resume examples/demo_timeline.yaml  # resume from existing frames
python main.py --live examples/demo_timeline.yaml    # real-time playback with audio (pygame)
python -m pytest tests/ -v                 # run tests (14 tests: 12 effects + palette)
```

## Adding an effect

1. Create `amiga_demo/effects/your_effect.py` subclassing `Effect` (base.py)
2. Implement `render_frame(time_sec, beat_timeline) → PIL.Image`
3. Register in `amiga_demo/renderer/scene.py` `EFFECT_REGISTRY`

## Dependencies

Python ≥3.10, librosa, numpy, Pillow, moviepy, pyyaml, scipy.

Requires FFmpeg on `$PATH` for video encoding.

Optional extras:
- `fast`: `opencv-python-headless` for ~2× faster upscale resize
- `live`: `pygame>=2.5.0` for real-time preview playback

## Timeline format (`examples/demo_timeline.yaml`)

```yaml
audio: "music.wav"   # .wav and .aiff both supported
output: "demo.mp4"
fps: 60
amiga_palette: true
crt_filter: true
max_duration_sec: 20  # optional: render only first N seconds
preview: false        # optional: fast preview (30fps, no upscale/CRT)
workers: 1            # optional: parallel render workers
resume: false        # optional: resume from existing frames
transition_sec: 1.0   # crossfade between scenes

texts:
  - text: "Amiga Demo"
    start_beat: 0
    duration_beats: 8
    effect: sine_scroll

scenes:
  - effect: plasma
    start_beat: 0
    duration_beats: 16
    params: { palette: "fire", speed: 1.2 }
```

## Available effects

Registered in `amiga_demo/renderer/scene.py` `EFFECT_REGISTRY`:

- `plasma`
- `bouncing_ball`
- `copper_bars`
- `scroller`
- `rotozoom`
- `tunnel`
- `vector_objects`
- `spectrum`
- `metaballs`
- `dotfield`
- `sinus_scroll`
- `landscape`

Text effects (registered in `TEXT_EFFECT_REGISTRY`):

- `sine_scroll`
- `sinus_scroll`

## Performance

- Use `max_duration_sec` in YAML to preview short clips quickly
- Use `--preview` CLI flag or `preview: true` in YAML for fast preview at 30fps (no upscale/scanlines) — significantly faster than full render
- Parallel rendering with `--workers` helps for long videos; note crossfade is disabled in parallel mode

## Tests

```
tests/
├── test_effects.py   # smoke test each effect renders at 320×256
└── test_palette.py   # palette size + quantization
```

All pass: `pytest tests/ -v`

## Live playback

Requires `pip install -e ".[live]"`. Runs the demo in real-time with audio synced via pygame.

Keyboard controls during live playback:
- `Space` — pause
- `R` — restart
- `← / →` — seek ±5 seconds
- `Esc / Q` — quit

## Known gotchas

- **Crossfade disabled in parallel mode**: `workers > 1` automatically disables crossfade transitions (a warning is emitted).
- **Audio analysis is slow**: librosa beat tracking runs before any frames are rendered; for long audio files this can take several seconds.
- **Frame cache**: The `{output}_frames/` directory is deleted automatically after a successful render unless `--resume` is used.
- **macOS audio backend**: librosa uses Core Audio on macOS. If audio loading fails, verify the file is a valid `.wav` or `.aiff`.
