# KineticText

Per-character or per-word text entrance with stagger, direction, and motion blur.

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `text` | `string` | required | Text to animate. |
| `splitBy` | `"char" \| "word"` | `"char"` | Splitting mode. |
| `startFrame` | `number` | `0` | First unit entrance start. |
| `duration` | `number` | `18` | Frames for each unit's entrance. |
| `stagger` | `number` | `2` | Frames between units. |
| `direction` | `Direction` | `"up"` | `"up"`, `"down"`, `"left"`, `"right"`. |
| `blurAmount` | `number` | `12` | Starting motion blur in px. |
| `distance` | `number` | `32` | Travel distance in px. |
| `easing` | `EasingType` | `"backOut"` | Entrance easing. |
| `color` | `string` | `#f3f4f6` | Text color. |
| `fontSize` | `number \| string` | `64` | Font size. |
| `fontFamily` | `string` | system-ui | Font family. |
| `fontWeight` | `number \| string` | `700` | Font weight. |
| `letterSpacing` | `number \| string` | `-0.02em` | Letter spacing. |
| `lineHeight` | `number \| string` | `1.1` | Line height. |
| `textAlign` | `CSSProperties["textAlign"]` | `"center"` | Text alignment. |
| `className` | `string` | - | Container class. |
| `style` | `CSSProperties` | - | Container styles. |

## Timing contract

- Unit `i` animates from `startFrame + i * stagger` to `startFrame + i * stagger + duration`.
- Each unit starts blurred, offset by `distance` in the chosen direction, and lands at rest.

## Known limits

- Words are separated by whitespace; punctuation stays attached to the preceding word.
- Very long text with small stagger may exceed the parent composition duration.
