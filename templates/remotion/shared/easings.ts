import { Easing } from "remotion";
import { EasingType } from "./types";

const backOut = Easing.bezier(0.34, 1.56, 0.64, 1);
const backIn = Easing.bezier(0.6, -0.28, 0.735, 0.045);
const backInOut = Easing.bezier(0.68, -0.55, 0.265, 1.55);

export const easingFromType = (type: EasingType = "easeOut"): ((t: number) => number) => {
  switch (type) {
    case "linear":
      return Easing.linear;
    case "ease":
      return Easing.ease;
    case "easeIn":
      return Easing.in(Easing.ease);
    case "easeOut":
      return Easing.out(Easing.ease);
    case "easeInOut":
      return Easing.inOut(Easing.ease);
    case "backIn":
      return backIn;
    case "backOut":
      return backOut;
    case "backInOut":
      return backInOut;
    case "elastic":
      return Easing.elastic(1);
    case "bounce":
      return Easing.bounce;
    default:
      return Easing.out(Easing.ease);
  }
};

/**
 * Cubic bezier that feels like a camera push: slow start, fast middle, gentle settle.
 */
export const cameraPushEasing = Easing.bezier(0.16, 1, 0.3, 1);

/**
 * Smooth secondary motion easing for elements that should feel weighty.
 */
export const softOvershoot = Easing.bezier(0.34, 1.4, 0.64, 1);
