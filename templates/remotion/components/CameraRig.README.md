# CameraRig

A unified 3D camera system that arranges scenes along the Z axis and pushes through them continuously, replacing hard cuts with depth-driven motion.

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `scenes` | `SceneConfig[]` | required | Ordered scenes. Each needs `id`, `durationInFrames`, and `component`. |
| `zStep` | `number` | `1200` | Distance between scene planes on the Z axis. |
| `perspective` | `number` | `1200` | CSS `perspective` value. |
| `fadeDepth` | `number` | `1` | How quickly non-focused scenes fade. `0` disables depth fade. |
| `travelEasing` | `(t: number) => number` | `cameraPushEasing` | Easing for camera travel between scene centers. |
| `transition` | `TransitionType` | `"push"` | `"push"`, `"blur-wipe"`, `"scale-morph"`, or `"none"`. |
| `tailFrames` | `number` | `0` | Extra frames after the last scene. |
| `children` | `ReactNode` | - | Global overlay rendered on top of all scenes. |
| `className` | `string` | - | Outer container class. |
| `style` | `CSSProperties` | - | Outer container styles. |

## Timing contract

- Total duration = sum of `durationInFrames` + `holdFrames` for each scene.
- The camera travels from scene index `i * zStep` to `(i + 1) * zStep` over the scene's duration.
- Scenes behind or ahead of the camera fade and blur based on relative depth.
- Boundary overlays for `blur-wipe` and `scale-morph` play across the scene join.

## Known limits

- Scenes are rendered all at once; very long scene lists may impact performance.
- `blur-wipe` and `scale-morph` overlays are opinionated and do not mask scene content pixel-perfectly.
- Scene components must manage their own internal entrance timing.
