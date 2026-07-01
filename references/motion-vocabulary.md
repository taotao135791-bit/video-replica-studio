# Motion Vocabulary Card Deck

A decision-oriented catalog of motion patterns. Each card tells you **what it
does**, **when to use it**, **when to avoid it**, and **which component
implements it** in Remotion and HyperFrames.

Use this during Early Component Recognition (Workflow Step 4) and when
selecting building blocks for scaffold.

---

## Camera & Transition Cards

### camera-push

- **What:** Slow zoom-in toward a focal point, creating depth and focus.
- **When:** Hero moments, feature reveals, drawing attention to a detail.
- **Avoid:** When the scene already has high motion density — a push adds
  visual complexity on top of complexity.
- **Easing:** `power3.inOut` or `cameraPushEasing` (slow start, fast middle,
  gentle settle).
- **Remotion:** `CameraRig` with `scale` + `translate` toward target.
- **HyperFrames:** `.world` / `.camera` wrapper transform — see
  `components/camera-rig.html`.

### camera-pull

- **What:** Slow zoom-out, revealing context or creating distance.
- **When:** Closing scenes, revealing a full layout after detail shots,
  "big picture" narrative beats.
- **Avoid:** Opening scenes — pulling out implies retreat, not engagement.
- **Remotion:** `CameraRig` with inverse scale + translate.
- **HyperFrames:** Reverse the camera-push tween direction.

### push-transition

- **What:** The entire frame slides in a direction to reveal the next scene.
- **When:** Linear narratives, step-by-step progressions, timeline videos.
- **Avoid:** When scenes have no spatial relationship — a push implies
  directional continuity.
- **Remotion:** `SceneTransition` with `transition: "push"`.
- **HyperFrames:** Scene-to-scene GSAP choreography — animate outgoing scene
  `translateX/Y` out while incoming scene enters from opposite.

### blur-wipe-transition

- **What:** Outgoing scene blurs and fades while incoming scene sharpens in.
- **When:** Dreamy, atmospheric, or premium brand videos.
- **Avoid:** Fast-paced, data-heavy, or technical content — blur feels
  imprecise.
- **Remotion:** `SceneTransition` with `transition: "blur-wipe"`.
- **HyperFrames:** CSS `filter: blur()` tween + opacity crossfade.

### scale-morph-transition

- **What:** Outgoing scene scales up and fades; incoming scene scales in from
  smaller size. Creates a "passing through" feeling.
- **When:** Product showcases, feature comparisons, before/after reveals.
- **Avoid:** Text-heavy scenes — scaling text is hard to read during morph.
- **Remotion:** `SceneTransition` with `transition: "scale-morph"`.
- **HyperFrames:** `scale` + `opacity` GSAP crossfade on both scenes at the
  same timeline position.

---

## Text & Typography Cards

### kinetic-text-entrance

- **What:** Words or phrases enter with energetic staggered animation — each
  word slides, rotates, or scales in with a slight delay.
- **When:** Headlines, key messages, brand statements, calls to action.
- **Avoid:** Long paragraphs — stagger becomes chaotic with >6 phrases.
- **Easing:** `back.out(1.6)` for playful energy; `power3.out` for corporate
  confidence.
- **Remotion:** `KineticText` component.
- **HyperFrames:** GSAP `fromTo` per phrase — see
  `components/kinetic-text.html`.

### typewriter-reveal

- **What:** Characters appear one by one with a blinking cursor, simulating
  typing.
- **When:** Code snippets, quotes, step-by-step instructions, technical
  content.
- **Avoid:** Headlines or emotional content — typewriter feels mechanical,
  not expressive.
- **Remotion:** `TypewriterText` component.
- **HyperFrames:** `onUpdate` textContent slice + deterministic cursor blink
  — see `components/typewriter-text.html`.

### text-scale-up

- **What:** Text starts small and scales up to full size, often with slight
  overshoot.
- **When:** Emphasis moments, stat reveals, number callouts.
- **Avoid:** When text needs to be readable during the animation — it is only
  legible at full size.
- **Remotion:** `KineticText` with `scale` variant.
- **HyperFrames:** `fromTo({ scale: 0.5, opacity: 0 }, { scale: 1, opacity: 1 })`.

---

## Surface & Depth Cards

### glow-card-3d

- **What:** A card with 3D perspective tilt and an animated glow/sheen behind
  it. Settles into final position with subtle overshoot.
- **When:** Feature cards, product highlights, profile cards, premium UI
  showcases.
