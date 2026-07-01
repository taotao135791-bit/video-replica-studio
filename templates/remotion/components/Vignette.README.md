# Vignette

Subtle dark radial vignette to draw focus toward the center.

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `color` | `string` | `#000000` | Vignette color. |
| `intensity` | `number` | `0.55` | Edge opacity (0-1). |
| `innerRadius` | `number` | `0.4` | Start of the gradient (0-1). |
| `outerRadius` | `number` | `1.0` | End of the gradient (0-1). |
| `className` | `string` | - | Container class. |
| `style` | `CSSProperties` | - | Container styles. |

## Timing contract

- Static overlay; place at the top of a scene or composition.

## Known limits

- Always centered; offset position is not supported.
- Color is converted to hex + alpha; partially transparent colors will be flattened.
