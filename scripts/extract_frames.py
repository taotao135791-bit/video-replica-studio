#!/usr/bin/env python3
"""Extract fixed-interval video frames and optional contact sheets.

This script replaces the earlier ``extract_halfsec_frames.py`` and keeps the
same command-line interface while adding scene-aware dense sampling, preview
mode, and optional motion profiling.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Optional

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

from _utils import discover_ffmpeg, ffprobe_duration, get_font, run  # noqa: E402
import motion_profile  # noqa: E402


def safe_time(t: float) -> str:
    return f"{t:.3f}".replace(".", "_")


def extract_frame(
    video: Path,
    out: Path,
    t: float,
    scale: str,
    quality: int,
    ffmpeg: str,
) -> None:
    """Extract a single frame with the requested scale and JPEG quality."""
    vf = f"scale={scale}" if scale else "null"
    # Map Pillow-style quality (0-100) to ffmpeg q:v (2-31, lower is better).
    qv = max(2, min(31, round((100 - quality) / 3)))
    cmd = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-ss",
        f"{t:.3f}",
        "-i",
        str(video),
        "-frames:v",
        "1",
        "-vf",
        vf,
        "-q:v",
        str(qv),
        str(out),
    ]
    run(cmd)


def make_contact_sheet(
    frame_paths: list[Path],
    out: Path,
    cols: int,
    title: str,
) -> bool:
    from PIL import Image, ImageDraw, ImageFont

    if not frame_paths:
        return False

    try:
        font = get_font(22)
        small = get_font(18)
    except Exception:
        font = ImageFont.load_default()
        small = ImageFont.load_default()

    labeled = []
    for path in frame_paths:
        img = Image.open(path).convert("RGB")
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        label = path.stem.replace("frame_t", "").replace("_", ".") + "s"
        d.rectangle((0, 0, img.width, 34), fill=(0, 0, 0, 178))
        d.text((12, 6), label, fill=(255, 255, 255), font=font)
        labeled.append(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"))

    w, h = labeled[0].size
    rows = math.ceil(len(labeled) / cols)
    pad = 18
    header = 46
    canvas = Image.new(
        "RGB",
        (cols * w + (cols + 1) * pad, rows * h + (rows + 1) * pad + header),
        (12, 12, 12),
    )
    d = ImageDraw.Draw(canvas)
    d.text((pad, 12), title, fill=(255, 255, 255), font=small)
    for idx, img in enumerate(labeled):
        x = pad + (idx % cols) * (w + pad)
        y = header + pad + (idx // cols) * (h + pad)
        canvas.paste(img, (x, y))
    canvas.save(out, quality=88)
    return True


def parse_explicit_times(value: str) -> list[float]:
    times = []
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        times.append(round(float(item), 3))
    return times


def build_times(start: float, end: float, interval: float) -> list[float]:
    times = []
    current = start
    while current <= end + 0.001:
        times.append(round(current, 3))
        current += interval
    return times


def detect_scenes(
    video: Path,
    ffmpeg: str,
    threshold: float,
) -> list[dict[str, float]]:
    """Detect scene transitions using ffmpeg's scene filter."""
    scenes: list[dict[str, float]] = []
    with tempfile.NamedTemporaryFile(
        mode="w+", suffix=".txt", prefix="scenes_", delete=True
    ) as meta_file:
        vf = f"select=gt(scene\\,{threshold}),metadata=print:file={meta_file.name}"
        cmd = [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(video),
            "-vf",
            vf,
            "-an",
            "-f",
            "null",
            "-",
        ]
        run(cmd)
        meta_file.seek(0)
        text = meta_file.read()

    current: dict[str, float] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            if current:
                scenes.append(current)
                current = {}
            continue
        pts_match = re.search(r"pts_time:(\S+)", line)
        if pts_match:
            current["time"] = float(pts_match.group(1))
        score_match = re.search(r"lavfi\.scene_score=(\S+)", line)
        if score_match:
            current["score"] = float(score_match.group(1))
    if current:
        scenes.append(current)
    return scenes


