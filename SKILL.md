---
name: video-replica-studio
description: >
  Analyze, recreate, align, and verify reference-video motion. Use when the
  user asks to recreate, copy, match, align, pixel-align, or compare a video
  against a reference; when a HyperFrames or Remotion remake is judged "not
  aligned"; when reference motion should be turned into reusable components; or
  when a video needs frame-by-frame breakdown, side-by-side contact sheets,
  dense failing-window sampling, repair logs, PSNR/SSIM, hash checks, or a
  clear pixel-level vs visual-level vs style-level fidelity decision.
---

# Video Replica Studio / 视频复刻工作室

## Role

Make reference-video work evidence-driven and reusable. Classify the requested
fidelity, extract frames, describe the source timeline, compare the candidate,
repair the implementation in small verified passes, and capture successful
motion patterns as HyperFrames / Remotion components.

This skill is both a final QC gate and a replication loop for turning real
video motion into a component library so future AI-generated videos can reuse
proven animated patterns instead of defaulting to static slide-like layouts.

## Canonical Showcase

- Human display name: Presenton 复刻 Bitexact 成片
- Example finished piece: Presenton replica pixel-aligned bitexact output
- File: `assets/showcases/presenton-replica-pixel-aligned-bitexact.mp4`
- Use this as the repository's reference-video replication showcase. It is the
correct public example for this skill, replacing older short preview clips.

## Quick Start

Use the `replica` CLI to drive the whole workflow:

```bash
# 1. Analyze the reference: frames, scene transitions, motion profile
python3 cli/replica.py analyze reference.mp4 --out analysis/reference

# 2. Compare a candidate to the reference
python3 cli/replica.py diff reference.mp4 candidate.mp4 --out analysis/diff --report

# 3. Quick coarse check (preview frames + 1.0s render diff)
python3 cli/replica.py quick reference.mp4 candidate.mp4 --out analysis/quick

# 4. Scaffold a runnable anti-PPT project
python3 cli/replica.py scaffold remotion --out my-replica/
python3 cli/replica.py scaffold hyperframes --out my-hyperframes/
```

The CLI can also be run directly after `chmod +x cli/replica.py`.

## Fidelity Levels

Read `references/replica-levels.md` before promising any fidelity level.

| Level | When to use | Acceptance criteria |
|-------|-------------|---------------------|
| **Pixel-level** | User asks for exact, bit-exact, frame-identical output, or source stream reuse is possible. | Matching SHA-256 / `cmp`, PSNR `average:inf`, SSIM `All:1.000000`, identical resolution/frame rate/duration/media start. |
| **Visual-level** | User says "复刻", "做一个一样的", "对齐这个视频" and exact source files are unavailable. | Side-by-side frames match at the declared interval (default `0.5s`), with only accepted differences documented. Requires reference timeline report, candidate comparison report, side-by-side contact sheets, and a timestamped mismatch list or clear pass statement. |
| **Style-level** | User wants "这种风格", "参考这个感觉", "做同款风格". | Style principles are present: palette, typography behavior, motion grammar, scene rhythm, motifs, transition vocabulary. Exact timing is optional. |

Never describe a HyperFrames/Remotion rebuild as pixel-level unless it passes
the hard metrics.

## Anti-PPT Checklist

Reference videos that feel alive usually share these traits. Treat them as
design requirements, not optional polish:

1. **Continuous camera / transitions** — the frame never stops moving for a
   whole scene. Use pushes, morphs, or camera rigs instead of static cuts.
2. **Secondary motion** — every primary entrance is accompanied by glows,
   sheens, grain, cursors, or ambient layers.
3. **Texture layers** — film grain, vignette, ambient glow, or noise overlays
   sit on top at low opacity.
4. **Rich easing** — avoid linear fades and simple ease-in-out defaults. Use
   `power3.inOut`, `back.out`, `elastic.out`, or custom springs.
5. **Overlapping scene lifetimes** — the next scene should begin entering
   before the previous one finishes; never fade to black first.

## Motion Pattern Library

After a motion pattern is visually aligned, capture it as a reusable component
with purpose, inputs, timing, implementation stack, evidence, and limits.

### Remotion

- Components live in `templates/remotion/components/`.
- Shared tokens live in `templates/remotion/shared/`.
- A runnable example is in `templates/remotion/example/` (see
  `templates/remotion/example/README.md`).
- Use `CameraRig`, `GlowSurface`, `GlowCard3D`, `KineticText`,
  `TypewriterText`, `Cursor`, `GrainOverlay`, `Vignette`, `AmbientGlow`, and
  `SceneTransition` as building blocks.

### HyperFrames

- Paste-in snippets live in `templates/hyperframes/components/`.
- Sub-composition blocks live in `templates/hyperframes/blocks/`.
- The Remotion → HyperFrames mapping is documented in
  `templates/hyperframes/motion-grammar.md`.
