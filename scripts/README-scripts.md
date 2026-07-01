# Video Replica Studio — Analysis Scripts

This directory contains the cross-platform analysis pipeline for reference-video
replication work.  All scripts require **Python 3**, **Pillow**, and a working
**ffmpeg/ffprobe** pair.

For day-to-day use, prefer the unified CLI at `cli/replica.py` (see the main
`SKILL.md`).  The scripts below are the underlying building blocks that the CLI
calls; use them directly when you need fine-grained control.

## ffmpeg/ffprobe discovery

Scripts locate the binaries in this order:

1. `FFMPEG_BIN` / `FFPROBE_BIN` environment variables.
2. `ffmpeg` / `ffprobe` on the current `PATH`.
3. The `static_ffmpeg` Python package, if installed.
4. The `imageio-ffmpeg` Python package, if installed.
5. A short list of common bundled-app fallback paths (e.g. Audio Jam,
   VideoFusion on macOS).

If the binaries are not on PATH, install `static-ffmpeg` or `imageio-ffmpeg`
with pip, or set the environment variables.

---

## `extract_frames.py`

Replacement for the older `extract_halfsec_frames.py`.  Keeps the same core CLI
and adds scene-aware dense sampling, preview mode, and motion profiling.

```bash
python3 scripts/extract_frames.py reference.mp4 --out analysis/reference
```

### Core options (backward compatible)

| Option | Default | Description |
|--------|---------|-------------|
| `video` | — | Input video path. |
| `--out` | required | Output directory for frames and manifests. |
| `--interval` | `0.5` | Seconds between regular samples. |
| `--start` | `0.0` | Start time in seconds. |
| `--end` | video duration | End time in seconds. |
| `--times` | — | Comma-separated explicit timestamps; overrides interval sampling. |
| `--scale` | `480:270` | ffmpeg `scale=` expression. Preview default is `320:180`. |
| `--quality` | `88` | JPEG quality 0-100. Preview default is `60`. |
| `--contact` | — | Generate labeled contact sheets. |
| `--cols` | `3` | Columns per contact sheet. |

### New options

| Option | Default | Description |
|--------|---------|-------------|
| `--preview` | — | Low-resolution / low-quality fast output. |
| `--detect-scenes` | — | Run ffmpeg scene detection and sample densely around transitions. |
| `--scene-threshold` | `0.3` | Scene-change score threshold. |
| `--scene-radius` | `0.3` | Seconds around each transition to sample. |
| `--scene-step` | `0.05` | Dense sampling step around transitions. |
| `--motion-profile` | — | Also write `motion-profile.json` in `--out`. |

### Examples

```bash
# Default 0.5s interval frames
python3 scripts/extract_frames.py reference.mp4 --out analysis/reference

# 0.1s dense sampling over a motion-heavy window, with contact sheets
python3 scripts/extract_frames.py reference.mp4 \
  --out analysis/reference-dense \
  --interval 0.1 --start 18 --end 21 --contact

# Preview mode for quick motion verification
python3 scripts/extract_frames.py reference.mp4 --out analysis/preview --preview

# Scene-aware extraction with motion profile
python3 scripts/extract_frames.py reference.mp4 \
  --out analysis/scenes \
  --detect-scenes --motion-profile --contact
```

### Outputs

- `frames/...` — extracted JPEG frames.
- `frames-manifest.json` — metadata about the extraction.
- `contact/...` — labeled contact sheets (with `--contact`).
- `scene-transitions.json` — detected scene changes (with `--detect-scenes`).
- `motion-profile.json` — motion profile (with `--motion-profile`).

---

## `motion_profile.py`

Standalone motion-profile tool.  Can be run directly or imported as a library
(`analyze_motion`).

```bash
python3 scripts/motion_profile.py reference.mp4 --out motion-profile.json
```

| Option | Default | Description |
|--------|---------|-------------|
| `video` | — | Input video path. |
| `--out` | stdout | Output JSON file. If omitted, JSON is printed. |
| `--fps` | source fps capped at 30 | Sampling frame rate. |
| `--scale` | `320:180` | ffmpeg scale expression for working frames. |
| `--static-threshold` | `0.015` | Activity level considered static. |
| `--hard-cut-threshold` | `0.35` | Activity peak considered a hard cut. |
| `--mutation-threshold` | `0.08` | Activity level considered a significant mutation. |
| `--keep-frames` | — | Keep the temporary extracted frames. |

The output JSON contains:

- `activity` — list of per-frame inter-frame difference values.
- `static_segments` — start/end of segments where activity stays below the static threshold.
- `hard_cuts` — sharp activity spikes above the hard-cut threshold.
- `mutations` — broader significant activity bursts above the mutation threshold.

---

## `compare_videos.py`

Compare a reference and candidate video with SHA-256 hashes and optional
PSNR/SSIM metrics.

```bash
python3 scripts/compare_videos.py reference.mp4 candidate.mp4 --out analysis/compare
```

| Option | Description |
|--------|-------------|
| `reference` | Reference video. |
| `candidate` | Candidate video. |
| `--out` | Output directory. |
| `--skip-metrics` | Skip PSNR/SSIM (faster, hash-only). |

### Outputs

- `comparison.json` — structured comparison data.
- `comparison-report.md` — human-readable report.
- `psnr.log`, `ssim.log` — per-frame metric logs (unless `--skip-metrics`).

---

## `render_diff.py`

Render side-by-side and pixel-difference heatmaps for every sampled timestamp,
plus contact sheets.

```bash
python3 scripts/render_diff.py reference.mp4 candidate.mp4 analysis/diff \
  --interval 0.5 --scale 480:270 --cols 3
```

| Option | Default | Description |
|--------|---------|-------------|
| `reference` | — | Reference video. |
| `candidate` | — | Candidate video. |
| `output` | — | Output directory. |
| `--interval` | `0.5` | Seconds between samples. |
| `--scale` | `480:270` | ffmpeg scale expression for extracted frames. |
| `--cols` | `3` | Columns per contact sheet. |

## `component_crop.py`

Compare cropped regions between two videos.  The crops JSON maps region names to
`[x, y, w, h]` boxes in the coordinate space defined by `--scale`.

```bash
echo '{"logo": [20, 20, 200, 80]}' > crops.json
python3 scripts/component_crop.py reference.mp4 candidate.mp4 analysis/crops \
  --crops crops.json --interval 0.5 --scale 480:270 --cols 3
```

| Option | Default | Description |
|--------|---------|-------------|
| `reference` | — | Reference video. |
| `candidate` | — | Candidate video. |
| `output` | — | Output directory. |
| `--crops` | required | JSON file with `{name: [x, y, w, h]}` boxes. |
| `--interval` | `0.5` | Seconds between samples. |
| `--scale` | `480:270` | ffmpeg scale expression for extracted frames. |
| `--cols` | `3` | Columns per contact sheet. |

## Internal helpers

`_utils.py` is a private helper module used by the scripts above.  It is not
intended to be run directly.  It provides ffmpeg/ffprobe auto-discovery and a
cross-platform font fallback helper.
