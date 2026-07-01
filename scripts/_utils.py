#!/usr/bin/env python3
"""Shared utilities for the reference-video QC pipeline.

This module is imported by the standalone scripts in the same directory.  It is
not a public API and may change as the pipeline evolves.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple


def _try_add_static_ffmpeg() -> bool:
    """Add the static_ffmpeg package binaries to PATH if available."""
    try:
        import static_ffmpeg  # type: ignore

        static_ffmpeg.add_paths()
        return True
    except Exception:
        return False


def _imageio_ffmpeg() -> Optional[Path]:
    """Return the imageio-ffmpeg bundled binary path, if installed."""
    try:
        import imageio_ffmpeg  # type: ignore

        return Path(imageio_ffmpeg.get_ffmpeg_exe())
    except Exception:
        return None


def _common_ffmpeg_paths() -> list[Path]:
    """Platform-aware fallback locations for bundled ffmpeg binaries."""
    candidates: list[Path] = []
    if sys.platform == "darwin":
        candidates += [
            Path("/Applications/Audio Jam.app/Contents/lib/darwin/arm64/ffmpeg"),
            Path("/Applications/Audio Jam.app/Contents/lib/darwin/x64/ffmpeg"),
            Path("/Applications/VideoFusion-macOS.app/Contents/Resources/ffmpeg"),
        ]
    return [p for p in candidates if p.exists()]


def _common_ffprobe_paths(ffmpeg_path: Path) -> list[Path]:
    """Return likely ffprobe paths next to a discovered ffmpeg binary."""
    candidates = [
        ffmpeg_path.parent / "ffprobe",
        ffmpeg_path.parent / "ffprobe.exe",
    ]
    if sys.platform == "darwin":
        candidates += [
            Path("/Applications/Audio Jam.app/Contents/lib/darwin/arm64/ffprobe"),
            Path("/Applications/Audio Jam.app/Contents/lib/darwin/x64/ffprobe"),
            Path("/Applications/VideoFusion-macOS.app/Contents/Resources/ffprobe"),
        ]
    return [p for p in candidates if p.exists()]


def discover_ffmpeg() -> Tuple[str, str]:
    """Return (ffmpeg, ffprobe) executable paths.

    Resolution order:
      1. ``FFMPEG_BIN`` / ``FFPROBE_BIN`` environment variables.
      2. ``shutil.which`` on the current ``PATH``.
      3. The ``static_ffmpeg`` Python package, if installed.
      4. The ``imageio-ffmpeg`` Python package, if installed (ffmpeg only).
      5. A short list of common bundled-app fallback paths.

    Raises:
        SystemExit: if either binary cannot be found.
    """
    ffmpeg: Optional[str] = os.environ.get("FFMPEG_BIN")
    ffprobe: Optional[str] = os.environ.get("FFPROBE_BIN")

    # 1. Environment variables.
    if ffmpeg and ffprobe and shutil.which(ffmpeg) and shutil.which(ffprobe):
        return str(Path(ffmpeg).resolve()), str(Path(ffprobe).resolve())

    # 2. PATH lookup.
    if not ffmpeg:
        ffmpeg = shutil.which("ffmpeg")
    if not ffprobe:
        ffprobe = shutil.which("ffprobe")

    # 3. static_ffmpeg adds both binaries to PATH.
    if not ffmpeg or not ffprobe:
        _try_add_static_ffmpeg()
        if not ffmpeg:
            ffmpeg = shutil.which("ffmpeg")
        if not ffprobe:
            ffprobe = shutil.which("ffprobe")

    # 4. imageio-ffmpeg only ships ffmpeg; try to locate ffprobe next to it.
    if not ffmpeg:
        io_ffmpeg = _imageio_ffmpeg()
        if io_ffmpeg:
            ffmpeg = str(io_ffmpeg)
            if not ffprobe:
                for candidate in _common_ffprobe_paths(io_ffmpeg):
                    ffprobe = str(candidate)
                    break

    # 5. Platform-aware fallback bundles.
    if not ffmpeg:
        for candidate in _common_ffmpeg_paths():
            ffmpeg = str(candidate)
            if not ffprobe:
                for p in _common_ffprobe_paths(candidate):
                    ffprobe = str(p)
                    break
            break

    if not ffmpeg or not ffprobe:
        raise SystemExit(
            "ffmpeg and ffprobe are required. "
            "Install them on PATH or set FFMPEG_BIN / FFPROBE_BIN."
        )

    return str(Path(ffmpeg).resolve()), str(Path(ffprobe).resolve())


def run(
    cmd: list[str], check: bool = True, timeout: Optional[int] = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd, check=check, text=True, capture_output=True, timeout=timeout
    )


def ffprobe_duration(video: Path, ffprobe: str) -> float:
    out = run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(video),
        ]
    )
    return float(out.stdout.strip())


def ffprobe_fps(video: Path, ffprobe: str) -> Optional[float]:
    """Return the first video stream frame rate, or None if unavailable."""
    try:
        result = run(
            [
                ffprobe,
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=r_frame_rate",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(video),
            ]
        )
        value = result.stdout.strip()
        if "/" in value:
            num, den = value.split("/")
            return float(num) / float(den)
        return float(value)
    except Exception:
        return None


def get_font(size: int = 22):
    """Load a TrueType font if one is available, otherwise PIL default."""
    from PIL import ImageFont

    candidates: list[Path] = []
    if sys.platform == "darwin":
        candidates = [
            Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
            Path("/Library/Fonts/Arial.ttf"),
            Path("/System/Library/Fonts/Helvetica.ttc"),
            Path("/System/Library/Fonts/HelveticaNeue.ttc"),
        ]
    elif sys.platform == "win32":
        candidates = [
            Path.home() / "AppData/Local/Microsoft/Windows/Fonts/Arial.ttf",
            Path("C:/Windows/Fonts/arial.ttf"),
            Path("C:/Windows/Fonts/segoeui.ttf"),
            Path("C:/Windows/Fonts/calibri.ttf"),
        ]
    else:
        candidates = [
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
            Path("/usr/share/fonts/truetype/freefont/FreeSans.ttf"),
            Path("/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"),
        ]

    for path in candidates:
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size)
            except Exception:
                pass
    return ImageFont.load_default()
