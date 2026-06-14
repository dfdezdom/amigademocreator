# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-06-14

### Added

- Initial release of AmigaDemoCreator
- 12 visual effects: plasma, bouncing_ball, copper_bars, scroller, rotozoom, tunnel, vector_objects, spectrum, metaballs, dotfield, sinus_scroll, landscape
- 2 text effects: sine_scroll, sinus_scroll
- Audio synchronization via librosa beat detection and BPM analysis
- Render pipeline: 640×512 internal resolution → 1920×1080 with CRT scanlines
- Amiga OCS 32-color palette enforcement
- Preview mode: fast rendering at 30fps without upscale/CRT
- Parallel rendering with multiprocessing (`--workers N`)
- Live playback mode with real-time audio sync via pygame
- Resume interrupted renders (`--resume`)
- Crossfade transitions between scenes (`transition_sec`)
- YAML timeline configuration format
- 14 tests with pytest (12 effects + 2 palette)
- FFmpeg video encoding integration
- Optional OpenCV support for faster upscaling
- Command-line interface with argparse
- `amiga_demo` console entry point

## [Unreleased]

### Planned

- Additional visual effects (fire, particles, starfield)
- GPU acceleration support
- More audio analysis features (onset detection, chroma features)
- Custom palette definitions in YAML
- Scene layering and compositing
- Video export profiles (720p, 4K, etc.)
- Plugin system for external effects
- Web-based timeline editor

---

## Release History

- **0.1.0** (2026-06-14) — Initial release