- **Avoid:** Dense layouts with many cards — each card demands visual
  attention; too many creates noise.
- **Remotion:** `GlowCard3D` component.
- **HyperFrames:** `preserve-3d` + `perspective` + GSAP bloom — see
  `blocks/glow-card-3d.html`.

### glow-surface

- **What:** A flat surface with an animated bloom or traveling sheen across it.
- **When:** Background accents, panel highlights, section dividers.
- **Avoid:** When the surface contains interactive elements — the glow can
  obscure click targets visually.
- **Remotion:** `GlowSurface` component.
- **HyperFrames:** Radial gradient bloom or clipped gradient band — see
  `components/glow-surface.html`.

### ambient-glow

- **What:** A soft, large, low-opacity glow layer that sits behind hero
  content. Color is darker and more saturated than the hero it backs.
- **When:** Adding depth to otherwise flat compositions, brand color
  reinforcement.
- **Avoid:** When the background is already busy — ambient glow adds a layer
  that can muddy the composition.
- **Peak opacity:** ≤ 0.45.
- **Remotion:** `AmbientGlow` component.
- **HyperFrames:** `components/ambient-glow.html`.

---

## Interaction Cards

### cursor-interaction

- **What:** An animated mouse cursor moves to a target, clicks, and produces a
  ripple effect.
- **When:** Product demos, UI walkthroughs, "how it works" sequences.
- **Avoid:** Non-interactive content — a cursor in a brand video feels out
  of place.
- **Remotion:** `Cursor` component.
- **HyperFrames:** Positioned div + GSAP move + ripple — see
  `components/cursor.html`.

---

## Texture & Atmosphere Cards

### film-grain

- **What:** A static or near-static noise texture at very low opacity, giving
  a cinematic, analog feel.
- **When:** Almost always — grain is the cheapest way to add texture and
  avoid the "AI-generated flat" look.
- **Avoid:** Pixel-level fidelity tasks where grain alters hash values.
- **Opacity:** 0.03–0.06 with `mix-blend-mode: overlay`.
- **Remotion:** `GrainOverlay` component.
- **HyperFrames:** Inline SVG noise filter — see `components/grain-overlay.html`.

### vignette

- **What:** A radial gradient overlay that darkens the edges, drawing the eye
  toward the center.
- **When:** Cinematic or dramatic scenes, focusing attention, closing moments.
- **Avoid:** Wide panoramic compositions where edge darkening feels
  unnatural.
- **Remotion:** `Vignette` component.
- **HyperFrames:** CSS radial gradient — see `components/vignette.html`.

---

## Combination Recipes

Standard pairings that produce polished, anti-PPT scenes:

### Brand Statement Scene
```
CameraRig (slow push) + KineticText (stagger entrance) + AmbientGlow +
GrainOverlay + Vignette
```
Use for: opening hooks, brand declarations, product vision statements.

### Feature Showcase Scene
```
GlowCard3D (tilt + bloom) + TypewriterText (detail reveal) + Cursor (click) +
GrainOverlay
```
Use for: product features, UI demos, capability highlights.

### Data Reveal Scene
```
CameraRig (pull to reveal) + KineticText (scale-up numbers) + GlowSurface +
Vignette
```
Use for: statistics, metrics, before/after comparisons.

### Transition Chain
```
push-transition → scale-morph-transition → blur-wipe-transition
```
Use for: building escalation — start directional, morph through the climax,
blur-wipe into the close.

### Ambient Bed (background layer stack)
```
GrainOverlay (z-index: 999) + Vignette (z-index: 998) + AmbientGlow (z-index: 1)
```
Use for: **every** scene as a default texture stack. Remove only when the
reference explicitly has no texture.

---

## Decision Tree

```
Is the scene static for > 2 seconds?
├─ YES → Add CameraRig (slow push or pull)
│        + AmbientGlow as secondary motion
└─ NO → Does it have a primary subject entrance?
    ├─ YES → Is it text?
    │   ├─ YES, headline → KineticText
    │   ├─ YES, code/quote → TypewriterText
    │   └─ NO → Is it a card/surface?
    │       ├─ YES → GlowCard3D or GlowSurface
    │       └─ NO → Generic fromTo entrance + secondary motion
    └─ NO → Is it a transition?
        ├─ YES → Choose from push / blur-wipe / scale-morph
        └─ NO → Add GrainOverlay + Vignette as texture bed
```

Always check: does the scene have at least **one primary motion** and **one
secondary motion** layer? If not, it will feel like a PPT slide.