def dense_scene_samples(
    scenes: list[dict[str, float]],
    radius: float,
    step: float,
    start: float,
    end: float,
) -> list[float]:
    times = []
    for scene in scenes:
        t = scene["time"]
        offset = -radius
        while offset <= radius + 0.0001:
            sample = round(t + offset, 3)
            if start - 0.001 <= sample <= end + 0.001:
                times.append(sample)
            offset += step
    return times


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract fixed-interval frames from a video."
    )
    parser.add_argument("video", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--interval", type=float, default=0.5)
    parser.add_argument("--start", type=float, default=0.0)
    parser.add_argument("--end", type=float, help="End timestamp in seconds.")
    parser.add_argument(
        "--times",
        help="Comma-separated explicit timestamps, overriding interval sampling.",
    )
    parser.add_argument(
        "--scale",
        default=None,
        help="ffmpeg scale expression (default: 480:270, preview: 320:180).",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=None,
        help="JPEG quality 0-100 (default: 88, preview: 60).",
    )
    parser.add_argument(
        "--contact", action="store_true", help="Create labeled contact sheets."
    )
    parser.add_argument("--cols", type=int, default=3)
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Fast, low-resolution output for motion verification.",
    )
    parser.add_argument(
        "--detect-scenes",
        action="store_true",
        help="Detect scene transitions and sample densely around each one.",
    )
    parser.add_argument(
        "--scene-threshold", type=float, default=0.3, help="Scene detection threshold."
    )
    parser.add_argument(
        "--scene-radius",
        type=float,
        default=0.3,
        help="Seconds around each scene change to sample densely.",
    )
    parser.add_argument(
        "--scene-step",
        type=float,
        default=0.05,
        help="Dense sampling step around scene changes.",
    )
    parser.add_argument(
        "--motion-profile",
        action="store_true",
        help="Write motion-profile.json in the output directory.",
    )
    args = parser.parse_args()

    ffmpeg, ffprobe = discover_ffmpeg()

    if args.interval <= 0:
        raise SystemExit("--interval must be positive")
    if args.scene_step <= 0:
        raise SystemExit("--scene-step must be positive")

    video = args.video.expanduser().resolve()
    out = args.out.expanduser().resolve()
    frames_dir = out / "frames"
    contact_dir = out / "contact"
    frames_dir.mkdir(parents=True, exist_ok=True)
    contact_dir.mkdir(parents=True, exist_ok=True)

    scale = args.scale or ("320:180" if args.preview else "480:270")
    quality = args.quality if args.quality is not None else (60 if args.preview else 88)

    dur = ffprobe_duration(video, ffprobe)
    start = max(0.0, args.start)
    end = min(args.end if args.end is not None else dur, dur)
    if start > end:
        raise SystemExit("--start must be less than or equal to --end")

    if args.times:
        base_times = [t for t in parse_explicit_times(args.times) if 0 <= t <= dur + 0.001]
    else:
        base_times = build_times(start, end, args.interval)

    scenes: list[dict[str, float]] = []
    if args.detect_scenes:
        scenes = detect_scenes(video, ffmpeg, args.scene_threshold)
        dense = dense_scene_samples(scenes, args.scene_radius, args.scene_step, start, end)
        times = sorted({round(t, 3) for t in base_times + dense})
    else:
        times = base_times

    frames = []
    for t in times:
        path = frames_dir / f"frame_t{safe_time(t)}.jpg"
        extract_frame(video, path, t, scale, quality, ffmpeg)
        frames.append(path)

    manifest: dict[str, Any] = {
        "video": str(video),
        "duration": dur,
        "start": start,
        "end": end,
        "interval": args.interval,
        "explicit_times": bool(args.times),
        "scale": scale,
        "quality": quality,
        "preview": args.preview,
        "frame_count": len(frames),
        "frames": [str(p) for p in frames],
    }
    if args.detect_scenes:
        manifest["scene_threshold"] = args.scene_threshold
        manifest["scene_radius"] = args.scene_radius
        manifest["scene_step"] = args.scene_step
        manifest["scene_transitions"] = scenes
        (out / "scene-transitions.json").write_text(
            json.dumps(
                {
                    "threshold": args.scene_threshold,
                    "transitions": scenes,
                    "dense_radius": args.scene_radius,
                    "dense_step": args.scene_step,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    (out / "frames-manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )

    if args.contact:
        per_sheet = args.cols * 6
        for sheet_start in range(0, len(frames), per_sheet):
            chunk = frames[sheet_start : sheet_start + per_sheet]
            sheet = contact_dir / f"contact_{sheet_start // per_sheet + 1:02d}.jpg"
            make_contact_sheet(
                chunk,
                sheet,
                args.cols,
                f"{video.name} frames {sheet_start + 1}-{sheet_start + len(chunk)}",
            )

    if args.motion_profile:
        motion_profile.analyze_motion(
            video=video,
            out_json=out / "motion-profile.json",
        )

    summary = {
        "out": str(out),
        "frames": len(frames),
        "duration": dur,
        "scale": scale,
        "quality": quality,
        "scenes_detected": len(scenes) if args.detect_scenes else None,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
