import React, { CSSProperties } from "react";

export interface VignetteProps {
  /** Vignette color. Default black. */
  color?: string;
  /** Intensity from 0 to 1. Default 0.55. */
  intensity?: number;
  /** Inner radius of the gradient. 0 - 1. Default 0.4. */
  innerRadius?: number;
  /** Outer radius of the gradient. 0 - 1. Default 1.0. */
  outerRadius?: number;
  /** Optional className. */
  className?: string;
  /** Optional inline styles. */
  style?: CSSProperties;
}

export const Vignette: React.FC<VignetteProps> = ({
  color = "#000000",
  intensity = 0.55,
  innerRadius = 0.4,
  outerRadius = 1.0,
  className,
  style,
}) => {
  const transparentColor = `${color}00`;
  const opaqueColor = `${color}${Math.round(intensity * 255)
    .toString(16)
    .padStart(2, "0")}`;

  return (
    <div
      className={className}
      style={{
        position: "absolute",
        inset: 0,
        pointerEvents: "none",
        background: `radial-gradient(circle at 50% 50%, ${transparentColor} ${innerRadius * 100}%, ${opaqueColor} ${outerRadius * 100}%)`,
        ...style,
      }}
    />
  );
};
