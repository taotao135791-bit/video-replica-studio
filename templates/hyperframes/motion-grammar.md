# Motion Grammar — Remotion → HyperFrames Mapping

This document maps the anti-PPT motion patterns used by the Remotion templates to the closest HyperFrames primitives. HyperFrames renders video from seekable HTML + GSAP, so the unit of reuse is a **sub-composition block** (`data-composition-src`) or a **paste-in component snippet** (HTML/CSS/JS), not a React component.

> TL;DR: Remotion props become HyperFrames `data-variable-values` (for blocks) or top-of-script constants / CSS variables (for snippets). Transitions become CSS/GSAP scene-to-scene choreography or `HyperShader` transitions. Effects become CSS overlays or GSAP-driven layers.

---

## 1. CameraRig / Scene Transition System

### Remotion concept
`CameraRig` sequences `SceneConfig[]`, applies `TransitionType` (`push`, `blur-wipe`, `scale-morph`, `none`), and animates a virtual camera over `durationInFrames`.

### HyperFrames equivalent
A **host `index.html`** wires standalone scene blocks with `data-composition-src`. Camera motion is a `.world`/`.camera` wrapper transform inside a scene. Scene-to-scene handoff is either:

- **CSS/GSAP transitions** — animate the outgoing scene and incoming scene at the same `t` (the transition IS the exit; never fade out before the transition).
- **`HyperShader` shader transitions** — use `@hyperframes/shader-transitions` for WebGL morphs.

### Minimal host wiring

```html
<div
  id="root"
  data-composition-id="main"
  data-width="1920"
  data-height="1080"
  data-duration="10"
>
  <!-- Scene A -->
  <div
    class="clip"
    data-composition-id="scene-a"
    data-composition-src="compositions/scene-a.html"
    data-start="0"
    data-duration="5"
    data-track-index="1"
    data-width="1920"
    data-height="1080"
  ></div>

  <!-- Scene B -->
  <div
    class="clip"
    data-composition-id="scene-b"
    data-composition-src="compositions/scene-b.html"
    data-start="4.7"
    data-duration="5.3"
    data-track-index="2"
    data-width="1920"
    data-height="1080"
  ></div>
</div>
```

### Virtual camera inside a scene (single-wrapper form)

```js
const world = document.getElementById("world");
const cam = { scale: 1, x: 0, y: 0 };
function applyCamera() {
  world.style.transform = `translate(${cam.x}px, ${cam.y}px) scale(${cam.scale})`;
}
applyCamera();

// Push in on a focal point
const counterY = -targetOffsetY * targetScale;
tl.to(cam, {
  scale: targetScale,
  y: counterY,
  duration: 1.2,
  ease: "power3.inOut",
  onUpdate: applyCamera,
}, 2.0);
```

> See `components/camera-rig.html` and `blocks/camera-rig-block.html`.

---

## 2. GlowSurface / GlowCard3D

### Remotion concept
A 3D-tilted card or surface with an animated glow / sheen behind or across it.

### HyperFrames equivalent
Two forms:

1. **Hero bloom** — a radial-gradient layer behind the card, animated with `opacity` + `scale`.
2. **Traveling sheen** — a clipped gradient band that translates once across the surface.

Use `preserve-3d` + `perspective` for the 3D tilt; animate only `rotateX`/`rotateY`/`scale` (transform-only).

```html
<div class="card-stage">
  <div class="glow" id="card-glow"></div>
  <div class="card" id="card">{{content}}</div>
</div>
```

```css
.card-stage {
  position: relative;
  perspective: 1200px;
  transform-style: preserve-3d;
}
.card {
  position: relative;
  z-index: 2;
  transform: rotateX(var(--rx, 0deg)) rotateY(var(--ry, 0deg));
  background: var(--surface);
  border: 1px solid rgba(255,255,255,0.08);
}
.glow {
  position: absolute;
  z-index: 1;
  inset: -80px;
  background: radial-gradient(circle, var(--glowColor) 0%, rgba(0,0,0,0) 70%);
  opacity: 0;
  transform: scale(0.85);
  pointer-events: none;
}
```

```js
// Bloom in
 tl.fromTo("#card-glow",
  { opacity: 0, scale: 0.85 },
  { opacity: 0.32, scale: 1, duration: 0.9, ease: "power2.out" },
  0.4
);
// 3D settle
 tl.fromTo("#card",
  { rotateX: 12, rotateY: -18, scale: 0.92 },
  { rotateX: 0, rotateY: 0, scale: 1, duration: 1.0, ease: "power3.out" },
  0.2
);
```

> See `components/glow-surface.html` and `blocks/glow-card-3d.html`.

---

## 3. KineticText / TypewriterText

### Remotion concept
`KineticText` animates words/phrases with energetic entrances. `TypewriterText` reveals characters one at a time with a cursor.

### HyperFrames equivalent
Use GSAP `fromTo` entrance tweens or an `onUpdate` driver that writes `textContent`.

**Kinetic text** — staggered `fromTo` per phrase:

