from __future__ import annotations

import numpy as np

BAYER_8x8 = np.array([
    [ 0, 48, 12, 60,  3, 51, 15, 63],
    [32, 16, 44, 28, 35, 19, 47, 31],
    [ 8, 56,  4, 52, 11, 59,  7, 55],
    [40, 24, 36, 20, 43, 27, 39, 23],
    [ 2, 50, 14, 62,  1, 49, 13, 61],
    [34, 18, 46, 30, 33, 17, 45, 29],
    [10, 58,  6, 54,  9, 57,  5, 53],
    [42, 26, 38, 22, 41, 25, 37, 21],
], dtype=np.uint8)


def ordered_dither(image: np.ndarray, matrix: np.ndarray | None = None) -> np.ndarray:
    if matrix is None:
        matrix = BAYER_8x8
    h, w = image.shape[:2]
    mh, mw = matrix.shape
    n_tiles_y = h // mh + 1
    n_tiles_x = w // mw + 1
    threshold_tiled = np.tile(matrix, (n_tiles_y, n_tiles_x))[:h, :w]
    threshold_norm = threshold_tiled.astype(np.float32) / 63.0 - 0.5
    step = 255.0 / 31.0
    offset = threshold_norm * step
    img_f = image.astype(np.float32)
    for c in range(3):
        img_f[:, :, c] += offset
    return np.clip(img_f, 0, 255).astype(np.uint8)
