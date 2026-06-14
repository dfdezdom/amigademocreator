from __future__ import annotations

import numpy as np

AMIGA_OCS_COLORS_12BIT: list[tuple[int, int, int]] = [
    (0, 0, 0),
    (255, 255, 255),
    (170, 0, 0),
    (0, 170, 0),
    (0, 0, 170),
    (255, 170, 0),
    (170, 255, 0),
    (0, 255, 170),
    (170, 0, 255),
    (255, 0, 170),
    (170, 85, 0),
    (85, 170, 0),
    (0, 170, 85),
    (85, 0, 170),
    (170, 0, 85),
    (85, 85, 85),
    (170, 170, 170),
    (255, 85, 85),
    (85, 255, 85),
    (85, 85, 255),
    (255, 255, 85),
    (85, 255, 255),
    (255, 85, 255),
    (255, 170, 170),
    (170, 255, 170),
    (170, 170, 255),
    (255, 255, 170),
    (170, 255, 255),
    (255, 170, 255),
    (255, 85, 170),
    (170, 255, 85),
    (85, 170, 255),
]

_AMIGA_PALETTE_NP = np.array(AMIGA_OCS_COLORS_12BIT, dtype=np.uint8)
_AMIGA_PALETTE_F32 = _AMIGA_PALETTE_NP.astype(np.float32)

def _build_quantize_lut() -> np.ndarray:
    lut = np.zeros((32, 32, 32), dtype=np.uint8)
    pal = _AMIGA_PALETTE_F32
    for r in range(32):
        cr = int(r * 255 / 31)
        for g in range(32):
            cg = int(g * 255 / 31)
            for b in range(32):
                cb = int(b * 255 / 31)
                c = np.array([cr, cg, cb], dtype=np.float32)
                d = np.sum((pal - c) ** 2, axis=1)
                lut[r, g, b] = d.argmin()
    return lut


_QUANTIZE_LUT: np.ndarray = _build_quantize_lut()


def quantize_to_amiga(image: np.ndarray, dither: bool = False) -> np.ndarray:
    if dither:
        from .dither import ordered_dither  # noqa: PLC0415
        image = ordered_dither(image)
    r_idx = np.clip(image[:, :, 0].astype(np.uint16) * 31 // 255, 0, 31)
    g_idx = np.clip(image[:, :, 1].astype(np.uint16) * 31 // 255, 0, 31)
    b_idx = np.clip(image[:, :, 2].astype(np.uint16) * 31 // 255, 0, 31)
    return _AMIGA_PALETTE_NP[_QUANTIZE_LUT[r_idx, g_idx, b_idx]]


def quantize_to_amiga_fast(image: np.ndarray) -> np.ndarray:
    r = (image[:, :, 0].astype(np.uint16) + 8) // 17 * 17
    g = (image[:, :, 1].astype(np.uint16) + 8) // 17 * 17
    b = (image[:, :, 2].astype(np.uint16) + 8) // 17 * 17
    result = np.stack([r, g, b], axis=2).astype(np.uint8)
    return quantize_to_amiga(result)


def generate_gradient_palette(
    color_a: tuple[int, int, int], color_b: tuple[int, int, int], steps: int = 16
) -> list[tuple[int, int, int]]:
    result = []
    for i in range(steps):
        t = i / (steps - 1)
        r = int(color_a[0] + (color_b[0] - color_a[0]) * t)
        g = int(color_a[1] + (color_b[1] - color_a[1]) * t)
        b = int(color_a[2] + (color_b[2] - color_a[2]) * t)
        result.append((r, g, b))
    return result


def fire_palette(steps: int = 32) -> list[tuple[int, int, int]]:
    result = []
    for i in range(steps):
        t = i / (steps - 1)
        r = int(min(255, t * 510))
        g = int(max(0, min(255, (t - 0.5) * 510)))
        b = 0
        result.append((r, g, b))
    return result


def ocean_palette(steps: int = 32) -> list[tuple[int, int, int]]:
    result = []
    for i in range(steps):
        t = i / (steps - 1)
        r = int(20 + (t * 40))
        g = int(60 + (t * 150))
        b = int(120 + (t * 135))
        result.append((r, g, b))
    return result


AMIGA_FIRE_COLORS: list[tuple[int, int, int]] = [
    (0, 0, 0),
    (85, 85, 85),
    (170, 0, 0),
    (170, 85, 0),
    (255, 85, 85),
    (255, 170, 0),
    (255, 255, 85),
    (255, 255, 170),
    (255, 255, 255),
]


AMIGA_OCEAN_COLORS: list[tuple[int, int, int]] = [
    (0, 0, 0),
    (0, 0, 170),
    (0, 170, 85),
    (0, 170, 0),
    (85, 170, 255),
    (170, 170, 255),
    (170, 255, 255),
    (85, 255, 255),
    (255, 255, 255),
]


def amiga_fire_palette(steps: int = 64) -> list[tuple[int, int, int]]:
    n = len(AMIGA_FIRE_COLORS)
    result = []
    for i in range(steps):
        idx = min(i * n // steps, n - 1)
        result.append(AMIGA_FIRE_COLORS[idx])
    return result


def amiga_ocean_palette(steps: int = 64) -> list[tuple[int, int, int]]:
    n = len(AMIGA_OCEAN_COLORS)
    result = []
    for i in range(steps):
        idx = min(i * n // steps, n - 1)
        result.append(AMIGA_OCEAN_COLORS[idx])
    return result