- A runnable host composition is in `templates/hyperframes/example/index.html`.

## Workflow

### 1. Establish Inputs

Collect:

- reference video path or URL
- candidate video path, if one exists
- requested fidelity level
- target renderer (HyperFrames, Remotion, CSS/SVG, etc.)
- output directory for analysis artifacts

If the URL is private or expired, retrieve a fresh source before analysis.

### 2. Analyze The Reference

```bash
python3 cli/replica.py analyze reference.mp4 --out analysis/reference
```

This produces:

- `frames/...` and `contact/...` — sampled frames and contact sheets
- `frames-manifest.json` — extraction metadata
- `scene-transitions.json` — detected scene changes
- `motion-profile.json` — activity, static segments, hard cuts, mutations

Inspect `motion-profile.json` first. It tells you where the motion lives, where
things are static, and where the hard cuts are. Use that to choose dense
sampling windows.

### 3. Compare The Candidate

```bash
python3 cli/replica.py diff reference.mp4 candidate.mp4 --out analysis/diff --report
```

This produces:

- `comparison.json` — structured comparison data
- `comparison-report.md` — human-readable report
- `psnr.log`, `ssim.log` — per-frame metrics
- `render-diff/` — side-by-side frames, heatmaps, and contact sheets
- `component-crop/` — region-level comparisons when `--crops` is provided
- `alignment-report.md` and `patch-log.md` when `--report` is provided

Read the comparison report first. It classifies mismatches as `hard_cut`,
`static_segment`, `scene_boundary_mismatch`, `timing_offset`, or
`missing_secondary_motion`.

### 4. Patch And Re-run

Pick the earliest or largest visible mismatch and make one targeted change.
Regenerate the same frames and re-run `replica diff`. Update the patch log.

Rules:

- Prefer one visible fix per pass: timing, layout, motion path, scale, color,
  or asset state.
- Recheck neighboring timestamps so a local fix does not break the sequence.
- Treat whole-frame PSNR/SSIM as supporting evidence, not the only truth, when
  fonts, browser rasterization, and generated assets differ.
- For HyperFrames, run `lint`, `validate`, and `inspect` before final render.
- For Remotion, run the equivalent render/screenshot validation used by the
  project.
- Do not say "aligned" until the report points to the passing evidence.

### 5. Capture Reusable Components

When a motion pattern is aligned well enough to reuse, write a component entry
in the motion pattern library. Each entry should include:

- component name and short description
- source reference and timestamp range
- when to use it in an AI-generated video
- input props or parameters
- timing contract and important easing/state changes
- implementation stack: HyperFrames, Remotion, React, CSS, SVG, GSAP, assets
- visual acceptance evidence: contact sheet, crop, overlay, or metrics
- known limits and what should not be promised

## CLI Reference

```bash
python3 cli/replica.py analyze <video> --out <dir> [--preview] [--interval SEC]
python3 cli/replica.py quick <reference> <candidate> --out <dir>
python3 cli/replica.py diff <reference> <candidate> --out <dir> [--crops JSON] [--report] [--interval SEC] [--scale EXPRESSION]
python3 cli/replica.py scaffold {remotion,hyperframes} --out <dir> [--config JSON]
```

| Subcommand | Purpose | Key outputs |
|------------|---------|-------------|
| `analyze` | Extract frames, detect scenes, build motion profile. | `frames/`, `contact/`, `frames-manifest.json`, `motion-profile.json`, `scene-transitions.json` |
| `quick` | Preview frames + coarse `1.0s` render diff. | `ref/`, `cand/`, `diff/` |
| `diff` | Full comparison with hashes, metrics, classification, render diff, and optional component crops. | `comparison.json`, `comparison-report.md`, `render-diff/`, `component-crop/` (with `--crops`), report templates (with `--report`) |
| `scaffold remotion` | Self-contained runnable Remotion anti-PPT project. | `package.json`, `tsconfig.json`, `src/`, `components/`, `shared/` |
| `scaffold hyperframes` | Runnable HyperFrames host composition. | `index.html` |

See `scripts/README-scripts.md` for lower-level script options.

## Outputs

Keep these artifacts near the video project:

- `alignment-report.md`
- `patch-log.md`
- reusable component entries or `component-catalog.md`
- source contact sheets
- side-by-side contact sheets
- crop/overlay evidence for active components
- `comparison-report.md`
- `motion-profile.json`
- PSNR/SSIM logs when comparing videos
- final pass/fail summary

For content-creation projects, copy the final QC artifacts into the desktop
archive `质检/` folder.

## References

- `references/replica-levels.md` — fidelity level definitions and acceptance evidence
- `references/alignment-workflow.md` — persistent replica loop and repair handoff
- `scripts/README-scripts.md` — low-level analysis script documentation
- `templates/remotion/example/README.md` — Remotion example project scripts
- `templates/hyperframes/motion-grammar.md` — Remotion → HyperFrames mapping
