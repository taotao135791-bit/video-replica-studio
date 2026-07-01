import React, { CSSProperties, ReactNode } from "react";
import { useCurrentFrame, interpolate } from "remotion";
import { Direction, TransitionType, EasingType } from "../shared";
import { easingFromType } from "../shared/easings";

export interface SceneTransitionProps {
  /** Content to transition. */
  children: ReactNode;
  /** Transition type. */
  type?: TransitionType;
  /** Frame when the enter transition starts. */
  enterStartFrame?: number;
  /** Duration of the enter transition. */
  enterDuration?: number;
  /** Frame when the exit transition starts. Omit for no exit. */
  exitStartFrame?: number;
  /** Duration of the exit transition. */
  exitDuration?: number;
  /** Direction for push transitions. */
  direction?: Direction;
  /** Distance in px for push transitions. */
  distance?: number;
  /** Blur amount during transitions. */
  blurAmount?: number;
  /** Easing. */
  easing?: EasingType;
  /** Optional className. */
  className?: string;
  /** Optional inline styles. */
  style?: CSSProperties;
}

export const SceneTransition: React.FC<SceneTransitionProps> = ({
  children,
  type = "push",
  enterStartFrame = 0,
  enterDuration = 20,
  exitStartFrame,
  exitDuration = 20,
  direction = "up",
  distance = 60,
  blurAmount = 10,
  easing = "easeOut",
  className,
  style,
}) => {
  const frame = useCurrentFrame();
  const easingFn = easingFromType(easing);

  const getOffset = (progress: number): { x: number; y: number } => {
    const p = 1 - progress;
    switch (direction) {
      case "up":
        return { x: 0, y: distance * p };
      case "down":
        return { x: 0, y: -distance * p };
      case "left":
        return { x: distance * p, y: 0 };
      case "right":
        return { x: -distance * p, y: 0 };
      default:
        return { x: 0, y: distance * p };
    }
  };

  const enterProgress = interpolate(
    frame,
    [enterStartFrame, enterStartFrame + enterDuration],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const exitProgress =
    typeof exitStartFrame === "number"
      ? interpolate(
          frame,
          [exitStartFrame, exitStartFrame + exitDuration],
          [0, 1],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
        )
      : 0;

  const visibleProgress =
    typeof exitStartFrame === "number"
      ? interpolate(frame, [enterStartFrame + enterDuration, exitStartFrame], [1, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        })
      : 1;

  const enterEased = easingFn(enterProgress);
  const exitEased = easingFn(exitProgress);

  let transform = "";
  let filter = "";
  let clipPath: string | undefined;

  if (type === "push") {
    const enterOffset = getOffset(enterEased);
    const exitOffset = getOffset(exitEased);
    const x = enterOffset.x * (1 - exitEased) + exitOffset.x * exitEased;
    const y = enterOffset.y * (1 - exitEased) + exitOffset.y * exitEased;
    transform = `translate3d(${x}px, ${y}px, 0)`;
    const currentBlur = blurAmount * (1 - enterEased + exitEased);
    filter = `blur(${Math.max(0, currentBlur)}px)`;
  } else if (type === "blur-wipe") {
    const wipe = enterEased * 100 * (1 - exitEased);
    clipPath = `inset(0 ${100 - wipe}% 0 0)`;
    const currentBlur = blurAmount * (1 - enterEased + exitEased);
    filter = `blur(${Math.max(0, currentBlur)}px)`;
  } else if (type === "scale-morph") {
    const scale = 0.92 + enterEased * 0.08 - exitEased * 0.08;
    transform = `scale(${scale})`;
    const currentBlur = blurAmount * (1 - enterEased + exitEased);
    filter = `blur(${Math.max(0, currentBlur)}px)`;
  }

  const opacity = Math.min(enterEased * 1.2, 1) * (1 - exitEased) * visibleProgress;

  return (
    <div
      className={className}
      style={{
        width: "100%",
        height: "100%",
        transform,
        filter,
        clipPath,
        opacity,
        ...style,
      }}
    >
      {children}
    </div>
  );
};
