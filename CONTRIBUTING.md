# Contributing to AmigaDemoCreator

¡Gracias por tu interés en contribuir! Este proyecto es open source bajo la licencia MIT y agradecemos cualquier tipo de contribución: nuevos efectos, correcciones de bugs, mejoras de rendimiento, documentación, etc.

## Cómo empezar

1. **Fork** el repositorio en GitHub
2. **Clona** tu fork:
   ```sh
   git clone https://github.com/tu-usuario/amigademocreator.git
   cd amigademocreator
   ```
3. **Crea un entorno virtual** (recomendado):
   ```sh
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   # .venv\Scripts\activate     # Windows
   ```
4. **Instala en modo desarrollo**:
   ```sh
   pip install -e ".[fast]"
   ```

## Antes de enviar un PR

### Ejecutar tests

Obligatorio antes de crear un Pull Request:

```sh
python -m pytest tests/ -v
```

Deben pasar los 14 tests (12 efectos + 2 de paleta).

### Revisar tu código

- Asegúrate de que no hay errores de sintaxis
- Verifica que los efectos nuevos funcionan correctamente
- Comprueba que no se rompe el renderizado existente

## Añadir un nuevo efecto

Puedes contribuir con nuevos efectos visuales o de texto. Sigue estos pasos:

### 1. Crear el archivo del efecto

Crea un nuevo archivo en `amiga_demo/effects/tu_efecto.py`:

```python
from __future__ import annotations

import numpy as np
from PIL import Image

from ..audio.sync import BeatTimeline
from .base import Effect


class TuEfecto(Effect):
    def __init__(self, width: int = 640, height: int = 512, fps: int = 60, **kwargs):
        super().__init__(width, height, fps)
        # Inicializa parámetros específicos
        self.parametro = kwargs.get("parametro", 1.0)

    def render_frame(self, time_sec: float, beat_timeline: BeatTimeline) -> Image.Image:
        # 1. Crear frame vacío
        frame = self._new_frame()
        
        # 2. Renderizar tu efecto
        # Usa beat_timeline.get_beat_phase(time_sec) para sincronización
        # Usa beat_timeline.get_beat_index(time_sec) para índice de beat
        
        # 3. Convertir a imagen
        return self._to_image(frame)
```

### 2. Registrar el efecto

Añade tu efecto al registro en `amiga_demo/renderer/scene.py`:

```python
from ..effects.tu_efecto import TuEfecto

EFFECT_REGISTRY = {
    # ... efectos existentes ...
    "tu_efecto": TuEfecto,
}
```

Si es un efecto de texto, añádelo a `TEXT_EFFECT_REGISTRY`.

### 3. Añadir test

Añade un test en `tests/test_effects.py`:

```python
def test_tu_efecto_renders(beat_timeline: BeatTimeline) -> None:
    from amiga_demo.effects.tu_efecto import TuEfecto
    effect = TuEfecto(width=320, height=256, fps=60)
    img = effect.render_frame(1.0, beat_timeline)
    assert isinstance(img, Image.Image)
    assert img.size == (320, 256)
```

### 4. Documentar

- Actualiza la lista de efectos en `README.md`
- Documenta los parámetros aceptados en un comentario o en el README

## Convenciones de código

- **Type hints** obligatorias en todas las funciones y métodos
- **`from __future__ import annotations`** en cada archivo Python
- **Naming**: usa `snake_case` para variables y funciones, `PascalCase` para clases
- **Herencia de efectos**: todos los efectos deben heredar de `Effect` en `amiga_demo/effects/base.py`
- **Sincronización**: usa `beat_timeline.get_beat_phase(time_sec)` para sincronizar con el audio
- **Paleta**: respeta `self.amiga_palette` para aplicar la paleta Amiga de 32 colores

## Reportar bugs

Abre un [issue en GitHub](https://github.com/dfdezdom/amigademocreator/issues) con:

- Descripción clara del problema
- Pasos para reproducirlo
- Versión de Python y sistema operativo
- Mensaje de error completo (si aplica)

## Sugerencias de mejoras

También puedes abrir un issue para proponer:
- Nuevos efectos visuales
- Mejoras de rendimiento
- Nuevas características
- Cambios en la arquitectura

## Pull Requests

- Usa una rama descriptiva: `feature/nuevo-efecto`, `fix/bug-renderizado`, etc.
- Escribe un título claro y descriptivo
- Incluye una descripción de los cambios y por qué
- Asegúrate de que todos los tests pasan
- Actualiza la documentación si es necesario

## Código de conducta

Sé respetuoso y constructivo. Todas las contribuciones son valiosas, desde correcciones de typos hasta nuevas características importantes.

## Contacto

- Autor: [dfdezdom](https://github.com/dfdezdom)
- Repo: [amigademocreator](https://github.com/dfdezdom/amigademocreator)

---

¡Gracias por contribuir! 🎮✨
