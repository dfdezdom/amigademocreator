from __future__ import annotations

import numpy as np

from amiga_demo.utils.palette import AMIGA_OCS_COLORS_12BIT, quantize_to_amiga


def test_palette_has_32_colors() -> None:
    assert len(AMIGA_OCS_COLORS_12BIT) == 32


def test_quantize_to_amiga() -> None:
    img = np.array([[[100, 150, 200]]], dtype=np.uint8)
    result = quantize_to_amiga(img)
    assert result.shape == (1, 1, 3)
    assert result.dtype == np.uint8
