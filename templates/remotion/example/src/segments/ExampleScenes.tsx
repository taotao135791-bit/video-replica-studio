import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { KineticText } from "../../../components/KineticText";
import { GlowCard3D } from "../../../components/GlowCard3D";
import { GlowSurface } from "../../../components/GlowSurface";
import { TypewriterText } from "../../../components/TypewriterText";
import { Cursor } from "../../../components/Cursor";
import { GrainOverlay } from "../../../components/GrainOverlay";
import { Vignette } from "../../../components/Vignette";
import { AmbientGlow } from "../../../components/AmbientGlow";
import { SceneTransition } from "../../../components/SceneTransition";
import { defaultDarkPalette } from "../../../shared/palette";

const palette = defaultDarkPalette;

export const SceneHero: React.FC = () => {
  return (
    <AbsoluteFill
      style={{
        background: palette.background,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <AmbientGlow color={palette.primaryGlow} x={30} y={40} size={800} />
      <AmbientGlow color={palette.accent + "55"} x={70} y={60} size={600} />
      <KineticText
        text="Motion, not slides."
        splitBy="word"
        startFrame={6}
        duration={24}
        stagger={5}
        direction="up"
        color={palette.text}
        fontSize={96}
        fontWeight={800}
      />
      <KineticText
        text="Reusable Remotion components with depth, glow, and texture."
        splitBy="word"
        startFrame={36}
        duration={18}
        stagger={2}
        direction="up"
        color={palette.textMuted}
        fontSize={32}
        fontWeight={400}
      />
      <Vignette intensity={0.5} />
      <GrainOverlay opacity={0.05} />
    </AbsoluteFill>
  );
};

export const SceneCard: React.FC = () => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [0, 120], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: palette.background,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <AmbientGlow color={palette.primaryGlow} x={50} y={50} size={900} />
      <SceneTransition type="scale-morph" enterDuration={24}>
        <GlowCard3D
          width={560}
          height={320}
          rotationProgress={progress}
          rotationRangeX={[-6, 6]}
          rotationRangeY={[-10, 10]}
          glowColor={palette.primaryGlow}
          background={palette.surface}
        >
          <KineticText
            text="3D Glow Card"
            startFrame={12}
            duration={16}
            stagger={2}
            color={palette.text}
            fontSize={42}
          />
          <div style={{ height: 16 }} />
          <TypewriterText
            text="Depth, reflection, and sheen — no hard cuts."
            startFrame={30}
            framesPerChar={2}
            color={palette.textMuted}
            fontSize={22}
            fontFamily="system-ui"
          />
        </GlowCard3D>
      </SceneTransition>
      <GrainOverlay opacity={0.04} />
    </AbsoluteFill>
  );
};

export const SceneForm: React.FC = () => {
  return (
    <AbsoluteFill
      style={{
        background: palette.background,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 32,
      }}
    >
      <AmbientGlow color={palette.accent + "55"} x={50} y={45} size={700} />
      <SceneTransition type="push" direction="left" enterDuration={20}>
        <GlowSurface
          width={640}
          height={72}
          borderRadius={36}
          borderWidth={2}
          padding={8}
          glowColor={palette.primaryGlow}
          gradient={`conic-gradient(from 180deg, ${palette.primary} 0deg, ${palette.accent} 120deg, ${palette.primary} 360deg)`}
          surfaceColor={palette.surface}
        >
          <TypewriterText
            text="user@example.com"
            startFrame={12}
            framesPerChar={2}
            color={palette.text}
            fontSize={24}
            fontFamily="system-ui"
          />
        </GlowSurface>
      </SceneTransition>

      <SceneTransition type="push" direction="right" enterDuration={20} enterStartFrame={8}>
        <GlowSurface
          width={240}
          height={64}
          borderRadius={32}
          borderWidth={2}
          glowColor={palette.accent + "88"}
          gradient={`conic-gradient(from 90deg, ${palette.accent} 0deg, ${palette.primary} 180deg, ${palette.accent} 360deg)`}
          surfaceColor={palette.surfaceHighlight}
        >
          <span
            style={{
              color: palette.text,
              fontSize: 20,
              fontWeight: 600,
              fontFamily: "system-ui",
            }}
          >
            Subscribe
          </span>
        </GlowSurface>
      </SceneTransition>

      <Vignette intensity={0.4} />
      <GrainOverlay opacity={0.05} />
    </AbsoluteFill>
  );
};

export const SceneCursor: React.FC = () => {
  const frame = useCurrentFrame();
  const x = interpolate(frame, [0, 100], [200, 1600], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const y = interpolate(frame, [0, 100], [300, 700], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: palette.background,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <AmbientGlow color={palette.primaryGlow} x={50} y={50} size={700} />
      <GlowSurface
        width={480}
        height={80}
        borderRadius={16}
        glowColor={palette.primaryGlow}
        surfaceColor={palette.surface}
      >
        <span style={{ color: palette.textMuted, fontSize: 20, fontFamily: "system-ui" }}>
          Hover me
        </span>
      </GlowSurface>

      <Cursor x={x} y={y} clickFrame={60} color={palette.text} />
      <GrainOverlay opacity={0.04} />
    </AbsoluteFill>
  );
};

export const SceneOutro: React.FC = () => {
  return (
    <AbsoluteFill
      style={{
        background: palette.background,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <AmbientGlow color={palette.accent + "55"} x={50} y={50} size={900} />
      <KineticText
        text="Build anti-PPT videos."
        splitBy="word"
        startFrame={6}
        duration={22}
        stagger={5}
        color={palette.text}
        fontSize={84}
        fontWeight={800}
      />
      <Vignette intensity={0.55} />
      <GrainOverlay opacity={0.05} />
    </AbsoluteFill>
  );
};
