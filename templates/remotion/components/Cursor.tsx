import React, { CSSProperties } from "react";
import { useCurrentFrame, interpolate } from "remotion";

export interface CursorProps {
  /** Horizontal position in px. */
  x?: number;
  /** Vertical position in px. */
  y?: number;
  /** Cursor color. */
  color?: string;
  /** Cursor size in px. Default 28. */
  size?: number;
  /** Stroke width. Default 2. */
  strokeWidth?: number;
  /** Frame at which a click occurs. Omit for no click animation. */
  clickFrame?: number;
  /** Duration of the click press in frames. Default 8. */
  clickDuration?: number;
  /** Scale of the cursor during click. Default 0.85. */
  clickScale?: number;
  /** Show a ripple ring on click. Default true. */
  showRipple?: boolean;
  /** Rotation of the cursor in degrees. Default -15. */
  rotation?: number;
  /** Optional className. */
  className?: string;
  /** Optional inline styles. */
  style?: CSSProperties;
}

export const Cursor: React.FC<CursorProps> = ({
  x = 100,
  y = 100,
  color = "#ffffff",
  size = 28,
  strokeWidth = 2,
  clickFrame,
  clickDuration = 8,
  clickScale = 0.85,
  showRipple = true,
  rotation = -15,
  className,
  style,
}) => {
  const frame = useCurrentFrame();

  const isClickDefined = typeof clickFrame === "number";
  const clickProgress = isClickDefined
    ? interpolate(
        frame,
        [clickFrame, clickFrame + clickDuration],
        [0, 1],
        { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
      )
    : 0;

  const pressScale = isClickDefined
    ? interpolate(clickProgress, [0, 0.3, 1], [1, clickScale, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    : 1;

  const rippleScale = isClickDefined
    ? interpolate(clickProgress, [0, 1], [0.5, 2.5], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    : 0;

  const rippleOpacity = isClickDefined
    ? interpolate(clickProgress, [0, 0.4, 1], [0, 0.35, 0], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    : 0;

  return (
    <div
      className={className}
      style={{
        position: "absolute",
        left: x,
        top: y,
        width: size,
        height: size,
        transform: `translate(-10%, -10%) rotate(${rotation}deg) scale(${pressScale})`,
        transformOrigin: "0 0",
        pointerEvents: "none",
        ...style,
      }}
    >
      {showRipple && rippleOpacity > 0 && (
        <div
          style={{
            position: "absolute",
            left: size / 2,
            top: size / 2,
            width: size,
            height: size,
            borderRadius: "50%",
            border: `${strokeWidth}px solid ${color}`,
            transform: `translate(-50%, -50%) scale(${rippleScale})`,
            opacity: rippleOpacity,
          }}
        />
      )}

      <svg
        width={size}
        height={size}
        viewBox="0 0 24 24"
        fill={color}
        style={{ display: "block" }}
      >
        <path d="M5.5 3.21V20.8c0 .45.54.67.85.35l4.86-4.86a.5.5 0 0 1 .35-.15h6.87a.5.5 0 0 0 .35-.85L6.35 2.85a.5.5 0 0 0-.85.36Z" />
      </svg>
    </div>
  );
};
