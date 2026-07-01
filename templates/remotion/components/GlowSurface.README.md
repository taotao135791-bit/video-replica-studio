# GlowSurface

A gradient-border surface with outer glow, useful for input bars, buttons, and highlighted panels.

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `width` | `number \| string` | `"100%"` | Surface width. |
| `height` | `number \| string` | `"100%"` | Surface height. |
| `borderRadius` | `number` | `16` | Outer border radius. |
| `borderWidth` | `number` | `1` | Gradient border thickness. |
| `padding` | `number` | `0` | Inner padding. |
| `glowColor` | `string` | `rgba(59, 130, 246, 0.55)` | Outer glow color. |
| `glowIntensity` | `number` | `20` | Glow spread. `0` disables. |
| `gradient` | `string` | conic gradient | CSS gradient for the animated border. |
| `animateGradient` | `boolean` | `false` | Rotate the gradient over time. |
| `animationDuration` | `number` | `120` | Frames for one full rotation. |
| `surfaceColor` | `string` | `rgba(10,10,10,0.85)` | Inner fill color. |
| `style` | `CSSProperties` | - | Outer container styles. |
| `children` | `ReactNode` | - | Content inside the surface. |

## Timing contract

- Gradient rotation is frame-driven via `frame / animationDuration * 360deg`.
- No entrance animation is built in; wrap with `SceneTransition` if needed.

## Known limits

- CSS `transform: rotate()` on the gradient means the gradient must be large enough to avoid visible edges; the component scales it 1.4x.
- Heavy glow can reduce perceived sharpness on thin borders.
