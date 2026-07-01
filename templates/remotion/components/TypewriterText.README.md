# TypewriterText

Typing effect with a blinking caret.

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `text` | `string` | required | Text to type. |
| `startFrame` | `number` | `0` | Typing start frame. |
| `framesPerChar` | `number` | `3` | Frames per character. Lower is faster. |
| `color` | `string` | `#f3f4f6` | Text color. |
| `fontSize` | `number \| string` | `32` | Font size. |
| `fontFamily` | `string` | `monospace` | Font family. |
| `fontWeight` | `number \| string` | `400` | Font weight. |
| `cursorColor` | `string` | `#22d3ee` | Caret color. |
| `cursorWidth` | `number` | `3` | Caret width in px. |
| `showCursor` | `boolean` | `true` | Show blinking cursor. |
| `cursorBlinkSpeed` | `number` | `20` | Frames for one full blink. |
| `className` | `string` | - | Container class. |
| `style` | `CSSProperties` | - | Container styles. |

## Timing contract

- Character `n` appears at `startFrame + n * framesPerChar`.
- Cursor blinks continuously with `cursorBlinkSpeed`.

## Known limits

- Only reveals characters left-to-right; no delete/backspace animation.
- Cursor height matches `1em`, which depends on the chosen font.
