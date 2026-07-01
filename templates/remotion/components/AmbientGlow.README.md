# AmbientGlow

Large, blurred radial glow for atmospheric lighting.

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `color` | `string` | `rgba(59, 130, 246, 0.55)` | Glow color. |
| `x` | `number` | `50` | Horizontal position as percentage. |
| `y` | `number` | `50` | Vertical position as percentage. |
| `size` | `number` | `600` | Glow diameter in px. |
| `opacity` | `number` | `0.35` | Base opacity. |
| `pulseAmount` | `number` | `0.1` | Opacity oscillation amplitude. `0` disables. |
| `pulseDuration` | `number` | `180` | Frames for one pulse cycle. |
| `className` | `string` | - | Container class. |
| `style` | `CSSProperties` | - | Container styles. |

## Timing contract

- Opacity pulses as `opacity + sin(frame / pulseDuration * 2π) * pulseAmount`.
- Position is static; animate via the parent if needed.

## Known limits

- Large blurred divs can be GPU-intensive; consider lowering `size` or `opacity`.
- The glow is always radial.
