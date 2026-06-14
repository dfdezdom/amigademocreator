from __future__ import annotations

import os
import re
import shutil
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np
from moviepy import AudioFileClip, ImageSequenceClip
from PIL import Image
from tqdm import tqdm

from ..audio.analyzer import AudioAnalysis
from ..audio.sync import BeatTimeline
from .scene import DemoConfig, TEXT_EFFECT_REGISTRY, build_effect
from .upscaler import upscale_to_array


def _find_scene(scenes, time_sec, beat_interval):
    for s in scenes:
        s_start = s.start_beat * beat_interval
        s_end = (s.start_beat + s.duration_beats) * beat_interval
        if s_start <= time_sec < s_end:
            return s
    return None


def _render_single_frame(
    frame_idx: int,
    time_sec: float,
    fps: int,
    amiga_w: int,
    amiga_h: int,
    scenes: list,
    texts_data: list,
    beat_interval: float,
    timeline: BeatTimeline,
    preview: bool,
    crt_filter: bool,
    effect_cache: dict,
    text_scrollers: dict | None = None,
    transition_state: dict | None = None,
    audio_analysis: object | None = None,
    amiga_palette: bool = True,
    transition_sec: float = 1.0,
) -> np.ndarray:
    scene = _find_scene(scenes, time_sec, beat_interval)

    if scene is None:
        base_arr = np.zeros((amiga_h, amiga_w, 3), dtype=np.uint8)
        current_effect = None
    else:
        _hashable_params = frozenset((k, tuple(v) if isinstance(v, list) else v) for k, v in (scene.params or {}).items())
        key = (scene.effect, _hashable_params)
        if key not in effect_cache:
            effect_cache[key] = build_effect(scene.effect, scene.params, fps, amiga_palette, audio_analysis)
        current_effect = effect_cache[key]
        img = current_effect.render_frame(time_sec, timeline)
        base_arr = np.array(img, dtype=np.uint8)

    if transition_state is not None and transition_state["active"]:
        alpha = transition_state["progress"]
        prev = transition_state["prev_frame"]
        base_arr = (prev.astype(np.float32) * (1.0 - alpha) + base_arr.astype(np.float32) * alpha).astype(np.uint8)
        transition_state["progress"] += 1.0 / transition_state["duration_frames"]
        if transition_state["progress"] >= 1.0:
            transition_state["active"] = False

    if text_scrollers is not None:
        for (start_sec, end_sec), scroller in text_scrollers.items():
            if start_sec <= time_sec < end_sec:
                text_img = scroller.render_frame(time_sec, timeline)
                text_arr = np.array(text_img, dtype=np.uint8)
                mask = np.any(text_arr > 10, axis=2)
                base_arr = base_arr.copy()
                base_arr[mask] = text_arr[mask]

    if preview:
        result = base_arr
    else:
        result = upscale_to_array(base_arr, crt_filter=crt_filter)

    next_time = time_sec + 1.0 / fps
    next_scene = _find_scene(scenes, next_time, beat_interval)
    if transition_state is not None and scene is not None and next_scene is not None and next_scene != scene:
        transition_state["active"] = True
        transition_state["progress"] = 0.0
        transition_state["duration_frames"] = max(1, int(transition_sec * fps))
        transition_state["prev_frame"] = base_arr.copy()

    return result


