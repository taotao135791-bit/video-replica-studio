import { ReactNode } from "react";

export type EasingType =
  | "linear"
  | "ease"
  | "easeIn"
  | "easeOut"
  | "easeInOut"
  | "backIn"
  | "backOut"
  | "backInOut"
  | "elastic"
  | "bounce";

export type TransitionType = "push" | "blur-wipe" | "scale-morph" | "none";

export type Direction = "up" | "down" | "left" | "right";

export interface SceneConfig {
  id: string;
  durationInFrames: number;
  component: ReactNode;
  /** Optional transition into this scene. Defaults to inherit from CameraRig. */
  transition?: TransitionType;
  /** Optional hold frames at the end of this scene before transitioning. */
  holdFrames?: number;
}

export interface SpringConfig {
  mass?: number;
  damping?: number;
  stiffness?: number;
  overshootClamping?: boolean;
}

export interface Rect {
  width: number;
  height: number;
  x: number;
  y: number;
}

export type Color = string;

export interface Palette {
  background: Color;
  surface: Color;
  surfaceHighlight: Color;
  primary: Color;
  primaryGlow: Color;
  text: Color;
  textMuted: Color;
  accent: Color;
  grain: Color;
}
