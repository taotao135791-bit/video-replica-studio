# GSAP SVG 自由变换参考

HyperFrames 里的 SVG 动画应该优先用 GSAP 实现，而不是 CSS animation / transition。原因是：

1. **可 seek / 确定性**：GSAP `timeline` 可以被暂停、回退、精确 scrub，适合视频渲染管线；CSS animation 很难做逐帧控制。
2. **跨浏览器 transform-origin**：SVG 元素的 CSS `transform-origin` 在不同浏览器里行为不一致，GSAP 的 `transformOrigin` / `svgOrigin` 是稳定的。
3. **高级能力**：沿路径运动（MotionPath）、描边生长（DrawSVG）、形状 morph（MorphSVG）用 GSAP 插件几行代码就能搞定，CSS 几乎做不到。

> GSAP 所有插件现在都是免费的（包括 SplitText、MorphSVG、DrawSVG、MotionPath 等），只需从公共 npm/CDN 加载即可，不需要 Club GSAP 认证或私有 registry。

---

## 前置：插件注册

使用任何插件前都必须注册一次。HyperFrames 示例已在 HTML head 加载 GSAP 核心：

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
```

如果需要插件，额外加载并注册：

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/MotionPathPlugin.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/DrawSVGPlugin.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/MorphSVGPlugin.min.js"></script>
<script>
  gsap.registerPlugin(MotionPathPlugin, DrawSVGPlugin, MorphSVGPlugin);
</script>
```

---

## 基础自由变换

GSAP 对 SVG 同样支持 transform aliases，优先用它们而不是直接写 `transform` 字符串。

```javascript
// 旋转、缩放、位移
gsap.to("#svg-logo", {
  rotation: 360,
  scale: 1.2,
  x: 100,
  y: -50,
  duration: 1.2,
  ease: "power3.inOut",
});
```

### 控制变换中心

```javascript
// 以元素自身中心为轴旋转
// 对 SVG 元素建议使用 transformOrigin 字符串
gsap.to("#gear", {
  rotation: 90,
  transformOrigin: "50% 50%", // 元素坐标系内的中心
  duration: 1,
});

// 让所有 SVG 元素围绕 SVG 全局坐标系里的同一点旋转
// 注意：svgOrigin 和 transformOrigin 只能二选一
gsap.to(".orbit", {
  rotation: 180,
  svgOrigin: "960 540", // SVG 全局坐标，无百分比
  duration: 2,
});
```

### 定向旋转

避免旋转时“绕远路”：

```javascript
gsap.to("#arrow", {
  rotation: "-170_short", // 自动选择最短路径
  duration: 0.8,
});
```

---

## 沿路径运动（MotionPathPlugin）

让元素沿 SVG `<path>` 运动，并自动对齐切线方向。

```javascript
const tl = gsap.timeline({ paused: true });

tl.to("#dot", {
  duration: 3,
  ease: "none",
  motionPath: {
    path: "#route",
    align: "#route",
    alignOrigin: [0.5, 0.5],
    autoRotate: true,
    curviness: 1.25,
  },
});
```

| 配置 | 作用 |
|------|------|
| `path` | SVG path 元素、选择器或 path data 字符串 |
| `align` | 把目标对齐到 path（通常和 `path` 用同一个） |
| `alignOrigin` | 对齐原点，`[0.5, 0.5]` 表示元素中心 |
| `autoRotate` | 元素自动沿切线旋转 |
| `curviness` | 路径平滑度，0 为直线，1 为原 path，>1 更平滑 |
| `start` / `end` | 运动起点/终点比例，例如 `0.2` 到 `0.8` |

---

## 描边生长动画（DrawSVGPlugin）

让 SVG 线条像被画出来一样生长。目标元素必须有可见的 `stroke` 和 `stroke-width`。