def _render_chunk(args: tuple) -> list[tuple[int, str]]:
    start, end, fps, amiga_w, amiga_h, scenes_data, texts_data, beat_interval, bpm, duration_sec, beat_times_list, output_dir, preview, crt_filter, audio_analysis_data, amiga_palette, transition_sec = args

    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

    from ..audio.analyzer import AudioAnalysis
    from ..audio.sync import BeatTimeline

    timeline = BeatTimeline(bpm=bpm, total_beats=len(beat_times_list), beat_times=np.array(beat_times_list), duration_sec=duration_sec)

    audio_analysis = None
    if audio_analysis_data is not None:
        aa = AudioAnalysis.__new__(AudioAnalysis)
        aa.y = None
        aa.sr = audio_analysis_data["sr"]
        aa.duration_sec = audio_analysis_data["duration_sec"]
        aa.bpm = audio_analysis_data["bpm"]
        aa.n_fft = audio_analysis_data["n_fft"]
        aa.hop_length = audio_analysis_data["hop_length"]
        aa._stft = np.array(audio_analysis_data["_stft"])
        aa._freqs = np.array(audio_analysis_data["_freqs"])
        aa._times = np.array(audio_analysis_data["_times"])
        aa.beat_times = np.array(audio_analysis_data["beat_times"])
        aa.beat_frames = np.array(audio_analysis_data["beat_frames"])
        aa.onset_times = np.array(audio_analysis_data["onset_times"])
        aa.onset_strength = np.array(audio_analysis_data["onset_strength"])
        audio_analysis = aa

    from .scene import SceneDef, TEXT_EFFECT_REGISTRY
    scenes = [SceneDef(**s) for s in scenes_data]

    text_scrollers = {}
    for t in texts_data:
        start_sec = t["start_beat"] * beat_interval
        end_sec = (t["start_beat"] + t["duration_beats"]) * beat_interval
        effect_cls = TEXT_EFFECT_REGISTRY.get(t["effect"])
        if effect_cls is not None:
            scroller = effect_cls(width=amiga_w, height=amiga_h, fps=fps, text=t["text"])
            text_scrollers[(start_sec, end_sec)] = scroller

    effect_cache: dict = {}
    transition_state: dict | None = None if preview else {"active": False, "progress": 0.0, "duration_frames": 1, "prev_frame": None}

    rendered: list[tuple[int, str]] = []
    for idx in range(start, end):
        path = os.path.join(output_dir, f"frame_{idx:06d}.png")
        if os.path.exists(path):
            rendered.append((idx, path))
            continue
        time_sec = idx / fps
        frame_arr = _render_single_frame(
            idx, time_sec, fps, amiga_w, amiga_h, scenes, texts_data,
            beat_interval, timeline, preview, crt_filter, effect_cache,
            text_scrollers, transition_state, audio_analysis,
            amiga_palette, transition_sec,
        )
        Image.fromarray(frame_arr).save(path)
        rendered.append((idx, path))

    return rendered


