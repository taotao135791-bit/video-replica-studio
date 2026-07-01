#!/usr/bin/env python3
"""Compute a motion profile for a single video.

The profile captures per-frame inter-frame activity, static segments, hard cuts,
and significant visual mutations.  It can be imported as a library (see
``analyze_motion``) or invoked from the command line.
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Optional

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

from _utils import (  # noqa: E402
    discover_ffmpeg,
    ffprobe_duration,
    ffprobe_fps,
    run,
)


def _frames_from_video(
    video: Path,
    out_dir: Path,
    ffmpeg: str,
    fps: float,
    scale: str,
    quality: int = 3,
) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    pattern = out_dir / "%05d.jpg"
    vf = f"fps={fps},scale={scale}"
    cmd = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(video),
        "-vf",
        vf,
        "-q:v",
        str(quality),
        "-pix_fmt",
        "yuvj420p",
        str(pattern),
    ]
    run(cmd, timeout=max(60, int(fps * 120)))
    return sorted(out_dir.glob("*.jpg"))


def _frame_activity(frames: list[Path]) -> list[float]:
    from PIL import Image

    activity: list[float] = [0.0]
    prev = None
    for path in frames:
        img = Image.open(path).convert("L")
        data = img.tobytes()
        if prev is None:
            prev = data
            continue
        # Mean absolute pixel difference normalised to [0, 1].
        diff_sum = sum(abs(a - b) for a, b in zip(prev, data))
        activity.append(diff_sum / (255.0 * len(data)))
        prev = data
    return activity


def _detect_static_segments(
    activity: list[float],
    threshold: float,
    fps: float,
) -> list[dict[str, Any]]:
    segments: list[dict[str, Any]] = []
    start_idx: Optional[int] = None
    for i, value in enumerate(activity):
        below = value < threshold
        if below and start_idx is None:
            start_idx = i
        elif not below and start_idx is not None:
            segments.append(
                {
                    "start_frame": start_idx,
                    "end_frame": i - 1,
                    "start_time": round(start_idx / fps, 3),
                    "end_time": round((i - 1) / fps, 3),
                    "mean_activity": round(sum(activity[start_idx:i]) / (i - start_idx), 5),
                }
            )
            start_idx = None
    if start_idx is not None:
        n = len(activity)
        segments.append(
            {
                "start_frame": start_idx,
                "end_frame": n - 1,
                "start_time": round(start_idx / fps, 3),
                "end_time": round((n - 1) / fps, 3),
                "mean_activity": round(sum(activity[start_idx:]) / (n - start_idx), 5),
            }
        )
    return segments


def _detect_hard_cuts(
    activity: list[float],
    threshold: float,
    fps: float,
) -> list[dict[str, Any]]:
    cuts: list[dict[str, Any]] = []
    for i in range(1, len(activity) - 1):
        if activity[i] >= threshold and activity[i] >= activity[i - 1] and activity[i] >= activity[i + 1]:
            cuts.append(
                {
                    "frame": i,
                    "time": round(i / fps, 3),
                    "activity": round(activity[i], 5),
                }
            )
    return cuts


def _detect_mutations(
    activity: list[float],
    threshold: float,
    hard_cuts: list[dict[str, Any]],
    fps: float,
) -> list[dict[str, Any]]:
    """Detect significant non-cut activity bursts."""
    cut_frames = {c["frame"] for c in hard_cuts}
    mutations: list[dict[str, Any]] = []
    start_idx: Optional[int] = None
    peak_idx = -1
    for i, value in enumerate(activity):
        in_burst = value >= threshold and i not in cut_frames
        if in_burst and start_idx is None:
            start_idx = i
            peak_idx = i
        elif in_burst and start_idx is not None:
            if value > activity[peak_idx]:
                peak_idx = i
        elif start_idx is not None:
            end_idx = i - 1
            mutations.append(
                {
                    "start_frame": start_idx,
                    "end_frame": end_idx,
                    "start_time": round(start_idx / fps, 3),
                    "end_time": round(end_idx / fps, 3),
                    "peak_frame": peak_idx,
                    "peak_time": round(peak_idx / fps, 3),
                    "peak_activity": round(activity[peak_idx], 5),
                    "mean_activity": round(sum(activity[start_idx : end_idx + 1]) / (end_idx - start_idx + 1), 5),
                }
            )
            start_idx = None
            peak_idx = -1
    return mutations


def analyze_motion(
    video: Path,
    out_json: Optional[Path] = None,
    fps: Optional[float] = None,
    scale: str = "320:180",
    static_threshold: float = 0.015,
    hard_cut_threshold: float = 0.35,
    mutation_threshold: float = 0.08,
    workdir: Optional[Path] = None,
    keep_frames: bool = False,
) -> dict[str, Any]:
    """Build a motion profile for ``video``.

    Args:
        video: input video path.
        out_json: optional path to write the JSON report.
        fps: sampling frame rate.  Defaults to the source frame rate capped at 30.
        scale: ffmpeg scale expression for the working frames.
        static_threshold: activity level below which frames are considered static.
        hard_cut_threshold: activity peak level considered a hard cut.
        mutation_threshold: activity level considered a significant visual change.
        workdir: directory for temporary extracted frames.
        keep_frames: keep the temporary frame directory after analysis.

    Returns:
        The profile dictionary.
    """
    ffmpeg, ffprobe = discover_ffmpeg()
    duration = ffprobe_duration(video, ffprobe)
    source_fps = ffprobe_fps(video, ffprobe)

    if fps is None:
        if source_fps:
            fps = min(max(source_fps, 5.0), 30.0)
        else:
            fps = 10.0

    tmp = workdir is None
    frame_dir = Path(tempfile.mkdtemp(prefix="motion_profile_")) if workdir is None else workdir
    try:
        frames = _frames_from_video(video, frame_dir, ffmpeg, fps, scale)
        if not frames:
            raise RuntimeError(f"No frames extracted from {video}")
        activity = _frame_activity(frames)
        frame_count = len(activity)

        static_segments = _detect_static_segments(activity, static_threshold, fps)
        hard_cuts = _detect_hard_cuts(activity, hard_cut_threshold, fps)
        mutations = _detect_mutations(activity, mutation_threshold, hard_cuts, fps)

        timestamps = [round(i / fps, 3) for i in range(frame_count)]
        profile = {
            "video": str(video.resolve()),
            "duration": round(duration, 3),
            "fps": round(fps, 3),
            "scale": scale,
            "frame_count": frame_count,
            "thresholds": {
                "static": static_threshold,
                "hard_cut": hard_cut_threshold,
                "mutation": mutation_threshold,
            },
            "timestamps": timestamps,
            "activity": [round(v, 5) for v in activity],
            "static_segments": static_segments,
            "hard_cuts": hard_cuts,
            "mutations": mutations,
        }

        if out_json:
            out_json = out_json.expanduser().resolve()
            out_json.parent.mkdir(parents=True, exist_ok=True)
            out_json.write_text(json.dumps(profile, indent=2), encoding="utf-8")

        return profile
    finally:
        if tmp and not keep_frames:
            shutil.rmtree(frame_dir, ignore_errors=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute a motion profile for a video."
    )
    parser.add_argument("video", type=Path, help="Input video.")
    parser.add_argument(
        "--out",
        type=Path,
        help="Output JSON file. If omitted, the profile is printed to stdout.",
    )
    parser.add_argument(
        "--fps",
        type=float,
        help="Sampling frame rate (default: source fps capped at 30).",
    )
    parser.add_argument(
        "--scale",
        default="320:180",
        help="ffmpeg scale expression for working frames (default: 320:180).",
    )
    parser.add_argument(
        "--static-threshold",
        type=float,
        default=0.015,
        help="Activity level below which a segment is considered static.",
    )
    parser.add_argument(
        "--hard-cut-threshold",
        type=float,
        default=0.35,
        help="Activity peak level considered a hard cut.",
    )
    parser.add_argument(
        "--mutation-threshold",
        type=float,
        default=0.08,
        help="Activity level considered a significant visual mutation.",
    )
    parser.add_argument(
        "--keep-frames",
        action="store_true",
        help="Keep the temporary extracted frames for inspection.",
    )
    args = parser.parse_args()

    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        discover_ffmpeg()  # trigger a clear error message if missing

    profile = analyze_motion(
        video=args.video.expanduser().resolve(),
        out_json=args.out,
        fps=args.fps,
        scale=args.scale,
        static_threshold=args.static_threshold,
        hard_cut_threshold=args.hard_cut_threshold,
        mutation_threshold=args.mutation_threshold,
        keep_frames=args.keep_frames,
    )

    if not args.out:
        print(json.dumps(profile, indent=2))
    else:
        print(json.dumps({"out": str(args.out), "frame_count": profile["frame_count"]}, indent=2))


if __name__ == "__main__":
    main()
