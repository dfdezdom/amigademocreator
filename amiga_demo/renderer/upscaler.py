from __future__ import annotations

import numpy as np

try:
    import cv2

    HAVE_CV2 = True
except ImportError:
    HAVE_CV2 = False
    from PIL import Image


def upscale_to_array(
    arr: np.ndarray,
    target_size: tuple[int, int] = (1920, 1080),
    crt_filter: bool = True,
) -> np.ndarray:
    if HAVE_CV2:
        result = cv2.resize(arr, target_size, interpolation=cv2.INTER_NEAREST)
    else:
        from PIL import Image

        pil_img = Image.fromarray(arr)
        scaled = pil_img.resize(target_size, Image.NEAREST)
        result = np.array(scaled, dtype=np.uint8, copy=True)
    if crt_filter:
        result[1::2, :, :] = (result[1::2, :, :].astype(np.uint16) * 3 // 4).astype(np.uint8)
    return result
