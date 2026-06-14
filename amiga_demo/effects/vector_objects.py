from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw

from ..audio.sync import BeatTimeline
from ..utils.palette import quantize_to_amiga
from .base import Effect


_OBJECTS: dict[str, tuple[np.ndarray, list[tuple[int, int]]]] = {}


def _build_cube() -> tuple[np.ndarray, list[tuple[int, int]]]:
    s = 1.0
    verts = np.array([
        [-s, -s, -s], [ s, -s, -s], [ s,  s, -s], [-s,  s, -s],
        [-s, -s,  s], [ s, -s,  s], [ s,  s,  s], [-s,  s,  s],
    ], dtype=np.float32)
    edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
    return verts, edges


def _build_pyramid() -> tuple[np.ndarray, list[tuple[int, int]]]:
    s = 1.0
    h = 1.2
    verts = np.array([
        [-s, -s, -s], [ s, -s, -s], [ s, -s,  s], [-s, -s,  s],
        [ 0,  h,  0],
    ], dtype=np.float32)
    edges = [(0,1),(1,2),(2,3),(3,0),(0,4),(1,4),(2,4),(3,4)]
    return verts, edges


def _build_sphere(rings: int = 8, segments: int = 12) -> tuple[np.ndarray, list[tuple[int, int]]]:
    verts = []
    edges = []
    for i in range(rings + 1):
        theta = math.pi * i / rings
        for j in range(segments):
            phi = 2 * math.pi * j / segments
            x = math.sin(theta) * math.cos(phi)
            y = math.cos(theta)
            z = math.sin(theta) * math.sin(phi)
            verts.append((x, y, z))
            if i > 0:
                prev = (i - 1) * segments + j
                curr = i * segments + j
                prev_next = (i - 1) * segments + (j + 1) % segments
                curr_next = i * segments + (j + 1) % segments
                edges.append((prev, curr))
                edges.append((prev, prev_next))
    return np.array(verts, dtype=np.float32), edges


_OBJECTS = {
    "cube": _build_cube(),
    "pyramid": _build_pyramid(),
    "sphere": _build_sphere(),
}


def _project(verts: np.ndarray, rot_matrix: np.ndarray, cx: float, cy: float, scale: float) -> np.ndarray:
    rotated = verts @ rot_matrix.T
    projected = np.empty((len(verts), 2), dtype=np.int32)
    for i, (x, y, z) in enumerate(rotated):
        if z < 0.01:
            z = 0.01
        projected[i, 0] = int(cx + x * scale / z)
        projected[i, 1] = int(cy - y * scale / z)
    return projected


class VectorObjects(Effect):
    def __init__(
        self,
        width: int = 640,
        height: int = 512,
        fps: int = 60,
        object_type: str = "cube",
        rotation_speed: float = 0.5,
        scale: int = 100,
        color: tuple[int, int, int] = (180, 180, 255),
    ):
        super().__init__(width, height, fps)
        self.object_type = object_type
        self.rotation_speed = rotation_speed
        self.scale = scale
        self.color = tuple(color)
        if object_type not in _OBJECTS:
            raise ValueError(f"Unknown object '{object_type}'. Available: {list(_OBJECTS)}")
        self.verts, self.edges = _OBJECTS[object_type]

    def render_frame(self, time_sec: float, beat_timeline: BeatTimeline) -> Image.Image:
        pil_img = Image.new("RGB", (self.width, self.height), (0, 0, 0))
        draw = ImageDraw.Draw(pil_img)
        cx, cy = self.width // 2, self.height // 2

        beat_phase = beat_timeline.get_beat_phase(time_sec)
        rx = time_sec * self.rotation_speed * 1.0 + beat_phase * 0.5
        ry = time_sec * self.rotation_speed * 0.7
        rz = time_sec * self.rotation_speed * 0.3

        cx2, sx2 = math.cos(rx), math.sin(rx)
        cy2, sy2 = math.cos(ry), math.sin(ry)
        cz2, sz2 = math.cos(rz), math.sin(rz)

        rot_x = np.array([[1, 0, 0], [0, cx2, -sx2], [0, sx2, cx2]], dtype=np.float32)
        rot_y = np.array([[cy2, 0, sy2], [0, 1, 0], [-sy2, 0, cy2]], dtype=np.float32)
        rot_z = np.array([[cz2, -sz2, 0], [sz2, cz2, 0], [0, 0, 1]], dtype=np.float32)
        rot = rot_z @ rot_y @ rot_x

        proj = _project(self.verts, rot, cx, cy, self.scale)

        for i, j in self.edges:
            draw.line([tuple(proj[i]), tuple(proj[j])], fill=self.color, width=1)

        frame = np.array(pil_img, dtype=np.uint8)
        if self.amiga_palette:
            frame = quantize_to_amiga(frame)
        return self._to_image(frame)