def render_demo(config: DemoConfig) -> str:
    print("Analyzing audio...")
    analysis = AudioAnalysis(config.audio)
    timeline = BeatTimeline.from_analysis(analysis)
    beat_interval = timeline.beat_times[1] - timeline.beat_times[0] if len(timeline.beat_times) > 1 else 0.5
    total_sec = timeline.duration_sec
    if config.max_duration_sec is not None:
        total_sec = min(total_sec, config.max_duration_sec)

    amiga_w, amiga_h = 640, 512
    fps = config.fps
    if config.preview:
        fps = min(fps, 30)
    total_frames = int(total_sec * fps)

    output_dir = os.path.splitext(config.output)[0] + "_frames"
    os.makedirs(output_dir, exist_ok=True)

    existing_frames: set[int] = set()
    if config.resume and os.path.isdir(output_dir):
        for fname in os.listdir(output_dir):
            m = re.match(r"frame_(\d+)\.png", fname)
            if m:
                existing_frames.add(int(m.group(1)))
        if existing_frames:
            print(f"Resuming: {len(existing_frames)}/{total_frames} frames already rendered")

    scenes_data = [
        {"effect": s.effect, "start_beat": s.start_beat, "duration_beats": s.duration_beats, "params": dict(s.params)}
        for s in config.scenes
    ]
    texts_data = [
        {"text": t.text, "start_beat": t.start_beat, "duration_beats": t.duration_beats, "effect": t.effect}
        for t in config.texts
    ]
    beat_times_list = timeline.beat_times.tolist()

    if config.workers > 1:
        existing_paths = [(idx, os.path.join(output_dir, f"frame_{idx:06d}.png")) for idx in sorted(existing_frames)]
        missing = [idx for idx in range(total_frames) if idx not in existing_frames]
        if not missing:
            all_frames = existing_paths
        else:
            num_workers = min(config.workers, len(missing))
            chunk_size = max(1, len(missing) // num_workers)
            chunks = []
            audio_analysis_data = None
            if hasattr(analysis, '_stft') and analysis._stft is not None:
                audio_analysis_data = {
                    "sr": analysis.sr,
                    "duration_sec": analysis.duration_sec,
                    "bpm": analysis.bpm,
                    "n_fft": analysis.n_fft,
                    "hop_length": analysis.hop_length,
                    "_stft": analysis._stft.tolist(),
                    "_freqs": analysis._freqs.tolist(),
                    "_times": analysis._times.tolist(),
                    "beat_times": analysis.beat_times.tolist(),
                    "beat_frames": analysis.beat_frames.tolist(),
                    "onset_times": analysis.onset_times.tolist(),
                    "onset_strength": analysis.onset_strength.tolist(),
                }
            for i in range(num_workers):
                chunk_indices = missing[i * chunk_size: (i + 1) * chunk_size] if i < num_workers - 1 else missing[i * chunk_size:]
                if not chunk_indices:
                    break
                s, e = chunk_indices[0], chunk_indices[-1] + 1
                chunks.append((s, e, fps, amiga_w, amiga_h, scenes_data, texts_data,
                               beat_interval, timeline.bpm, timeline.duration_sec,
                               beat_times_list, output_dir, config.preview, config.crt_filter,
                               audio_analysis_data, config.amiga_palette, config.transition_sec))

            print(f"Rendering {len(missing)} frames with {len(chunks)} workers...")
            all_frames: list[tuple[int, str]] = []
            with ProcessPoolExecutor(max_workers=num_workers) as pool:
                futures = [pool.submit(_render_chunk, c) for c in chunks]
                for f in tqdm(as_completed(futures), total=len(futures), desc="Chunks", unit="chunk"):
                    all_frames.extend(f.result())

            all_frames = existing_paths + all_frames
            all_frames.sort(key=lambda x: x[0])
    else:
        print("Rendering frames...")
        timeline_for_seq = timeline
        scenes_obj = config.scenes
        text_scrollers = {}
        for t in config.texts:
            start_sec = t.start_beat * beat_interval
            end_sec = (t.start_beat + t.duration_beats) * beat_interval
            effect_cls = TEXT_EFFECT_REGISTRY.get(t.effect)
            if effect_cls is not None:
                scroller = effect_cls(width=amiga_w, height=amiga_h, fps=fps, text=t.text)
                text_scrollers[(start_sec, end_sec)] = scroller

        effect_cache: dict = {}
        transition_state: dict = {"active": False, "progress": 0.0, "duration_frames": 1, "prev_frame": None}

        all_frames = [(idx, os.path.join(output_dir, f"frame_{idx:06d}.png")) for idx in sorted(existing_frames)]
        remaining = [idx for idx in range(total_frames) if idx not in existing_frames]
        for frame_idx in tqdm(remaining, desc="Rendering frames", unit="frame"):
            time_sec = frame_idx / fps
            frame_arr = _render_single_frame(
                frame_idx, time_sec, fps, amiga_w, amiga_h,
                scenes_obj, texts_data, beat_interval, timeline_for_seq,
                config.preview, config.crt_filter, effect_cache,
                text_scrollers, transition_state, analysis,
                config.amiga_palette, config.transition_sec,
            )
            path = os.path.join(output_dir, f"frame_{frame_idx:06d}.png")
            Image.fromarray(frame_arr).save(path)
            all_frames.append((frame_idx, path))

    print("Encoding video...")
    frame_paths = [p for _, p in all_frames]
    clip = ImageSequenceClip(frame_paths, fps=fps)
    audio = AudioFileClip(config.audio)
    final = clip.with_audio(audio)

    temp_audio = os.path.splitext(config.output)[0] + "_TEMP_MPY_wvf_snd.mp4"
    final.write_videofile(config.output, codec="libx264", audio_codec="aac", fps=fps)

    if os.path.exists(temp_audio):
        os.remove(temp_audio)

    if not config.resume:
        shutil.rmtree(output_dir, ignore_errors=True)
    else:
        print(f"Frames kept in: {output_dir}")

    return config.output
