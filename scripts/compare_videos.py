#!/usr/bin/env python3
"""Compare a reference and candidate video with hashes, PSNR/SSIM, and mismatch classification.

Cross-platform replacement for the earlier version: byte-exact comparison now
uses the already-computed SHA-256 hashes instead of the Unix ``cmp`` utility.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

from _utils import discover_ffmpeg, ffprobe_duration, run  # noqa: E402
from render_diff import run_render_diff  # noqa: E402
from component_crop import run_component_crop  # noqa: E402


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ffprobe_info(path: Path, ffprobe: str) -> dict:
    result = run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration,size,bit_rate",
            "-show_entries",
            "stream=index,codec_type,codec_name,width,height,r_frame_rate,channels",
            "-of",
            "json",
            str(path),
        ]
    )
    return json.loads(result.stdout)


def metric(
    reference: Path,
    candidate: Path,
    outdir: Path,
    name: str,
    ffmpeg: str,
) -> str:
    log = outdir / f"{name}.log"
    expr = f"[0:v][1:v]{name}=stats_file={log}"
    result = run(
        [
            ffmpeg,
            "-hide_banner",
            "-nostats",
            "-i",
            str(reference),
            "-i",
            str(candidate),
            "-lavfi",
            expr,
            "-f",
            "null",
            "-",
        ],
        check=False,
        timeout=1800,
    )
    combined = (result.stderr or "") + "\n" + (result.stdout or "")
    lines = [
        line.strip()
        for line in combined.splitlines()
        if name.upper() in line or f"Parsed_{name}" in line
    ]
    return lines[-1] if lines else combined.strip().splitlines()[-1]


def safe_time(t: float) -> str:
    return f"{t:.3f}".replace(".", "_")


def build_times(start: float, end: float, interval: float) -> list[float]:
    times: list[float] = []
    current = start
    while current < end - 0.001:
        times.append(round(current, 3))
        current += interval
    return times


def extract_frame(
    video: Path,
    out: Path,
    t: float,
    scale: str,
    ffmpeg: str,
) -> None:
    vf = f"scale={scale}" if scale else "null"
    run(
        [
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
            str(out),
        ]
    )


def extract_pair_frames(
    reference: Path,
    candidate: Path,
    outdir: Path,
    interval: float,
    scale: str,
    ffmpeg: str,
    ffprobe: str,
) -> tuple[list[float], list[Path], list[Path]]:
    ref_dir = outdir / "frames_ref"
    cand_dir = outdir / "frames_candidate"
    for d in (ref_dir, cand_dir):
        d.mkdir(parents=True, exist_ok=True)

    dur = min(ffprobe_duration(reference, ffprobe), ffprobe_duration(candidate, ffprobe))
    times = build_times(0.0, dur, interval)
    ref_paths: list[Path] = []
    cand_paths: list[Path] = []
    for t in times:
        tag = safe_time(t)
        rp = ref_dir / f"frame_t{tag}.jpg"
        cp = cand_dir / f"frame_t{tag}.jpg"
        extract_frame(reference, rp, t, scale, ffmpeg)
        extract_frame(candidate, cp, t, scale, ffmpeg)
        ref_paths.append(rp)
        cand_paths.append(cp)
    return times, ref_paths, cand_paths


def load_grayscale(path: Path):
    from PIL import Image

    return Image.open(path).convert("L")


def frame_mae(a, b) -> float:
    """Mean absolute pixel difference between two grayscale PIL images."""
    from PIL import ImageChops

    diff = ImageChops.difference(a, b)
    hist = diff.histogram()
    total = sum(hist)
    if total == 0:
        return 0.0
    return sum(i * hist[i] for i in range(256)) / total


def edge_std(img) -> float:
    """Standard deviation of edge-filtered grayscale image (proxy for texture/detail)."""
    from PIL import ImageFilter

    edges = img.filter(ImageFilter.FIND_EDGES)
    hist = edges.histogram()
    total = sum(hist)
    if total == 0:
        return 0.0
    mean = sum(i * hist[i] for i in range(256)) / total
    var = sum(hist[i] * ((i - mean) ** 2) for i in range(256)) / total
    return math.sqrt(var)


def normalized_cross_correlation(a: list[float], b: list[float], max_lag: int):
    """Return (best_lag, best_corr) using Pearson correlation over lags."""
    n = len(a)
    if n != len(b) or n < 2:
        return 0, 0.0

    def _corr(arr1: list[float], arr2: list[float]) -> float:
        m1 = sum(arr1) / len(arr1)
        m2 = sum(arr2) / len(arr2)
        num = sum((x - m1) * (y - m2) for x, y in zip(arr1, arr2))
        den = math.sqrt(sum((x - m1) ** 2 for x in arr1) * sum((y - m2) ** 2 for y in arr2))
        return num / den if den > 1e-12 else 0.0

    best_lag = 0
    best_corr = _corr(a, b)
    for lag in range(-max_lag, max_lag + 1):
        if lag == 0:
            continue
        if lag < 0:
            seg_a = a[-lag:]
            seg_b = b[:lag]
        else:
            seg_a = a[:-lag]
            seg_b = b[lag:]
        if len(seg_a) < 2:
            continue
        c = _corr(seg_a, seg_b)
        if c > best_corr:
            best_corr = c
            best_lag = lag
    return best_lag, best_corr


def detect_transitions(diffs: list[float], times: list[float], threshold: float) -> list[float]:
    """Simple peak detection on frame-to-frame differences."""
    transitions: list[float] = []
    if len(diffs) < 3:
        return transitions
    non_zero = [d for d in diffs if d > 0]
    med = sorted(non_zero)[len(non_zero) // 2] if non_zero else 0.0
    scene_thr = max(threshold, med * 3)
    for i in range(1, len(diffs) - 1):
        if diffs[i] > scene_thr and diffs[i] > diffs[i - 1] + 1 and diffs[i] > diffs[i + 1] + 1:
            transitions.append(times[i])
    return transitions


def statistics_stdev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = sum(values) / len(values)
    return math.sqrt(sum((v - m) ** 2 for v in values) / len(values))


def classify_mismatches(
    times: list[float],
    ref_paths: list[Path],
    cand_paths: list[Path],
    interval: float,
) -> list[dict]:
    """Classify visual/temporal mismatches between aligned frame sequences."""
    if not ref_paths or not cand_paths:
        return []

    ref_imgs = [load_grayscale(p) for p in ref_paths]
    cand_imgs = [load_grayscale(p) for p in cand_paths]
    n = min(len(ref_imgs), len(cand_imgs))
    times = times[:n]
    ref_imgs = ref_imgs[:n]
    cand_imgs = cand_imgs[:n]

    ref_diffs = [frame_mae(ref_imgs[i - 1], ref_imgs[i]) for i in range(1, n)]
    cand_diffs = [frame_mae(cand_imgs[i - 1], cand_imgs[i]) for i in range(1, n)]
    aligned_mae = [frame_mae(ref_imgs[i], cand_imgs[i]) for i in range(n)]

    ref_luma = [
        sum(i * c for i, c in enumerate(img.histogram())) / (img.width * img.height)
        for img in ref_imgs
    ]
    cand_luma = [
        sum(i * c for i, c in enumerate(img.histogram())) / (img.width * img.height)
        for img in cand_imgs
    ]

    mismatches: list[dict] = []
    seen: set[tuple[float, str]] = set()

    def add(t: float, kind: str, severity: str, description: str) -> None:
        key = (round(t, 3), kind)
        if key in seen:
            return
        seen.add(key)
        mismatches.append(
            {
                "timestamp": round(t, 3),
                "type": kind,
                "severity": severity,
                "description": description,
            }
        )

    # Hard cuts
    hard_cut_abs = 25.0
    hard_cut_rel = 2.5
    ref_smooth_max = 12.0
    ref_transitions = detect_transitions(ref_diffs, times[1:], 30.0)
    for i in range(1, n):
        cd = cand_diffs[i - 1]
        rd = ref_diffs[i - 1]
        if cd > hard_cut_abs and cd > hard_cut_rel * rd and rd < ref_smooth_max:
            t = times[i]
            if not any(abs(t - rt) <= max(interval, 0.5) for rt in ref_transitions):
                add(t, "hard_cut", "high", f"Candidate shows a sharp frame change ({cd:.1f}) while the reference is smooth ({rd:.1f}).")

    # Static segments
    static_low = 3.0
    ref_motion_min = 8.0
    min_static_frames = max(2, math.ceil(0.6 / interval))
    i = 0
    while i < len(cand_diffs):
        if cand_diffs[i] < static_low:
            j = i
            while j < len(cand_diffs) and cand_diffs[j] < static_low:
                j += 1
            run_len = j - i
            if run_len >= min_static_frames:
                avg_ref_motion = sum(ref_diffs[k] for k in range(i, j)) / run_len
                if avg_ref_motion > ref_motion_min:
                    add(
                        times[i],
                        "static_segment",
                        "medium",
                        f"Candidate is nearly static for {run_len * interval:.1f}s while reference moves (avg motion {avg_ref_motion:.1f}).",
                    )
            i = j
        else:
            i += 1

    # Scene boundary mismatch
    cand_transitions = detect_transitions(cand_diffs, times[1:], 30.0)
    tolerance = max(interval, 0.5)
    for rt in ref_transitions:
        if not any(abs(rt - ct) <= tolerance for ct in cand_transitions):
            add(rt, "scene_boundary_mismatch", "high", "Reference scene transition not detected in candidate.")
    for ct in cand_transitions:
        if not any(abs(ct - rt) <= tolerance for rt in ref_transitions):
            add(ct, "scene_boundary_mismatch", "high", "Candidate scene transition not present in reference.")

    # Timing offset
    max_lag = min(n - 1, max(1, int(5.0 / interval)))
    best_lag, best_corr = normalized_cross_correlation(ref_luma, cand_luma, max_lag)
    zero_corr = normalized_cross_correlation(ref_luma, cand_luma, 0)[1]
    if best_lag != 0 and best_corr > 0.75 and best_corr > zero_corr + 0.15:
        offset_seconds = best_lag * interval
        direction = "later" if offset_seconds > 0 else "earlier"
        add(
            0.0,
            "timing_offset",
            "high",
            f"Same visual sequence appears ~{abs(offset_seconds):.2f}s {direction} in the candidate (lag {best_lag}, correlation {best_corr:.2f}).",
        )

    # Missing secondary motion / texture / grain
    texture_ref_min = 12.0
    texture_ratio = 0.45
    for i in range(n):
        et_ref = edge_std(ref_imgs[i])
        et_cand = edge_std(cand_imgs[i])
        if et_ref > texture_ref_min and et_cand < texture_ratio * et_ref:
            add(
                times[i],
                "missing_secondary_motion",
                "low",
                f"Candidate is missing fine texture/grain present in reference (edge detail {et_cand:.1f} vs {et_ref:.1f}).",
            )

    window = max(3, math.ceil(1.0 / interval))
    for i in range(window, n):
        ref_window = ref_diffs[i - window : i]
        cand_window = cand_diffs[i - window : i]
        if not ref_window or not cand_window:
            continue
        ref_std = statistics_stdev(ref_window)
        cand_std = statistics_stdev(cand_window)
        if ref_std > 6.0 and cand_std < 0.35 * ref_std:
            add(
                times[i],
                "missing_secondary_motion",
                "low",
                f"Candidate temporal micro-motion is much lower than reference (std {cand_std:.1f} vs {ref_std:.1f}).",
            )

    mismatches.sort(key=lambda x: x["timestamp"])
    return mismatches


def severity_icon(severity: str) -> str:
    return {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(severity, "⚪")


def write_report(outdir: Path, data: dict) -> Path:
    report = outdir / "comparison-report.md"
    lines = [
        "# Video Comparison Report",
        "",
        "## Files",
        "",
        f"- Reference: `{data['reference']}`",
        f"- Candidate: `{data['candidate']}`",
        "",
        "## Hash / Bit Exact",
        "",
        f"- Reference SHA-256: `{data['reference_sha256']}`",
        f"- Candidate SHA-256: `{data['candidate_sha256']}`",
        f"- Byte-identical: `{data['bit_exact']}`",
        "",
        "## Video Metrics",
        "",
        f"- PSNR: `{data.get('psnr', 'not run')}`",
        f"- SSIM: `{data.get('ssim', 'not run')}`",
        "",
    ]

    if data.get("render_diff"):
        rd = data["render_diff"]
        lines.extend(
            [
                "## Render Diff Artifacts",
                "",
                f"- Frames sampled every `{rd.get('interval')}s`",
                f"- Manifest: `{rd.get('manifest_path')}`",
                "- Contact sheets:",
            ]
        )
        for p in rd.get("side_by_side_sheets", []):
            lines.append(f"  - `{p}`")
        for p in rd.get("heatmap_sheets", []):
            lines.append(f"  - `{p}`")
        lines.append("")

    if data.get("component_crop"):
        cc = data["component_crop"]
        lines.extend(
            [
                "## Component Crop Artifacts",
                "",
                f"- Manifest: `{cc.get('manifest_path')}`",
                "- Regions:",
            ]
        )
        for region in cc.get("regions", []):
            lines.append(f"  - `{region['name']}` {region['box']} → `{region.get('manifest_path')}`")
        lines.append("")

    lines.extend(["## Mismatch Classification", ""])
    mismatches = data.get("mismatches", [])
    if not mismatches:
        lines.append("No mismatches detected at the sampled timestamps.")
    else:
        lines.append(f"Detected **{len(mismatches)}** mismatch(es):")
        lines.append("")
        lines.append("| Timestamp | Type | Severity | Description |")
        lines.append("|----------:|------|----------|-------------|")
        for m in mismatches:
            lines.append(
                f"| {m['timestamp']:.3f}s | `{m['type']}` | {severity_icon(m['severity'])} {m['severity']} | {m['description']} |"
            )
    lines.append("")

    lines.extend(
        [
            "## Media Info",
            "",
            "```json",
            json.dumps({"reference": data["reference_probe"], "candidate": data["candidate_probe"]}, indent=2),
            "```",
            "",
        ]
    )
    report.write_text("\n".join(lines), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare reference and candidate video files."
    )
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--skip-metrics", action="store_true")
    parser.add_argument(
        "--render-diff",
        action="store_true",
        help="Generate side-by-side and heatmap contact sheets.",
    )
    parser.add_argument(
        "--component-crop",
        type=Path,
        help="JSON file with {name: [x, y, w, h]} boxes for region comparisons.",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=0.5,
        help="Frame sampling interval for classification and render diff.",
    )
    parser.add_argument(
        "--scale",
        default="480:270",
        help="Scale used for extracted frames.",
    )
    args = parser.parse_args()

    ffmpeg, ffprobe = discover_ffmpeg()

    outdir = args.out.expanduser().resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    reference = args.reference.expanduser().resolve()
    candidate = args.candidate.expanduser().resolve()

    if not reference.exists():
        raise SystemExit(f"Reference not found: {reference}")
    if not candidate.exists():
        raise SystemExit(f"Candidate not found: {candidate}")

    reference_sha = sha256(reference)
    candidate_sha = sha256(candidate)

    data = {
        "reference": str(reference),
        "candidate": str(candidate),
        "reference_sha256": reference_sha,
        "candidate_sha256": candidate_sha,
        "bit_exact": reference_sha == candidate_sha,
        "reference_probe": ffprobe_info(reference, ffprobe),
        "candidate_probe": ffprobe_info(candidate, ffprobe),
        "interval": args.interval,
        "scale": args.scale,
    }

    if not args.skip_metrics:
        data["psnr"] = metric(reference, candidate, outdir, "psnr", ffmpeg)
        data["ssim"] = metric(reference, candidate, outdir, "ssim", ffmpeg)

    # Frame extraction + mismatch classification
    try:
        from PIL import Image  # noqa: F401

        times, ref_paths, cand_paths = extract_pair_frames(
            reference, candidate, outdir, args.interval, args.scale, ffmpeg, ffprobe
        )
        data["mismatches"] = classify_mismatches(times, ref_paths, cand_paths, args.interval)
        data["sampled_frames"] = len(times)
    except Exception as exc:
        data["classification_error"] = str(exc)
        data["mismatches"] = []

    if args.render_diff:
        try:
            rd_manifest = run_render_diff(
                reference, candidate, outdir / "render-diff", args.interval, args.scale
            )
            data["render_diff"] = {
                "manifest_path": str((outdir / "render-diff" / "diff-manifest.json").relative_to(outdir)),
                "interval": rd_manifest["interval"],
                "side_by_side_sheets": rd_manifest["contact_sheets"]["side_by_side"],
                "heatmap_sheets": rd_manifest["contact_sheets"]["heatmap"],
            }
        except Exception as exc:
            data["render_diff_error"] = str(exc)

    if args.component_crop:
        try:
            cc_manifest = run_component_crop(
                reference,
                candidate,
                outdir / "component-crop",
                args.component_crop,
                args.interval,
                args.scale,
            )
            data["component_crop"] = {
                "manifest_path": str(
                    (outdir / "component-crop" / "component-crop-manifest.json").relative_to(outdir)
                ),
                "regions": [
                    {
                        "name": r["name"],
                        "box": r["box"],
                        "manifest_path": str(
                            (outdir / "component-crop" / "component-crop-manifest.json").relative_to(
                                outdir
                            )
                        ),
                    }
                    for r in cc_manifest["regions"]
                ],
            }
        except Exception as exc:
            data["component_crop_error"] = str(exc)

    (outdir / "comparison.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    report = write_report(outdir, data)
    print(
        json.dumps(
            {
                "report": str(report),
                "bit_exact": data["bit_exact"],
                "mismatches": len(data.get("mismatches", [])),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