```javascript
const tl = gsap.timeline({ paused: true });

// 从 0 到完整描边
tl.from("#line", {
  drawSVG: 0,
  duration: 1.5,
  ease: "power2.inOut",
});

// 从中间向两端生长
// drawSVG 值描述“可见区段”："start end"
tl.fromTo(
  "#line",
  { drawSVG: "50% 50%" },
  { drawSVG: "0% 100%", duration: 1.5, ease: "power2.inOut" }
);
```

> 如果不用 DrawSVGPlugin，也可以手动动画 `stroke-dashoffset`，但 DrawSVG 更稳定，且会自动处理多段 path 的怪异行为。

---

## 形状 Morph（MorphSVGPlugin）

把一种 SVG 形状平滑变成另一种。起始形状和目标形状的点数可以不同。

```javascript
const tl = gsap.timeline({ paused: true });

// 先把 circle/rect/ellipse/line/polygon/polyline 转成 path（如果需要）
MorphSVGPlugin.convertToPath("#start-shape");

// 目标可以是选择器、元素或 raw path data
tl.to("#start-shape", {
  duration: 1.2,
  morphSVG: "#end-shape",
  ease: "power2.inOut",
});

// 如果 morph 出现“交叉”或“翻转”，用 shapeIndex 修正
// 先设 shapeIndex: "log"，在控制台看推荐值，再写死
tl.to("#start-shape", {
  duration: 1.2,
  morphSVG: {
    shape: "#end-shape",
    type: "rotational", // 对容易扭的形状优先试 rotational
    shapeIndex: 3,
  },
  ease: "power2.inOut",
});
```

| 配置 | 作用 |
|------|------|
| `shape` | 目标：选择器 / 元素 / raw path string |
| `type` | `"linear"`（默认）或 `"rotational"`，后者能减少扭结 |
| `shapeIndex` | 起点映射偏移，用 `"log"` 查看自动值 |
| `map` | `"size"` / `"position"` / `"complexity"`，调整 segment 匹配方式 |
| `smooth` | v3.14+，增加平滑点，解决锯齿感 |
| `curveMode` | v3.14+，插值控制柄角度，减少曲线扭结 |

---

## HyperFrames 里的注意事项

1. **全部动画进 GSAP timeline**：不要写 CSS `@keyframes` 或 `transition`，否则 HyperFrames 无法 seek 和 scrub。
2. **循环必须是有界**的：避免 `repeat: -1`。如需循环，用有限的 `repeat` 次数，或用 `onUpdate` 读取 `tl.time()` 做伪循环。
3. **初始状态用 `gsap.set`**：在 timeline 开始前把元素放到正确初始状态，避免第一帧闪烁。
4. **SVG 初始渲染**：如果用 `from()` / `fromTo()`，注意 `immediateRender: true` 是默认行为；多个 `from()` 同时作用于同一属性时，后面的要设 `immediateRender: false`。
5. **性能**：优先动画 transform 属性（`x`/`y`/`scale`/`rotation`），避免动画 `width`/`height`/`top`/`left`。

---

## 与 Remotion 缓动的对应

| Remotion `EasingType` | GSAP ease 字符串 |
|-----------------------|------------------|
| `linear` | `"none"` |
| `easeOut` | `"power3.out"` |
| `easeInOut` | `"power3.inOut"` |
| `backOut` | `"back.out(1.6)"` |
| `backInOut` | `"back.inOut(1.6)"` |
| `elastic` | `"elastic.out(1, 0.5)"` |
| `bounce` | `"bounce.out"` |

---

## 参考

- [官方 GSAP Skills](https://github.com/greensock/gsap-skills)
- [GSAP Plugins 文档](https://gsap.com/docs/v3/Plugins/)
- [MotionPathPlugin](https://gsap.com/docs/v3/Plugins/MotionPathPlugin/)
- [DrawSVGPlugin](https://gsap.com/docs/v3/Plugins/DrawSVGPlugin/)
- [MorphSVGPlugin](https://gsap.com/docs/v3/Plugins/MorphSVGPlugin/)
