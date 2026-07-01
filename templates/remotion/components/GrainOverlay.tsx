import React, { CSSProperties } from "react";
import { useCurrentFrame } from "remotion";

export interface GrainOverlayProps {
  /** Opacity of the grain. Default 0.06. */
  opacity?: number;
  /** Blend mode. Default 'overlay'. */
  blendMode?: CSSProperties["mixBlendMode"];
  /** Base frequency for the noise. Higher = finer grain. Default 0.85. */
  baseFrequency?: number;
  /** Optional className. */
  className?: string;
  /** Optional inline styles. */
  style?: CSSProperties;
}

export const GrainOverlay: React.FC<GrainOverlayProps> = ({
  opacity = 0.06,
  blendMode = "overlay",
  baseFrequency = 0.85,
  className,
  style,
}) => {
  const frame = useCurrentFrame();
  const seed = 1 + (frame % 120);

  return (
    <div
      className={className}
      style={{
        position: "absolute",
        inset: 0,
        pointerEvents: "none",
        opacity,
        mixBlendMode: blendMode,
        ...style,
      }}
    >
      <svg width="100%" height="100%">
        <filter id={`grain-filter-${seed}`}>
          <feTurbulence
            type="fractalNoise"
            baseFrequency={baseFrequency}
            numOctaves="3"
            seed={seed}
            stitchTiles="stitch"
          />
        </filter>
        <rect width="100%" height="100%" filter={`url(#grain-filter-${seed})`} />
      </svg>
    </div>
  );
};
