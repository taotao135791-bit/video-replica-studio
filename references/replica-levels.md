# Replica Fidelity Levels

## Pixel-level

Use only when the user explicitly asks for pixel-perfect, pixel-level, exact,
bit-exact, or frame-identical output.

Acceptance evidence:

- matching file hash and `cmp`, when the output is a source-stream copy
- PSNR `average:inf`
- SSIM `All:1.000000`
- same resolution, frame rate, duration, and media start

Hand-authored HTML/Remotion/HyperFrames renders usually cannot meet this level
because browser font rasterization, anti-aliasing, easing curves, missing source
assets, and encoder differences alter pixels.

## Visual-level

Use for "复刻", "做一个一样的", "对齐这个视频" when exact source files are not
available. Acceptance is side-by-side visual review at a declared sampling
interval, usually `0.5s` for fast motion and `1.0s` for slower videos.

Required evidence:

- reference timeline report
- candidate comparison report
- side-by-side contact sheets
- a timestamped mismatch list or a clear pass statement

## Style-level

Use when the user wants "这种风格", "参考这个感觉", "做同款风格" rather than the
same shots. Extract style rules, not exact frame targets:

- palette and background treatment
- typography behavior
- motion grammar
- scene rhythm
- UI/component motifs
- transition vocabulary

Do not require frame-by-frame timing unless the user asks for a remake.