```js
const phrases = ["Ship", "faster", "with", "motion"];
phrases.forEach((text, i) => {
  const el = document.createElement("span");
  el.className = "phrase";
  el.textContent = text;
  container.appendChild(el);
  tl.fromTo(el,
    { y: 60, opacity: 0, rotateX: -45 },
    { y: 0, opacity: 1, rotateX: 0, duration: 0.55, ease: "back.out(1.6)" },
    0.2 + i * 0.18
  );
});
```

**Typewriter text** — smooth slice with a deterministic cursor blink:

```js
const fullText = "{{yourText}}";
const cursor = document.getElementById("cursor");
const driver = { len: 0 };
tl.to(driver, {
  len: fullText.length,
  duration: fullText.length * 0.07,
  ease: "power1.inOut",
  onUpdate: () => {
    textEl.textContent = fullText.slice(0, Math.floor(driver.len));
  },
}, 0.2);

// Deterministic blink via sin sweep (NOT CSS animation)
const blink = { p: 0 };
tl.to(blink, {
  p: Math.PI * 2 * 8,
  duration: 8,
  ease: "none",
  onUpdate: () => {
    cursor.style.opacity = Math.sin(blink.p) > 0 ? "1" : "0";
  },
}, 0);
```

> See `components/kinetic-text.html`, `components/typewriter-text.html`, and the block versions.

---

## 4. Cursor

### Remotion concept
An animated mouse cursor that moves to a target, clicks, and possibly ripples.

### HyperFrames equivalent
A positioned `<div class="cursor">` + ripple rings, driven by a GSAP timeline. Cursor lives in DOM from `t=0` with `opacity: 0` (no conditional rendering).

```js
// Move
 tl.to(".cursor", { x: targetX, y: targetY, duration: 0.5, ease: "back.out(1.3)" }, 0);
// Click depression
 tl.to(".cursor", { scale: 0.85, duration: 0.08, yoyo: true, repeat: 1 }, 0.55);
tl.to("#cta", { scale: 0.95, duration: 0.08, yoyo: true, repeat: 1 }, 0.55);
// Ripple
 tl.set(".ripple", { opacity: 1 }, 0.55);
tl.fromTo(".ripple",
  { scale: 0, opacity: 1 },
  { scale: 5, opacity: 0, duration: 0.7, ease: "power2.out" },
  0.55
);
```

> See `components/cursor.html`.

---

## 5. GrainOverlay / Vignette / AmbientGlow

These are **paste-in overlay components**. They sit on top of the scene with `pointer-events: none`.

### GrainOverlay
A static or nearly-static film grain texture. In HyperFrames use an inline SVG noise filter or a CSS gradient noise layer at very low opacity. Avoid animated CSS `background-position` loops (they desync from seek).

```html
<div class="grain" aria-hidden="true"></div>
```

```css
.grain {
  position: absolute;
  inset: 0;
  z-index: 999;
  opacity: 0.04;
  pointer-events: none;
  background-image: url("data:image/svg+xml,...noise filter...");
  mix-blend-mode: overlay;
}
```

### Vignette
A pure CSS radial gradient overlay.

```css
.vignette {
  position: absolute;
  inset: 0;
  z-index: 998;
  pointer-events: none;
  background: radial-gradient(circle at 50% 50%, rgba(0,0,0,0) 50%, rgba(0,0,0,0.55) 100%);
}
```

### AmbientGlow
See section 2. Use the bloom layer or the traveling sheen pattern. Peak opacity ≤ 0.45; color darker + more saturated than the hero it backs.

> See `components/grain-overlay.html`, `components/vignette.html`, and `components/ambient-glow.html`.

---

## Props → HyperFrames Variables

| Remotion prop | HyperFrames mechanism |
|---------------|-----------------------|
| `palette: Palette` | CSS `:root` variables or inline `style="--bg: #050505"` on the root |
| `durationInFrames` | `data-duration` in seconds + `data-fps` hint |
| `transition: TransitionType` | GSAP scene-to-scene choreography or `HyperShader` config |
| `direction: Direction` | Signed `x`/`y` values in the transition tween |
| `easing: EasingType` | GSAP ease string (e.g. `"power3.out"`, `"back.out(1.6)"`) |
| `spring: SpringConfig` | `back.out` / `elastic.out` approximations; see `components/easing-map.md` |
| React `children` | Host content slot or inner HTML of a component snippet |

---

## File Map

- `components/*.html` — copy-paste snippets for a single composition.
- `blocks/*.html` — standalone sub-compositions loaded via `data-composition-src`.
- `example/index.html` — runnable host composition demonstrating the components.

---

## Key Differences Users Should Know

1. **No React runtime.** HyperFrames is HTML + GSAP. Props become `data-variable-values` or script constants.
2. **One paused timeline per composition.** Register it at `window.__timelines["<data-composition-id>"]`.
3. **No `repeat: -1`.** All loops must be bounded finite tweens or deterministic `onUpdate` reads of `tl.time()`.
4. **Transitions are scene-to-scene choreography.** Do not fade out a scene before the next one enters; animate both at the same timeline position.
5. **Sub-compositions need `<template>` wrappers** and host `data-composition-id` must exactly match the internal composition ID.
6. **CSS variables are fine for static styling**, but values that HyperFrames captures for shader transitions must be literal (no `var()` on captured elements).
7. **Lint/validate/inspect** are the minimum gates; multi-scene projects also need `snapshot` to catch cross-file mount bugs.
