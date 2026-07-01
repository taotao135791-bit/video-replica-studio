import React, { CSSProperties, ReactNode, useMemo } from "react";
import {
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  AbsoluteFill,
} from "remotion";
import { SceneConfig, TransitionType } from "../shared";
import { cameraPushEasing } from "../shared/easings";

export interface CameraRigProps {
  /** Ordered scene definitions. Total duration is derived from scenes. */
  scenes: SceneConfig[];
  /** Distance between scenes on the Z axis. Default 1200. */
  zStep?: number;
  /** CSS perspective value. Default 1200. */
  perspective?: number;
  /** How quickly distant scenes fade. 0 = no fade, 1 = normal, >1 = faster. Default 1. */
  fadeDepth?: number;
  /** Easing for camera travel between scene centers. */
  travelEasing?: (t: number) => number;
  /** Optional boundary transition applied to every scene change unless overridden. */
  transition?: TransitionType;
  /** Frames to add as a safety buffer after the last scene. Default 0. */
  tailFrames?: number;
  /** Optional global layer rendered on top of all scenes. */
  children?: ReactNode;
  /** Optional className on the outer container. */
  className?: string;
  /** Optional inline styles on the outer container. */
  style?: CSSProperties;
}

interface SceneBoundary {
  scene: SceneConfig;
  start: number;
  end: number;
  z: number;
}

export const CameraRig: React.FC<CameraRigProps> = ({
  scenes,
  zStep = 1200,
  perspective = 1200,
  fadeDepth = 1,
  travelEasing = cameraPushEasing,
  transition = "push",
  tailFrames = 0,
  children,
  className,
  style,
}) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();

  const boundaries = useMemo<SceneBoundary[]>(() => {
    let cursor = 0;
    return scenes.map((scene, index) => {
      const hold = scene.holdFrames ?? 0;
      const start = cursor;
      const end = cursor + scene.durationInFrames + hold;
      cursor = end;
      return { scene, start, end, z: index * zStep };
    });
  }, [scenes, zStep]);

  const totalDuration = boundaries[boundaries.length - 1]?.end ?? 0;

  const cameraZ = useMemo(() => {
    if (boundaries.length === 0) return 0;

    const clampedFrame = Math.max(0, Math.min(frame, totalDuration + tailFrames));

    // Find the segment the frame belongs to, allowing the last frame to map to the end.
    for (let i = 0; i < boundaries.length; i++) {
      const { start, end, z } = boundaries[i];
      if (clampedFrame >= start && clampedFrame <= end) {
        const progress =
          end === start ? 0 : (clampedFrame - start) / (end - start);
        const eased = travelEasing(progress);
        return z + eased * zStep;
      }
    }

    return boundaries[boundaries.length - 1].z + zStep;
  }, [boundaries, frame, totalDuration, tailFrames, travelEasing, zStep]);

  return (
    <AbsoluteFill
      className={className}
      style={{
        background: "transparent",
        perspective,
        perspectiveOrigin: "50% 50%",
        overflow: "hidden",
        ...style,
      }}
    >
      <div
        style={{
          position: "absolute",
          left: width / 2,
          top: height / 2,
          width: 0,
          height: 0,
          transformStyle: "preserve-3d",
        }}
      >
        {boundaries.map(({ scene, z }) => {
          const relativeZ = z - cameraZ;
          const normalizedDepth = Math.max(
            0,
            Math.min(1, Math.abs(relativeZ) / Math.max(1, zStep))
          );
          const opacity = 1 - normalizedDepth * Math.min(1, fadeDepth);
          const blur = normalizedDepth * 6;
          const scale = 1 - normalizedDepth * 0.08;

          return (
            <div
              key={scene.id}
              style={{
                position: "absolute",
                left: -width / 2,
                top: -height / 2,
                width,
                height,
                transform: `translateZ(${relativeZ}px) scale(${scale})`,
                opacity,
                filter: `blur(${blur}px)`,
                transformStyle: "preserve-3d",
                pointerEvents: opacity < 0.05 ? "none" : "auto",
              }}
            >
              {scene.component}
            </div>
          );
        })}
      </div>

      {transition !== "push" && transition !== "none" && (
        <BoundaryTransitionOverlay boundaries={boundaries} frame={frame} type={transition} />
      )}

      {children}
    </AbsoluteFill>
  );
};

const BoundaryTransitionOverlay: React.FC<{
  boundaries: SceneBoundary[];
  frame: number;
  type: Exclude<TransitionType, "push" | "none">;
}> = ({ boundaries, frame, type }) => {
  const { width, height } = useVideoConfig();

  // Find an active transition window around a scene boundary.
  for (let i = 0; i < boundaries.length - 1; i++) {
    const end = boundaries[i].end;
    const start = boundaries[i + 1].start;
    const duration = Math.max(1, end - start);
    if (frame >= start && frame <= end + 12) {
      const progress = interpolate(
        frame,
        [start, end + 12],
        [0, 1],
        { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
      );

      if (type === "blur-wipe") {
        const x = progress * (width * 1.2) - width * 0.1;
        return (
          <AbsoluteFill
            style={{
              background: `linear-gradient(90deg, transparent 0%, rgba(0,0,0,0.85) ${x}px, black ${x + 80}px)`,
              mixBlendMode: "multiply",
              pointerEvents: "none",
            }}
          />
        );
      }

      if (type === "scale-morph") {
        const scale = interpolate(progress, [0, 0.5, 1], [1, 1.08, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        return (
          <AbsoluteFill
            style={{
              boxShadow: "inset 0 0 120px rgba(0,0,0,0.8)",
              transform: `scale(${scale})`,
              pointerEvents: "none",
            }}
          />
        );
      }
    }
  }

  return null;
};
