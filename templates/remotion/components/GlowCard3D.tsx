import React, { CSSProperties, ReactNode } from "react";
import { useCurrentFrame, interpolate } from "remotion";

export interface GlowCard3DProps {
  width?: number | string;
  height?: number | string;
  borderRadius?: number;
  background?: string;
  /** Static rotation in degrees. Use with useCurrentFrame for animation. */
  rotationX?: number;
  rotationY?: number;
  /** Optional frame-based rotation override. If provided, rotationX/Y are ignored. */
  rotationProgress?: number;
  rotationRangeX?: [number, number];
  rotationRangeY?: [number, number];
  glowColor?: string;
  glowIntensity?: number;
  reflectionOpacity?: number;
  /** Enable a moving sheen highlight. */
  sheen?: boolean;
  sheenColor?: string;
  sheenDuration?: number;
  /** Scale factor. */
  scale?: number;
  style?: CSSProperties;
  children?: ReactNode;
}

export const GlowCard3D: React.FC<GlowCard3DProps> = ({
  width = 320,
  height = 200,
  borderRadius = 24,
  background = "rgba(20, 20, 25, 0.9)",
  rotationX = 0,
  rotationY = 0,
  rotationProgress,
  rotationRangeX = [-8, 8],
  rotationRangeY = [-8, 8],
  glowColor = "rgba(59, 130, 246, 0.5)",
  glowIntensity = 30,
  reflectionOpacity = 0.12,
  sheen = true,
  sheenColor = "rgba(255, 255, 255, 0.15)",
  sheenDuration = 180,
  scale = 1,
  style,
  children,
}) => {
  const frame = useCurrentFrame();

  const rx =
    typeof rotationProgress === "number"
      ? interpolate(
          rotationProgress,
          [0, 1],
          rotationRangeX,
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
        )
      : rotationX;

  const ry =
    typeof rotationProgress === "number"
      ? interpolate(
          rotationProgress,
          [0, 1],
          rotationRangeY,
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
        )
      : rotationY;

  const sheenPosition = sheen
    ? interpolate(frame, [0, sheenDuration], [-150, 150], {
        extrapolateLeft: "extend",
        extrapolateRight: "extend",
      })
    : 0;

  const resolvedWidth = typeof width === "number" ? `${width}px` : width;
  const resolvedHeight = typeof height === "number" ? `${height}px` : height;

  return (
    <div
      style={{
        width: resolvedWidth,
        height: resolvedHeight,
        borderRadius,
        background,
        transform: `perspective(1000px) rotateX(${rx}deg) rotateY(${ry}deg) scale(${scale})`,
        transformStyle: "preserve-3d",
        boxShadow:
          glowIntensity > 0
            ? `0 0 ${glowIntensity}px ${glowColor}, 0 ${glowIntensity / 2}px ${glowIntensity * 2}px rgba(0,0,0,0.45)`
            : `0 20px 60px rgba(0,0,0,0.45)`,
        position: "relative",
        overflow: "hidden",
        ...style,
      }}
    >
      {reflectionOpacity > 0 && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            borderRadius,
            background:
              "linear-gradient(135deg, rgba(255,255,255,0.18) 0%, transparent 40%, transparent 60%, rgba(255,255,255,0.06) 100%)",
            opacity: reflectionOpacity,
            pointerEvents: "none",
          }}
        />
      )}

      {sheen && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            borderRadius,
            background: `linear-gradient(105deg, transparent 40%, ${sheenColor} 50%, transparent 60%)`,
            backgroundSize: "200% 200%",
            backgroundPosition: `${sheenPosition}% 50%`,
            opacity: 0.8,
            pointerEvents: "none",
          }}
        />
      )}

      <div
        style={{
          position: "relative",
          width: "100%",
          height: "100%",
          boxSizing: "border-box",
          padding: 24,
        }}
      >
        {children}
      </div>
    </div>
  );
};
