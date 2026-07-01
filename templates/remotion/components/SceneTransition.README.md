# SceneTransition

Reusable entrance/exit wrapper for scenes or elements: push, blur-wipe, or scale-morph.

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `children` | `ReactNode` | required | Content to wrap. |
| `type` | `TransitionType` | `"push"` | `"push"`, `"blur-wipe"`, `"scale-morph"`, `"none"`. |
| `enterStartFrame` | `number` | `0` | Entrance start frame. |
| `enterDuration` | `number` | `20` | Entrance duration. |
| `exitStartFrame` | `number` | - | Exit start frame; omit for no exit. |
| `exitDuration` | `number` | `20` | Exit duration. |
| `direction` | `Direction` | `"up"` | Push direction. |
| `distance` | `number` | `60` | Push distance in px. |
| `blurAmount` | `number` | `10` | Blur during transitions. |
| `easing` | `EasingType` | `"easeOut"` | Entrance/exit easing. |
| `className` | `string` | - | Wrapper class. |
| `style` | `CSSProperties` | - | Wrapper styles. |

## Timing contract

- Enter: `frame` maps from `enterStartFrame` to `enterStartFrame + enterDuration`.
- Exit: `frame` maps from `exitStartFrame` to `exitStartFrame + exitDuration`.
- Between enter and exit, the element is fully visible.

## Known limits

- `blur-wipe` uses `clip-path`, which may clip nested 3D transforms.
- Exit must be explicitly scheduled; the component does not auto-exit at scene end.
