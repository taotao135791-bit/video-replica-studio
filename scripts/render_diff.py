#!/usr/bin/env python3
"""Generate side-by-side and pixel-difference heatmaps for two videos.

Example:
    python3 scripts/render_diff.py reference.mp4 candidate.mp4 analysis/diff
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

from _utils import discover_ffmpeg, get_font  # noqa: E402

_FFMPEG = "ffmpeg"
_FFPROBE = "ffprobe"


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=check, text=True, capture_output=True)


def duration(video: Path) -> float:
    out = run(
        [
            _FFPROBE,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(video),
        ]
    ).stdout.strip()
    return float(out)


def safe_time(t: float) -> str:
    return f"{t:.3f}".replace(".", "_")


def extract_frame(video: Path, out: Path, t: float, scale: str) -> None:
    vf = f"scale={scale}" if scale else "null"
    run(
        [
            _FFMPEG,
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
            str(out),
        ]
    )


def heat_palette() -> list[int]:
    """Return a 768-byte RGB palette: black -> blue -> cyan -> green -> yellow -> red."""
    palette: list[int] = []
    stops = [
        (0, (0, 0, 0)),
        (51, (0, 0, 255)),
        (102, (0, 255, 255)),
        (153, (0, 255, 0)),
        (204, (255, 255, 0)),
        (255, (255, 0, 0)),
    ]
    for i in range(len(stops) - 1):
        v0, c0 = stops[i]
        v1, c1 = stops[i + 1]
        for v in range(v0, v1 + 1):
            ratio = (v - v0) / (v1 - v0) if v1 != v0 else 0
            r = int(round(c0[0] + (c1[0] - c0[0]) * ratio))
            g = int(round(c0[1] + (c1[1] - c0[1]) * ratio))
            b = int(round(c0[2] + (c1[2] - c0[2]) * ratio))
            palette.extend([r, g, b])
    # Fill any remainder (should already be 256 entries)
    while len(palette) < 768:
        palette.extend([255, 0, 0])
    return palette[:768]


def ensure_size(img, target):
    from PIL import Image

    if img.size == target.size:
        return img
    return img.resize(target.size, Image.Resampling.LANCZOS)


def make_heatmap(ref_path: Path, cand_path: Path, out_path: Path) -> float:
    from PIL import Image, ImageChops

    ref = Image.open(ref_path).convert("RGB")
    cand = ensure_size(Image.open(cand_path).convert("RGB"), ref)
    diff = ImageChops.difference(ref, cand).convert("L")

    heat = Image.new("P", diff.size)
    heat.putpalette(heat_palette())
    heat.paste(diff)
    heat.convert("RGB").save(out_path, quality=92)

    hist = diff.histogram()
    total = sum(hist)
    if total == 0:
        return 0.0
    mae = sum(i * hist[i] for i in range(256)) / total
    return mae


def side_by_side(ref_path: Path, cand_path: Path, out_path: Path, label: str = "") -> None:
    from PIL import Image, ImageDraw, ImageFont

    ref = Image.open(ref_path).convert("RGB")
    cand = ensure_size(Image.open(cand_path).convert("RGB"), ref)
    font = _load_font(20)
    header = 34 if label else 0
    canvas = Image.new("RGB", (ref.width * 2, ref.height + header), (12, 12, 12))
    if label:
        d = ImageDraw.Draw(canvas)
        d.text((12, 8), label, fill=(255, 255, 255), font=font)
    canvas.paste(ref, (0, header))
    canvas.paste(cand, (ref.width, header))
    canvas.save(out_path, quality=92)


def _load_font(size: int):
    return get_font(size)


def make_contact_sheet(images: list[Image.Image], labels: list[str], out_path: Path, cols: int, title: str) -> bool:
    from PIL import Image, ImageDraw

    if not images:
        return False
    font = _load_font(22)
    small = _load_font(18)
    labeled: list[Image.Image] = []
    for img, label in zip(images, labels):
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        d.rectangle((0, 0, img.width, 34), fill=(0, 0, 0, 178))
        d.text((12, 6), label, fill=(255, 255, 255), font=font)
        labeled.append(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"))

    w, h = labeled[0].size
    rows = math.ceil(len(labeled) / cols)
    pad = 18
    header = 46
    canvas = Image.new("RGB", (cols * w + (cols + 1) * pad, rows * h + (rows + 1) * pad + header), (12, 12, 12))
    d = ImageDraw.Draw(canvas)
    d.text((pad, 12), title, fill=(255, 255, 255), font=small)
    for idx, img in enumerate(labeled):
        x = pad + (idx % cols) * (w + pad)
        y = header + pad + (idx // cols) * (h + pad)
        canvas.paste(img, (x, y))
    canvas.save(out_path, quality=88)
    return True


def build_times(start: float, end: float, interval: float) -> list[float]:
    times: list[float] = []
    current = start
    while current < end - 0.001:
        times.append(round(current, 3))
        current += interval
    return times


def _timestamp_from_path(path: Path) -> float:
    # e.g. sbs_t0_000.jpg -> 0.000, heat_t10_000.jpg -> 10.000
    stem = path.stem
    if "_t" in stem:
        time_part = stem.split("_t")[-1]
        return float(time_part.replace("_", "."))
    return 0.0


def _contact_sheets(image_dir: Path, out_dir: Path, prefix: str, cols: int, title_prefix: str) -> list[Path]:
    from PIL import Image

    files = sorted(
        (p for p in image_dir.iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png")),
        key=_timestamp_from_path,
    )
    sheets: list[Path] = []
    per_sheet = cols * 6
    for start in range(0, len(files), per_sheet):
        chunk = files[start : start + per_sheet]
        images = [Image.open(p).convert("RGB") for p in chunk]
        labels = [p.stem.replace("t", "").replace("_", ".") + "s" for p in chunk]
        sheet_path = out_dir / f"{prefix}_{start // per_sheet + 1:02d}.jpg"
        make_contact_sheet(images, labels, sheet_path, cols, f"{title_prefix} frames {start + 1}-{start + len(chunk)}")
        sheets.append(sheet_path)
    return sheets


def run_render_diff(
    reference: Path,
    candidate: Path,
    outdir: Path,
    interval: float = 0.5,
    scale: str = "480:270",
    cols: int = 3,
) -> dict:
    global _FFMPEG, _FFPROBE
    _FFMPEG, _FFPROBE = discover_ffmpeg()

    outdir = outdir.expanduser().resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    dur = min(duration(reference), duration(candidate))
    times = build_times(0.0, dur, interval)

    ref_dir = outdir / "frames_ref"
    cand_dir = outdir / "frames_candidate"
    sbs_dir = outdir / "side_by_side"
    heat_dir = outdir / "heatmaps"
    for d in (ref_dir, cand_dir, sbs_dir, heat_dir):
        d.mkdir(parents=True, exist_ok=True)

    entries: list[dict] = []
    for t in times:
        tag = safe_time(t)
        ref_frame = ref_dir / f"frame_t{tag}.jpg"
        cand_frame = cand_dir / f"frame_t{tag}.jpg"
        extract_frame(reference, ref_frame, t, scale)
        extract_frame(candidate, cand_frame, t, scale)

        sbs_path = sbs_dir / f"sbs_t{tag}.jpg"
        heat_path = heat_dir / f"heat_t{tag}.jpg"
        side_by_side(ref_frame, cand_frame, sbs_path, label=f"{t:.3f}s")
        mae = make_heatmap(ref_frame, cand_frame, heat_path)

        entries.append(
            {
                "timestamp": t,
                "mean_absolute_difference": round(mae, 4),
                "side_by_side": str(sbs_path.relative_to(outdir)),
                "heatmap": str(heat_path.relative_to(outdir)),
            }
        )

    contact_dir = outdir / "contact_sheets"
    contact_dir.mkdir(parents=True, exist_ok=True)
    sbs_sheets = _contact_sheets(sbs_dir, contact_dir, "side_by_side", cols, "Side-by-side")
    heat_sheets = _contact_sheets(heat_dir, contact_dir, "heatmap", cols, "Heatmap")

    manifest = {
        "reference": str(reference),
        "candidate": str(candidate),
        "interval": interval,
        "scale": scale,
        "duration": dur,
        "timestamps": entries,
        "contact_sheets": {
            "side_by_side": [str(p.relative_to(outdir)) for p in sbs_sheets],
            "heatmap": [str(p.relative_to(outdir)) for p in heat_sheets],
        },
    }
    (outdir / "diff-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Render side-by-side and heatmap diff contact sheets for two videos.")
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--interval", type=float, default=0.5)
    parser.add_argument("--scale", default="480:270")
    parser.add_argument("--cols", type=int, default=3)
    args = parser.parse_args()

    for label, path in (("Reference", args.reference), ("Candidate", args.candidate)):
        if not path.expanduser().resolve().exists():
            raise SystemExit(f"{label} not found: {path}")

    global _FFMPEG, _FFPROBE
    _FFMPEG, _FFPROBE = discover_ffmpeg()

    try:
        from PIL import Image  # noqa: F401
    except Exception as exc:
        raise SystemExit(f"Pillow is required: {exc}")

    manifest = run_render_diff(args.reference, args.candidate, args.output, args.interval, args.scale, args.cols)
    print(json.dumps({"out": str(args.output.expanduser().resolve()), "frames": len(manifest["timestamps"])}, indent=2))


if __name__ == "__main__":
    main()
