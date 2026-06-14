# AmigaDemoCreator

```
    _          _                  _      ____                _             _
   / \   _ __ (_) __ _  ___ _ __ | |_   / ___|_ __ ___  __ _| | ___  _   _| |_
  / _ \ | '_ \| |/ _` |/ _ \ '_ \| __| | |   | '__/ _ \/ _` | |/ _ \| | | | __|
 / ___ \| | | | | (_| |  __/ | | | |_  | |___| | |  __/ (_| | | (_) | |_| | |_
/_/   \_\_| |_|_|\__, |\___|_| |_|\__|  \____|_|  \___|\__, |_|\___/ \__,_|\__|
                 |___/                                 |___/
```

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.1.0-green.svg)](https://github.com/dfdezdom/amigademocreator)

Genera videos con el estilo de una demo de Amiga a partir de un archivo de audio. Sincroniza efectos visuales retro con el ritmo de la música usando análisis de beats.

---

## Demo

<!-- Añade aquí un GIF o screenshot de tu demo -->
<!-- Ejemplo: ![Demo](docs/demo.gif) -->

## Requisitos

- **Python** ≥ 3.10
- **FFmpeg** instalado y disponible en `$PATH`
- **pip** para gestionar dependencias

## Instalación

```sh
git clone https://github.com/dfdezdom/amigademocreator.git
cd amigademocreator
pip install -e .
```

### Opciones adicionales

```sh
# Para renderizado más rápido (usando OpenCV)
pip install -e ".[fast]"

# Para reproducción en tiempo real (usando pygame)
pip install -e ".[live]"
```

## Uso rápido

```sh
# Renderizar un demo
python main.py examples/demo_timeline.yaml

# Vista previa rápida (30fps, sin upscale ni CRT)
python main.py --preview examples/demo_timeline.yaml

# Renderizado paralelo (4 trabajadores)
python main.py --workers 4 examples/demo_timeline.yaml

# Reanudar un renderizado interrumpido
python main.py --resume examples/demo_timeline.yaml

# Reproducción en tiempo real con audio
python main.py --live examples/demo_timeline.yaml
```

## Modos de ejecución

| Modo | Descripción | Comando/Config |
|------|-------------|----------------|
| **Normal** | Calidad completa, 60fps, CRT scanlines | (por defecto) |
| **Preview** | Rápido: 30fps, sin upscale ni CRT | `--preview` o `preview: true` |
| **Paralelo** | Usa múltiples procesos para renderizar | `--workers N` o `workers: N` |
| **Resume** | Reanuda desde frames ya renderizados | `--resume` o `resume: true` |
| **Live** | Reproducción en tiempo real con audio | `--live` (requiere pygame) |

## Efectos disponibles

### Efectos visuales

- `plasma` — Efecto de plasma animado
- `bouncing_ball` — Pelota rebotando al ritmo
- `copper_bars` — Barras de color estilo Amiga Copper
- `scroller` — Texto scroll horizontal
- `rotozoom` — Rotación y zoom de texturas
- `tunnel` — Efecto de túnel 3D
- `vector_objects` — Objetos 3D vectoriales (cubo, etc.)
- `spectrum` — Analizador de espectro de audio
- `metaballs` — Meta-balls metabólicas
- `dotfield` — Campo de partículas
- `sinus_scroll` — Scroll senoidal de texto
- `landscape` — Paisaje 3D wireframe

### Efectos de texto

- `sine_scroll` — Scroll con onda sinusoidal
- `sinus_scroll` — Scroll senoidal alternativo

## Formato de timeline (YAML)

```yaml
audio: "Zero.aiff"       # .wav y .aiff soportados
output: "demo.mp4"
fps: 60
amiga_palette: true
crt_filter: true
max_duration_sec: 280    # opcional: renderizar solo N segundos
preview: false           # opcional: preview rápido
workers: 1               # opcional: trabajadores paralelos
resume: false           # opcional: reanudar render
transition_sec: 1.0      # duración de crossfade entre escenas

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

## Añadir un efecto

1. Crear `amiga_demo/effects/tu_efecto.py` heredando de `Effect`
2. Implementar `render_frame(time_sec, beat_timeline) -> PIL.Image`
3. Registrar en `amiga_demo/renderer/scene.py` en `EFFECT_REGISTRY` o `TEXT_EFFECT_REGISTRY`

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para más detalles.

## Tests

```sh
python -m pytest tests/ -v
```

14 tests: 12 efectos + 2 de paleta.

## Arquitectura

```
main.py
  └── amiga_demo/cli.py
        └── renderer/output.py
              ├── audio/analyzer.py    (análisis de audio con librosa)
              ├── audio/sync.py        (BeatTimeline)
              ├── effects/*.py         (12 efectos visuales)
              └── renderer/
                    ├── scene.py        (configuración y registro)
                    ├── compositor.py   (crossfade y fades)
                    ├── upscaler.py     (upscale + CRT scanlines)
                    └── output.py       (renderizado y encoding FFmpeg)
```

## Contribuir

¡Las contribuciones son bienvenidas! Consulta [CONTRIBUTING.md](CONTRIBUTING.md) para más información.

## Autor

- **dfdezdom** — [GitHub](https://github.com/dfdezdom)

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

**¡Disfruta creando demos al estilo Amiga! 🎮🎶**
