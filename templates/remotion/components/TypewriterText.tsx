import React, { CSSProperties } from "react";
import { useCurrentFrame, interpolate } from "remotion";

export interface TypewriterTextProps {
  /** Text content to type out. */
  text: string;
  /** Frame when typing starts. */
  startFrame?: number;
  /** Frames per character. Lower is faster. */
  framesPerChar?: number;
  /** Color of the text. */
  color?: string;
  /** Font size. */
  fontSize?: number | string;
  /** Font family. */
  fontFamily?: string;
  /** Font weight. */
  fontWeight?: number | string;
  /** Cursor color. */
  cursorColor?: string;
  /** Cursor width in px. */
  cursorWidth?: number;
  /** Whether to show the blinking cursor. */
  showCursor?: boolean;
  /** Frames for one full cursor blink. */
  cursorBlinkSpeed?: number;
  /** Optional className. */
  className?: string;
  /** Optional inline styles. */
  style?: CSSProperties;
}

export const TypewriterText: React.FC<TypewriterTextProps> = ({
  text,
  startFrame = 0,
  framesPerChar = 3,
  color = "#f3f4f6",
  fontSize = 32,
  fontFamily = "monospace",
  fontWeight = 400,
  cursorColor = "#22d3ee",
  cursorWidth = 3,
  showCursor = true,
  cursorBlinkSpeed = 20,
  className,
  style,
}) => {
  const frame = useCurrentFrame();

  const elapsed = Math.max(0, frame - startFrame);
  const charCount = Math.min(
    text.length,
    Math.floor(elapsed / Math.max(1, framesPerChar))
  );
  const visibleText = text.slice(0, charCount);

  const cursorPhase = (frame % cursorBlinkSpeed) / cursorBlinkSpeed;
  const cursorOpacity = interpolate(
    cursorPhase,
    [0, 0.5, 1],
    [1, 0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <div
      className={className}
      style={{
        color,
        fontSize,
        fontFamily,
        fontWeight,
        display: "inline-flex",
        alignItems: "baseline",
        ...style,
      }}
    >
      <span>{visibleText}</span>
      {showCursor && (
        <span
          style={{
            display: "inline-block",
            width: cursorWidth,
            height: "1em",
            background: cursorColor,
            marginLeft: 4,
            opacity: cursorOpacity,
            verticalAlign: "text-bottom",
          }}
        />
      )}
    </div>
  );
};
