# GrainOverlay

Animated film grain texture overlay.

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `opacity` | `number` | `0.06` | Grain opacity. |
| `blendMode` | `CSSProperties["mixBlendMode"]` | `"overlay"` | CSS blend mode. |
| `baseFrequency` | `number` | `0.85` | `feTurbulence` base frequency. |
| `className` | `string` | - | Container class. |
| `style` | `CSSProperties` | - | Container styles. |

## Timing contract

- Noise seed is driven by `frame % 120`, creating a new grain pattern every frame.
- No entrance; should span the full composition.

## Known limits

- SVG filters can be expensive at high resolution; reduce `baseFrequency` or opacity if rendering is slow.
- The seed loop repeats every 120 frames.
