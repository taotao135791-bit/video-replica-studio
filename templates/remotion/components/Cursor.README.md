# Cursor

A mouse cursor graphic with press/click state and an optional ripple ring.

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `x` | `number` | `100` | Horizontal position in px. |
| `y` | `number` | `100` | Vertical position in px. |
| `color` | `string` | `#ffffff` | Cursor color. |
| `size` | `number` | `28` | Cursor size in px. |
| `strokeWidth` | `number` | `2` | Ripple ring thickness. |
| `clickFrame` | `number` | - | Frame when a click happens. |
| `clickDuration` | `number` | `8` | Click animation length. |
| `clickScale` | `number` | `0.85` | Scale during click press. |
| `showRipple` | `boolean` | `true` | Show ripple ring on click. |
| `rotation` | `number` | `-15` | Cursor rotation in degrees. |
| `className` | `string` | - | Container class. |
| `style` | `CSSProperties` | - | Container styles. |

## Timing contract

- Position is absolute; animate `x`/`y` from the parent for movement paths.
- Click scale goes `1 -> clickScale -> 1` over `clickDuration` frames.
- Ripple scales outward and fades during the same window.

## Known limits

- Does not render the OS cursor; it is a decorative overlay.
- For complex paths, compute positions with `interpolate` in the parent and pass them as props.
