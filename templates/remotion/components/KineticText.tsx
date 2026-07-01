import React, { CSSProperties } from "react";
import { useCurrentFrame, interpolate } from "remotion";
import { Direction, EasingType } from "../shared";
import { easingFromType } from "../shared/easings";

export interface KineticTextProps {
  /** Text content to animate. */
  text: string;
  /** Split by character or word. */
  splitBy?: "char" | "word";
  /** Frame when animation starts. */
  startFrame?: number;
  /** Duration of each unit's entrance in frames. */
  duration?: number;
  /** Frames between each unit. */
  stagger?: number;
  /** Entrance direction. */
  direction?: Direction;
  /** Maximum blur in px at the start of the entrance. */
  blurAmount?: number;
  /** Travel distance in px. */
  distance?: number;
  /** Easing for each unit. */
  easing?: EasingType;
  /** Color of the text. */
  color?: string;
  /** Font size. */
  fontSize?: number | string;
  /** Font family. */
  fontFamily?: string;
  /** Font weight. */
  fontWeight?: number | string;
  /** Letter spacing. */
  letterSpacing?: number | string;
  /** Line height. */
  lineHeight?: number | string;
  /** Text align. */
  textAlign?: CSSProperties["textAlign"];
  /** Optional className. */
  className?: string;
  /** Optional inline styles on the container. */
  style?: CSSProperties;
}

export const KineticText: React.FC<KineticTextProps> = ({
  text,
  splitBy = "char",
  startFrame = 0,
  duration = 18,
  stagger = 2,
  direction = "up",
  blurAmount = 12,
  distance = 32,
  easing = "backOut",
  color = "#f3f4f6",
  fontSize = 64,
  fontFamily = "system-ui, sans-serif",
  fontWeight = 700,
  letterSpacing = "-0.02em",
  lineHeight = 1.1,
  textAlign = "center",
  className,
  style,
}) => {
  const frame = useCurrentFrame();
  const units = splitBy === "word" ? text.split(/\s+/) : Array.from(text);
  const easingFn = easingFromType(easing);

  const getInitialOffset = (): { x: number; y: number } => {
    switch (direction) {
      case "up":
        return { x: 0, y: distance };
      case "down":
        return { x: 0, y: -distance };
      case "left":
        return { x: distance, y: 0 };
      case "right":
        return { x: -distance, y: 0 };
      default:
        return { x: 0, y: distance };
    }
  };

  const initial = getInitialOffset();

  return (
    <div
      className={className}
      style={{
        color,
        fontSize,
        fontFamily,
        fontWeight,
        letterSpacing,
        lineHeight,
        textAlign,
        display: "flex",
        flexWrap: "wrap",
        justifyContent:
          textAlign === "center"
            ? "center"
            : textAlign === "right"
            ? "flex-end"
            : "flex-start",
        ...style,
      }}
    >
      {units.map((unit, index) => {
        const unitStart = startFrame + index * stagger;
        const unitEnd = unitStart + duration;
        const progress = interpolate(frame, [unitStart, unitEnd], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        const eased = easingFn(progress);

        const x = initial.x * (1 - eased);
        const y = initial.y * (1 - eased);
        const blur = blurAmount * (1 - eased);
        const opacity = Math.min(1, progress * 1.5);

        return (
          <span
            key={`${unit}-${index}`}
            style={{
              display: "inline-block",
              transform: `translate3d(${x}px, ${y}px, 0)`,
              filter: `blur(${blur}px)`,
              opacity,
              whiteSpace: splitBy === "word" ? "pre" : "pre-wrap",
            }}
          >
            {unit}
          </span>
        );
      })}
    </div>
  );
};
