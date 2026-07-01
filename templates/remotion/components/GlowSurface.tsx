import React, { CSSProperties, ReactNode } from "react";
import { useCurrentFrame, interpolate } from "remotion";

export interface GlowSurfaceProps {
  /** Width in px or CSS length. */
  width?: number | string;
  /** Height in px or CSS length. */
  height?: number | string;
  /** Outer border radius. Default 16. */
  borderRadius?: number;
  /** Thickness of the gradient border. Default 1. */
  borderWidth?: number;
  /** Padding inside the border. Default 0. */
  padding?: number;
  /** Color of the outer glow. */
  glowColor?: string;
  /** Intensity of the outer glow. 0 disables. Default 20. */
  glowIntensity?: number;
  /** Gradient definition for the border. */
  gradient?: string;
  /** Whether to rotate the gradient over time. Default false. */
  animateGradient?: boolean;
  /** Frames for one full gradient rotation. Default 120. */
  animationDuration?: number;
  /** Background of the inner surface. */
  surfaceColor?: string;
  /** Optional inline styles. */
  style?: CSSProperties;
  /** Content. */
  children?: ReactNode;
}

export const GlowSurface: React.FC<GlowSurfaceProps> = ({
  width = "100%",
  height = "100%",
  borderRadius = 16,
  borderWidth = 1,
  padding = 0,
  glowColor = "rgba(59, 130, 246, 0.55)",
  glowIntensity = 20,
  gradient = "conic-gradient(from 180deg at 50% 50%, #3b82f6 0deg, #22d3ee 120deg, #3b82f6 360deg)",
  animateGradient = false,
  animationDuration = 120,
  surfaceColor = "rgba(10, 10, 10, 0.85)",
  style,
  children,
}) => {
  const frame = useCurrentFrame();
  const rotation = animateGradient
    ? interpolate(frame, [0, animationDuration], [0, 360], {
        extrapolateLeft: "extend",
        extrapolateRight: "extend",
      })
    : 0;

  const resolvedWidth = typeof width === "number" ? `${width}px` : width;
  const resolvedHeight = typeof height === "number" ? `${height}px` : height;

  return (
    <div
      style={{
        position: "relative",
        width: resolvedWidth,
        height: resolvedHeight,
        borderRadius,
        padding: borderWidth,
        boxShadow:
          glowIntensity > 0
            ? `0 0 ${glowIntensity}px ${glowColor}, 0 0 ${glowIntensity * 2}px ${glowColor}`
            : undefined,
        overflow: "hidden",
        ...style,
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          borderRadius,
          background: gradient,
          transform: `rotate(${rotation}deg) scale(1.4)`,
          transformOrigin: "center",
        }}
      />
      <div
        style={{
          position: "relative",
          width: "100%",
          height: "100%",
          borderRadius: Math.max(0, borderRadius - borderWidth),
          background: surfaceColor,
          padding,
          boxSizing: "border-box",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        {children}
      </div>
    </div>
  );
};
