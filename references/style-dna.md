# Style DNA Extraction & Re-expression

This method turns a vague "参考这个感觉" into a concrete, parameterized style
brief that can be directly implemented in Remotion `palette.ts`, `easings.ts`,
`types.ts`, or HyperFrames CSS `:root` variables.

## When To Use

- Fidelity level is **Style-level** ("这种风格", "同款感觉", "参考风格").
- User wants to apply a reference video's visual identity to **new content**.
- You have contact sheets and a motion profile from `analyze`.

## Method

### Phase 1: Extract Primitives

Look at the contact sheets and extract these measurable primitives:

| Primitive | How to Measure | Example |
|-----------|---------------|---------|
| **Color ratios** | What % of frame area is background, surface, primary, accent? | bg 70%, surface 15%, primary 10%, accent 5% |
| **Color temperature** | Warm (amber/orange/red) vs cool (blue/cyan/purple) vs neutral | Cool-dominant with warm accent |
| **Font personality** | Serif vs sans-serif, weight, size ratio to frame, letter-spacing | Sans-serif, semibold hero, large scale (40% frame height) |
| **Motion rhythm** | Staccato (quick bursts + holds) vs legato (continuous smooth) vs hybrid | Hybrid: legato camera + staccato text |
| **Transition vocabulary** | Which transition types appear and how often? | push 60%, blur-wipe 30%, hard-cut 10% |
| **Spatial density** | How many overlapping elements per frame on average? | Moderate: 2-3 layers (subject + glow + grain) |
| **Hero-to-whitespace ratio** | How much of the frame does the primary subject occupy? | Hero occupies ~40% of frame, generous margins |
| **Easing preference** | Which easings dominate? | power3.inOut for camera, back.out for entrances |
| **Scene duration** | Average and range of scene hold times | Avg 3.5s, range 2-6s |

### Phase 2: Encode as Style Tokens

Map the extracted primitives to the shared type system used by Remotion and
HyperFrames:

**`Palette` mapping** (Remotion `shared/palette.ts` / HyperFrames CSS `:root`):

```typescript
// Extracted style DNA → Palette
const extractedPalette: Palette = {
  background: "/* dominant background color */",
  surface: "/* card/panel surface color */",
  surfaceHighlight: "/* hover/active surface */",
  primary: "/* most prominent accent */",
  primaryGlow: "/* primary at 55% opacity */",
  text: "/* main text color */",
  textMuted: "/* secondary text color */",
  accent: "/* secondary accent, often complementary */",
  grain: "rgba(255, 255, 255, 0.04)", // universal, adjust opacity
};
```

**`EasingType` mapping** (Remotion `shared/easings.ts` / HyperFrames GSAP
strings):

| Extracted rhythm | Remotion EasingType | HyperFrames GSAP |
|-----------------|--------------------|--------------------|
| Smooth, confident | `"easeOut"` | `"power3.out"` |
| Playful, bouncy | `"backOut"` | `"back.out(1.6)"` |
| Precise, mechanical | `"easeInOut"` | `"power2.inOut"` |
| Energetic, springy | `"elastic"` | `"elastic.out(1, 0.5)"` |
| Camera movement | use `cameraPushEasing` | `"power3.inOut"` |

**`TransitionType` mapping** (Remotion `shared/types.ts` / HyperFrames
scene-to-scene choreography):

| Extracted transition | Remotion TransitionType | HyperFrames equivalent |
|---------------------|------------------------|----------------------|
| Directional slide | `"push"` | GSAP translateX/Y choreography |
| Atmospheric fade | `"blur-wipe"` | CSS blur + opacity crossfade |
| Zoom through | `"scale-morph"` | GSAP scale + opacity morph |
| No transition | `"none"` | Hard cut (set opacity) |

**`SceneConfig` rhythm** (scene duration and overlap):

```typescript
// From extracted scene duration and transition frequency
const sceneRhythm = {
  avgDurationFrames: /* avg scene duration × fps */,
  overlapFrames: /* ~20% of avg duration for overlapping lifetimes */,
  holdFrames: /* 0-15 frames for "breathing room" after entrance */,
};
```

### Phase 3: Re-expression Strategies

Once the style DNA is encoded, choose a variation strategy based on the new
content's needs:

#### Rhythm Acceleration / Deceleration

- **Accelerate:** Shorten scene durations by 30%, tighten overlaps. Feels
  more energetic and urgent. Good for social media cuts.
- **Decelerate:** Lengthen scene durations by 30%, widen overlaps. Feels
  more premium and contemplative. Good for brand films.

#### Temperature Shift (Warm ↔ Cool)

- **Warm shift:** Rotate palette hues +20° toward amber/red. Swap blue
  primary → amber primary, cyan accent → orange accent.
- **Cool shift:** Rotate palette hues -20° toward blue/purple. Swap amber
  primary → blue primary, orange accent → teal accent.
- Keep background, surface, and text colors stable — only shift primary and
  accent.

#### Spatial Density Scaling

- **Increase density:** Add more secondary motion layers (extra AmbientGlow,
  additional particle effects), reduce whitespace, bring hero subject closer
  (higher hero-to-frame ratio).
- **Decrease density:** Remove one texture layer, increase whitespace, scale
  hero down (lower hero-to-frame ratio), add more hold frames between
  transitions.

#### Motion Density Scaling

- **Increase motion:** Replace `"none"` transitions with `"push"`, add
  CameraRig to every scene, add Cursor interactions, shorten easing durations
  for snappier feel.
- **Decrease motion:** Replace `"push"` with `"blur-wipe"`, remove CameraRig
  from calm scenes, extend easing durations for a more relaxed feel.

## Output Format

Write the result as `style-dna.json` in the analysis output directory:

```json
{
  "source_video": "reference.mp4",
  "extracted_at": "2024-01-01T00:00:00Z",
  "primitives": {
    "color_ratios": { "background": 0.70, "surface": 0.15, "primary": 0.10, "accent": 0.05 },
    "color_temperature": "cool-dominant",
    "font_personality": "sans-serif semibold large",
    "motion_rhythm": "hybrid",
    "transition_vocab": { "push": 0.6, "blur-wipe": 0.3, "hard-cut": 0.1 },
    "spatial_density": "moderate",
    "hero_to_whitespace": 0.40,
    "easing_preference": ["power3.inOut", "back.out(1.6)"],
    "avg_scene_duration_sec": 3.5
  },
  "encoded": {
    "palette": { "...Palette fields..." : "" },
    "easing_type": "backOut",
    "transition_type": "push",
    "scene_rhythm": { "avg_duration_frames": 105, "overlap_frames": 21, "hold_frames": 8 }
  },
  "variation_suggestion": "rhythm-decelerate + temperature-warm"
}
```

## Integration with Existing Components

The Style DNA output maps directly to the existing shared modules:

| Style DNA field | Remotion module | HyperFrames equivalent |
|----------------|-----------------|----------------------|
| `palette` | `shared/palette.ts` → `Palette` interface | CSS `:root` variables |
| `easing_type` | `shared/easings.ts` → `easingFromType()` | GSAP ease string |
| `transition_type` | `shared/types.ts` → `TransitionType` | Scene-to-scene choreography |
| `scene_rhythm` | `shared/types.ts` → `SceneConfig` fields | `data-start`, `data-duration` on clips |
| `spatial_density` | Component selection (use more/fewer overlay components) | Same — choose overlay stack depth |

This ensures the Style DNA is not just a description but a **direct input** to
the scaffold and replication phases.
