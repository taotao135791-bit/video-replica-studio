---
name: video-replica-studio
description: >
  Analyze, recreate, align, and verify reference-video motion with multimodal
  visual understanding. Use when the user asks to recreate, copy, match, align,
  pixel-align, or compare a video against a reference; when a HyperFrames or
  Remotion remake is judged "not aligned"; when reference motion should be
  turned into reusable components; when a video needs frame-by-frame breakdown,
  side-by-side contact sheets, dense failing-window sampling, repair logs,
  PSNR/SSIM, hash checks, or a clear pixel-level vs visual-level vs style-level
  fidelity decision; or when the user wants to extract a visual style DNA from
  a reference and re-express it in new content.
---

# Video Replica Studio / 视频复刻工作室

## Role

Make reference-video work evidence-driven, visually intelligent, and reusable.
Classify the requested fidelity, **see** the reference frames with multimodal
understanding, extract visual intent, map motion to known components, compare
the candidate, repair the implementation in small verified passes, and capture
successful motion patterns as HyperFrames / Remotion components.

This skill is both a final QC gate and a replication loop for turning real
video motion into a component library so future AI-generated videos can reuse
proven animated patterns instead of defaulting to static slide-like layouts.

For multimodal agents: **actively look at the contact sheets, render-diff
heatmaps, and side-by-side frames at every decision point**. Your visual
understanding is a first-class signal alongside PSNR/SSIM numbers.

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

# Scaffold with a JSON config (Remotion only)
python3 cli/replica.py scaffold remotion --out my-replica/ --config style-dna.json
```

The CLI can also be run directly as `./cli/replica.py` (it already has execute permission).

## Fidelity Levels

Read `references/replica-levels.md` before promising any fidelity level.

| Level | When to use | Acceptance criteria |
|-------|-------------|---------------------|
| **Pixel-level** | User asks for exact, bit-exact, frame-identical output, or source stream reuse is possible. | Matching SHA-256 hash (byte-identical files produce identical hashes), PSNR `average:inf`, SSIM `All:1.000000`, identical resolution/frame rate/duration/media start. |
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

For a deeper decision tree of motion patterns — when to use each, how to
combine them, and which component implements them — read
`references/motion-vocabulary.md`.

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
- SVG animation patterns (MotionPath, DrawSVG, MorphSVG) and GSAP best practices
  are documented in `references/gsap-svg-patterns.md` — use it for reference
  motion that involves SVG paths, strokes, shape morphs, or transform-origin
  subtleties.
- A runnable host composition is in `templates/hyperframes/example/index.html`.

## Style DNA Extraction

When the fidelity target is **Style-level**, or when the user wants to
re-express a reference's visual identity in new content, extract the Style DNA
before writing any code. Read `references/style-dna.md` for the full method.

Summary:

1. **Extract** primitives from contact sheets: color ratios, font personality,
   motion rhythm type (staccato / legato / hybrid), transition vocabulary,
   spatial density, and hero-to-whitespace ratio.
2. **Encode** primitives as parameterized tokens that map to the shared
    `Palette`, `EasingType`, and `TransitionType` types in the Remotion /
   HyperFrames shared modules.
3. **Re-express** by choosing a variation strategy: rhythm acceleration /
   deceleration, temperature shift (warm ↔ cool), spatial density increase /
   decrease, or motion density scaling.

This turns a vague "参考这个感觉" into a concrete, parameterized style brief
that the agent can implement directly in `palette.ts`, `easings.ts`, or
CSS `:root` variables.

## Workflow

### 1. Establish Inputs

Collect:

- reference video path or URL (URLs must be downloaded to a local file before running the CLI)
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

> **Visual Inspection Prompt:** Now read the contact sheet images. In your
> own words, describe: (a) the visual rhythm — is it fast-cut or long-take?
> (b) the dominant color temperature and mood. (c) the types of motion you
> observe — camera moves, text animations, object entrances, particle effects.
> (d) the narrative arc — how does the video open, build, and close?

### 3. Visual Intent Extraction

Read `references/visual-intent-guide.md` for the full protocol.

Using the contact sheets and motion profile, describe each scene segment with:

- **what happens** — text state, subject position/size, background, transition
- **why it happens** — the visual intent: attention capture, hierarchy
  establishment, brand tonality, urgency, spatial depth, or narrative beat
- **emotion/mood** — the feeling the segment should evoke

Output a `visual-intent.md` that serves as the creative brief for the
replication. This is especially important for Style-level work where the
goal is to understand the *design reasoning*, not just the pixel targets.

For Style-level tasks, also run the **Style DNA Extraction** here (see above).

### 4. Early Component Recognition

Before comparing or building, scan the visual intent against the Motion
Pattern Library and the Motion Vocabulary Card Deck
(`references/motion-vocabulary.md`).

Output a `component-mapping.json`:

```json
{
  "scenes": [
    {
      "timestamp": "0.0-3.5",
      "detected_patterns": ["camera-push", "kinetic-text-entrance"],
      "matched_components": ["CameraRig", "KineticText"],
      "needs_new_component": false,
      "notes": "Slow push-in with staggered word reveal"
    },
    {
      "timestamp": "3.5-7.0",
      "detected_patterns": ["glow-card-3d-tilt", "traveling-sheen"],
      "matched_components": ["GlowCard3D", "GlowSurface"],
      "needs_new_component": false,
      "notes": "Hero card with ambient bloom"
    }
  ],
  "unmatched_patterns": []
}
```

This lets the scaffold phase become "assemble from mapping + customize" instead
of "build from scratch".

### 5. Compare The Candidate

```bash
python3 cli/replica.py diff reference.mp4 candidate.mp4 --out analysis/diff --report

