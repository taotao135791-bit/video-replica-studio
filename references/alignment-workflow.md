# Alignment Workflow

## Persistent Replica Loop

Use a persistent objective for active recreation. If the agent runtime supports
Goal mode, create a goal for the exact reference segment, fidelity level, target
renderer, and acceptance evidence. If it does not, keep the same state in
`alignment-report.md` plus `patch-log.md`.

The loop is:

1. Extract reference frames.
2. Generate candidate frames at the same timestamps.
3. Compare full frame and active-component crops.
4. Name the earliest or largest visible mismatch.
5. Patch one small part of the implementation.
6. Regenerate the same frames.
7. Update evidence and repeat.

Do not mark a segment aligned because one frame improved. Recheck the adjacent
timestamps and the full motion window.

## Reference Breakdown

Use a fixed timestamp grid. For videos under 60 seconds, default to `0.5s`.
For high-speed typography or cursor movement, add finer samples around failing
moments. Use `0.1s` or explicit timestamps for dense windows around transitions,
model switchers, vertical rails, logo/color changes, or fast layout movement.

Describe each timestamp with:

- text state
- subject position and size
- background state
- active transition
- visible cursor or interaction
- scene boundary status

## Candidate Comparison

Use the same timestamp grid. Put reference on the left and candidate on the
right. Start the report with the earliest failing timestamp. For complex
motions, also create local crops and overlays for the active component so the
repair target is measurable.

Common failure classes:

- global offset: every scene is late or early
- drift: early scenes align, later scenes do not
- wrong scale: subject is too small or too large
- wrong background: persistent effects that should not exist
- wrong transition: missing flash, wipe, blur, or speed-ramp
- wrong semantic state: text says the right words but at the wrong phase
- accidental artifacts: blank frames, solid-color flashes, missing assets

Component-level checks:

- center, width, height, scale, and rotation
- line/rail path, endpoint, length, mask, and opacity
- text line breaks, font size, weight, opacity, and timing
- logo or provider-color anchors
- card stacking order, shadow, blur, and clipping
- camera/container translation, zoom, and crop

## Repair Handoff

For each failing segment, provide:

- timestamp range
- what the reference shows
- what the candidate shows
- required change
- whether the fix is timing, layout, asset, animation, or encoding

Do not say "adjust animation" without naming the timestamp and visible target.

## Component Capture

When a repaired motion becomes reusable, write a component entry. The entry
should be short but complete:

- name
- source video and timestamp range
- what content pattern it serves
- visual behavior
- input parameters
- implementation stack
- timing contract
- evidence files
- limits

This turns one-off reference recreation into a growing HyperFrames/Remotion
component library for future AI video generation.
