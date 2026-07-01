# GlowCard3D

A 3D card with perspective rotation, outer glow, reflection overlay, and optional moving sheen.

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `width` | `number \| string` | `320` | Card width. |
| `height` | `number \| string` | `200` | Card height. |
| `borderRadius` | `number` | `24` | Border radius. |
| `background` | `string` | `rgba(20,20,25,0.9)` | Card fill. |
| `rotationX` | `number` | `0` | Static X rotation in degrees. |
| `rotationY` | `number` | `0` | Static Y rotation in degrees. |
| `rotationProgress` | `number` | - | Optional 0-1 progress; overrides `rotationX/Y`. |
| `rotationRangeX` | `[number, number]` | `[-8, 8]` | X range when using `rotationProgress`. |
| `rotationRangeY` | `[number, number]` | `[-8, 8]` | Y range when using `rotationProgress`. |
| `glowColor` | `string` | `rgba(59,130,246,0.5)` | Glow color. |
| `glowIntensity` | `number` | `30` | Glow spread. |
| `reflectionOpacity` | `number` | `0.12` | Specular reflection strength. |
| `sheen` | `boolean` | `true` | Enable moving sheen. |
| `sheenColor` | `string` | `rgba(255,255,255,0.15)` | Sheen highlight color. |
| `sheenDuration` | `number` | `180` | Frames for one sheen pass. |
| `scale` | `number` | `1` | Card scale. |
| `style` | `CSSProperties` | - | Outer container styles. |
| `children` | `ReactNode` | - | Card content. |

## Timing contract

- Sheen position is `interpolate(frame, [0, sheenDuration], [-150%, 150%])`.
- For dynamic rotation, compute `rotationProgress` from the parent timeline and pass it in.

## Known limits

- Perspective is fixed at `1000px`; expose via prop if you need a different value.
- Reflection is a static gradient, not environment-aware.