# Compare focused regions (e.g. logo, headline)
echo '{"logo": [20, 20, 200, 80], "headline": [100, 200, 600, 120]}' > crops.json
python3 cli/replica.py diff reference.mp4 candidate.mp4 --out analysis/diff --report --crops crops.json
```

This produces:

- `comparison.json` — structured comparison data
- `comparison-report.md` — human-readable report
- `psnr.log`, `ssim.log` — per-frame metrics
- `render-diff/` — side-by-side frames, heatmaps, and contact sheets
- `component-crop/` — region-level comparisons when `--crops` is provided
- `alignment-report.md` and `patch-log.md` report templates copied into `--out` when `--report` is provided

Read the comparison report first. It classifies mismatches as `hard_cut`,
`static_segment`, `scene_boundary_mismatch`, `timing_offset`, or
`missing_secondary_motion`.

> **Visual Inspection Prompt:** Look at the render-diff heatmaps. Where are
> the largest visual differences? Are they in focal areas (text, hero subject)
> or peripheral areas (background texture, edge grain)? Prioritize focal-area
> mismatches — the viewer's eye forgives peripheral differences more easily.

### 6. Patch And Re-run

Pick the earliest or largest visible mismatch and make one targeted change.
Regenerate the same frames and re-run `replica diff`. Update the patch log.

> **Visual Inspection Prompt:** Before patching, look at the reference frame
> and candidate frame side by side. Describe what you see in natural language
> first, then map your observation to a specific code change (timing value,
> easing curve, scale factor, color, or component prop).

Rules:

- Prefer one visible fix per pass: timing, layout, motion path, scale, color,
  or asset state.
- Recheck neighboring timestamps so a local fix does not break the sequence.
- Treat whole-frame PSNR/SSIM as supporting evidence, not the only truth, when
  fonts, browser rasterization, and generated assets differ.
- For HyperFrames, run `lint`, `validate`, and `inspect` (if the HyperFrames CLI is available) before final render.
- For Remotion, run the equivalent render/screenshot validation used by the
  project.
- Do not say "aligned" until the report points to the passing evidence.

### 7. Capture Reusable Components

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
- **combination recipes**: which other components pair well with this one
  (see `references/motion-vocabulary.md` for standard recipes)

## CLI Reference

```bash
python3 cli/replica.py analyze <video> --out <dir> [--preview] [--interval SEC]
python3 cli/replica.py quick <reference> <candidate> --out <dir>
python3 cli/replica.py diff <reference> <candidate> --out <dir> [--crops PATH] [--report] [--interval SEC] [--scale EXPRESSION]
python3 cli/replica.py scaffold {remotion,hyperframes} --out <dir> [--config PATH]
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

- `visual-intent.md` — visual intent extraction and creative brief
- `component-mapping.json` — early component recognition mapping
- `alignment-report.md`
- `patch-log.md`
- reusable component entries or `component-catalog.md`
- source contact sheets
- side-by-side contact sheets
- crop/overlay evidence for active components
- `comparison-report.md`
- `motion-profile.json`
- PSNR/SSIM logs when comparing videos
- `style-dna.json` — extracted style primitives (Style-level tasks)
- final pass/fail summary

For content-creation projects, copy the final QC artifacts into the desktop
archive `质检/` folder.

## References

- `references/replica-levels.md` — fidelity level definitions and acceptance evidence
- `references/alignment-workflow.md` — persistent replica loop and repair handoff
- `references/visual-intent-guide.md` — visual intent extraction protocol for multimodal agents
- `references/motion-vocabulary.md` — motion vocabulary card deck: decision trees, combination recipes, component mapping
- `references/style-dna.md` — style DNA extraction and re-expression methodology
- `references/presenton-lessons.md` — case-study failure patterns and durable rules
- `scripts/README-scripts.md` — low-level analysis script documentation
- `templates/remotion/example/README.md` — Remotion example project scripts
- `templates/hyperframes/motion-grammar.md` — Remotion → HyperFrames mapping
- `references/gsap-svg-patterns.md` — GSAP SVG animation patterns for HyperFrames (MotionPath, DrawSVG, MorphSVG, transform origins)
