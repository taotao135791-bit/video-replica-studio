import React, { CSSProperties } from "react";
import { useCurrentFrame, interpolate } from "remotion";

export interface AmbientGlowProps {
  /** Glow color. */
  color?: string;
  /** Horizontal position as percentage. Default 50. */
  x?: number;
  /** Vertical position as percentage. Default 50. */
  y?: number;
  /** Size in px. Default 600. */
  size?: number;
  /** Base opacity. Default 0.35. */
  opacity?: number;
  /** Pulsing opacity amplitude. 0 disables. Default 0.1. */
  pulseAmount?: number;
  /** Pulsing duration in frames. Default 180. */
  pulseDuration?: number;
  /** Optional className. */
  className?: string;
  /** Optional inline styles. */
  style?: CSSProperties;
}

export const AmbientGlow: React.FC<AmbientGlowProps> = ({
  color = "rgba(59, 130, 246, 0.55)",
  x = 50,
  y = 50,
  size = 600,
  opacity = 0.35,
  pulseAmount = 0.1,
  pulseDuration = 180,
  className,
  style,
}) => {
  const frame = useCurrentFrame();

  const pulse = pulseAmount
    ? interpolate(frame, [0, pulseDuration], [0, Math.PI * 2], {
        extrapolateLeft: "extend",
        extrapolateRight: "extend",
      })
    : 0;

  const currentOpacity = opacity + Math.sin(pulse) * pulseAmount;

  return (
    <div
      className={className}
      style={{
        position: "absolute",
        left: `${x}%`,
        top: `${y}%`,
        width: size,
        height: size,
        transform: "translate(-50%, -50%)",
        pointerEvents: "none",
        background: `radial-gradient(circle, ${color} 0%, transparent 70%)`,
        opacity: currentOpacity,
        filter: "blur(40px)",
        ...style,
      }}
    />
  );
};
