# AmigaDemoCreator

```
    ___    __  __ _         __      __              _            __
   /   |  /  |/  (_)____ _ / /___ _/ /____ _ _  __ (_)_____ ____/ /____
  / /| | / /|_/ // // __ `// // __ `// __ `/| |/ // // ___// __  // __ \
 / ___ |/ /  / // // /_/ // // /_/ // /_/ / |  / // // /   / /_/ // /_/ /
/_/  |_/_/  /_//_/ \__, //_/ \__,_// \__,_/  |_/_/_//_/    \__,_/ \____/
                  /____/           /____/

   _____                                                     __
  / ___/ ___   _____ ____ ___   ____ ___   ___   _____ ____ / /_
  \__ \ / _ \ / ___// __ `__ \ / __ `__ \ / _ \ / ___// __ `// __/
 ___/ //  __// /__ / / / / / // / / / / //  __// /__ / /_/ // /_
/____/ \___/ \___//_/ /_/ /_//_/ /_/ /_/ \___/ \___/ \__,_/ \__/
```

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.1.0-green.svg)](https://github.com/dfdezdom/amigademocreator)

Generate Amiga-style demo videos synchronized to music. Retro visual effects synced to the beat of your audio using real-time analysis.

---

## Demo

<!-- Add a GIF or screenshot here -->
<!-- Example: ![Demo](docs/demo.gif) -->

## Requirements

- **Python** ≥ 3.10
- **FFmpeg** installed and available in `$PATH`
- **pip** for dependency management

## Installation

```sh
git clone https://github.com/dfdezdom/amigademocreator.git
cd amigademocreator
pip install -e .
```

### Optional extras

```sh
# Faster rendering (using OpenCV)
pip install -e ".[fast]"

# Real-time playback (using pygame)
pip install -e ".[live]"
```

## Quick Start

```sh
# Render a demo
python main.py examples/demo_timeline.yaml

# Fast preview (30fps, no upscale/CRT)
python main.py --preview examples/demo_timeline.yaml

# Parallel rendering (4 workers)
python main.py --workers 4 examples/demo_timeline.yaml

# Resume an interrupted render
python main.py --resume examples/demo_timeline.yaml

# Real-time playback with audio
python main.py --live examples/demo_timeline.yaml
```

## Render Modes

| Mode | Description | Command / Config |
|------|-------------|----------------|
| **Normal** | Full quality, 60fps, CRT scanlines | (default) |
| **Preview** | Fast: 30fps, no upscale/CRT | `--preview` or `preview: true` |
| **Parallel** | Multi-process rendering | `--workers N` or `workers: N` |
| **Resume** | Continue from existing frames | `--resume` or `resume: true` |
| **Live** | Real-time playback with audio | `--live` (requires pygame) |

## Available Effects

### Visual Effects

- `plasma` — Animated plasma effect
- `bouncing_ball` — Ball bouncing to the beat
- `copper_bars` — Amiga-style color bars
- `scroller` — Horizontal text scroller
- `rotozoom` — Rotating and zooming textures
- `tunnel` — 3D tunnel effect
- `vector_objects` — 3D vector objects (cube, etc.)
- `spectrum` — Audio spectrum analyzer
- `metaballs` — Metaballs effect
- `dotfield` — Particle field
- `sinus_scroll` — Sinusoidal text scroll
- `landscape` — 3D wireframe landscape

### Text Effects

- `sine_scroll` — Sine wave text scroll
- `sinus_scroll` — Alternative sinusoidal scroll

## Timeline Format (YAML)

```yaml
audio: "Zero.aiff"       # .wav and .aiff supported
output: "demo.mp4"
fps: 60
amiga_palette: true
crt_filter: true
max_duration_sec: 280    # optional: render only N seconds
preview: false           # optional: fast preview
workers: 1               # optional: parallel workers
resume: false           # optional: resume render
transition_sec: 1.0      # crossfade duration between scenes

texts:
  - text: "Amiga Demo Creator"
    start_beat: 0
    duration_beats: 16
    effect: sine_scroll

scenes:
  - effect: plasma
    start_beat: 0
    duration_beats: 64
    params:
      palette: "fire"
      speed: 1.2
```

## Adding an Effect

1. Create `amiga_demo/effects/your_effect.py` extending `Effect`
2. Implement `render_frame(time_sec, beat_timeline) -> PIL.Image`
3. Register in `amiga_demo/renderer/scene.py` in `EFFECT_REGISTRY` or `TEXT_EFFECT_REGISTRY`

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

## Tests

```sh
python -m pytest tests/ -v
```

14 tests: 12 effects + 2 palette.

## Architecture

```
main.py
  └── amiga_demo/cli.py
        └── renderer/output.py
              ├── audio/analyzer.py    (librosa audio analysis)
              ├── audio/sync.py        (BeatTimeline)
              ├── effects/*.py         (12 visual effects)
              └── renderer/
                    ├── scene.py        (config and registry)
                    ├── compositor.py   (crossfade and fades)
                    ├── upscaler.py     (upscale + CRT scanlines)
                    └── output.py       (rendering and FFmpeg encoding)
```

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for more information.

## Author

- **dfdezdom** — [GitHub](https://github.com/dfdezdom)

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

**Enjoy creating Amiga-style demos! 🎮🎶**
