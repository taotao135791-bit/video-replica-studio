import React from "react";
import { Composition } from "remotion";
import { CameraRig } from "../../components/CameraRig";
import {
  SceneHero,
  SceneCard,
  SceneForm,
  SceneCursor,
  SceneOutro,
} from "./segments/ExampleScenes";

const FPS = 30;

const scenes = [
  { id: "hero", durationInFrames: 90, component: <SceneHero /> },
  { id: "card", durationInFrames: 120, component: <SceneCard /> },
  { id: "form", durationInFrames: 120, component: <SceneForm /> },
  { id: "cursor", durationInFrames: 100, component: <SceneCursor /> },
  { id: "outro", durationInFrames: 90, component: <SceneOutro /> },
];

const totalDuration = scenes.reduce((sum, s) => sum + s.durationInFrames, 0);

export const Root: React.FC = () => {
  return (
    <Composition
      id="AntiPPTDemo"
      component={AntiPPTDemo}
      durationInFrames={totalDuration}
      fps={FPS}
      width={1920}
      height={1080}
    />
  );
};

const AntiPPTDemo: React.FC = () => {
  return (
    <CameraRig
      scenes={scenes}
      zStep={1400}
      perspective={1400}
      fadeDepth={1.2}
    />
  );
};
