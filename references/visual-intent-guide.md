# Visual Intent Extraction Guide

This protocol is designed for **multimodal agents** that can look at images.
It turns contact sheets and motion profiles into a structured creative brief
so the replication is driven by visual understanding, not just numbers.

## When To Use

- After `analyze` produces contact sheets and `motion-profile.json`.
- Especially valuable for **Style-level** and **Visual-level** fidelity tasks.
- For Pixel-level tasks, the visual intent is supplementary — the hard metrics
  are the source of truth.

## Protocol

### Step 1: Read the Contact Sheets

Open every contact sheet image in the `contact/` directory. Do not skip this
step — your multimodal understanding is the point.

Answer these questions in natural language:

1. **Visual rhythm** — Is this a fast-cut video (many scenes in quick
   succession) or a long-take video (few scenes held for longer)? What is the
   approximate average scene duration?
2. **Color temperature** — Is the palette warm (amber/orange), cool
   (blue/cyan), neutral, or high-contrast mixed? What is the dominant
   background color?
3. **Motion types** — Categorize the visible motion:
   - Camera moves (push, pull, pan, tilt, orbit)
   - Text animations (typewriter, kinetic stagger, slide-in, scale-up)
   - Object entrances (fade, slide, bounce, morph, wipe)
   - Particle/texture effects (grain, glow, sparks, confetti)
   - UI interactions (cursor, click ripple, toggle, scroll)
4. **Narrative arc** — How does the video open (hook?), build (escalation?),
   and close (CTA, logo lockup, fade)?
5. **Spatial composition** — Are subjects centered, rule-of-thirds, or
   asymmetric? Is the layout dense (many overlapping elements) or sparse
   (generous whitespace)?

### Step 2: Map Motion Profile to Visual Intent

Cross-reference `motion-profile.json` with your observations:

- **activity peaks** → what is happening visually at these moments? (scene
  transitions, text entrances, object animations)
- **static segments** → what is the visual state during calm periods? (holding
  on a hero subject, waiting for user interaction, ambient texture only)
- **hard cuts** → what type of transition? (push, wipe, flash, morph, dissolve)
- **mutations** → what is changing? (background swap, palette shift, scale
  jump, layout restructure)

### Step 3: Write the Visual Intent Brief

For each scene segment, write an entry with:

| Field | Description |
|-------|-------------|
| `timestamp` | Start–end range from motion-profile |
| `what` | Objective description: text, subject, background, transition |
| `why` | Visual intent: attention capture, hierarchy, brand tonality, urgency, spatial depth, narrative beat |
| `mood` | Emotion the segment should evoke: confidence, curiosity, excitement, calm, authority |
| `motion_type` | Primary + secondary motion from the vocabulary above |
| `focal_point` | Where the viewer's eye should land (center, top-left, etc.) |
| `energy` | Low / medium / high — relative to the overall video |

### Step 4: Identify Design Principles

After describing all segments, look for patterns and extract 3–5 design
principles that govern the whole video. Examples:

- "Every text entrance uses a stagger from bottom-left with back.out easing."
- "The camera never stops — even 'static' scenes have a slow push."
- "Color shifts from cool to warm as the narrative builds."
- "Secondary motion (glow, grain) always accompanies primary entrances."
- "Transitions overlap: the next scene starts entering at ~80% of the current
  scene's lifetime."

These principles become the design rules for the replication. They are
especially valuable for Style-level work where exact timing is flexible but
the *feel* must match.

## Output Format

Write the result as `visual-intent.md` in the analysis output directory.
Structure:

```markdown
# Visual Intent Brief

## Overview
- Rhythm: [fast-cut / long-take / hybrid]
- Temperature: [warm / cool / neutral / mixed]
- Density: [dense / sparse / moderate]
- Narrative: [hook → build → close description]

## Design Principles
1. ...
2. ...
3. ...

## Scene Segments

### 0.0s – 3.5s: Opening Hook
- **What:** ...
- **Why:** ...
- **Mood:** ...
- **Motion:** ...
- **Focal point:** ...
- **Energy:** high

### 3.5s – 7.0s: Feature Introduction
- **What:** ...
- ...
```

## Tips for Multimodal Agents

- **Do not just describe pixels.** Describe the *design intent* behind what you
  see. "A large hero number in the center" is observation. "A large hero number
  centered to establish authority and draw immediate attention" is intent.
- **Use the Anti-PPT Checklist as a lens.** When you see continuous camera
  motion, note it. When you notice secondary motion layers, name them.
- **Flag what is missing.** If the reference lacks something from the Anti-PPT
  Checklist (e.g. no texture layers), note that too — it defines the style.
- **Connect to components.** When you see a motion pattern that matches an
  existing component (CameraRig, KineticText, GlowCard3D, etc.), name it. This
  feeds directly into Early Component Recognition.
