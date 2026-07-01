<!-- pixel-art title: video-replica-studio -->
```
╔═════════════════════════════════════════════════════════════════╗
║                                                                 ║
║ █  █ ████ ███  ████  ██       ███  ████ ███  █    ████  ███  ██ ║
║ █  █  ██  █  █ █    █  █      █  █ █    █  █ █     ██  █    █  █ ║
║ █  █  ██  █  █ ███  █  █      ███  ███  ███  █     ██  █    ████ ║
║  █ █  ██  █  █ █    █  █      █ █  █    █    █     ██  █    █  █ ║
║   █  ████ ███  ████  ██       █  █ ████ █    ████ ████  ███ █  █ ║
║                                                                 ║
║                    ███ ████ █  █ ███  ████  ██                  ║
║                  █     ██  █  █ █  █  ██  █  █                  ║
║                   ██   ██  █  █ █  █  ██  █  █                  ║
║                     █  ██  █  █ █  █  ██  █  █                  ║
║                   ███   ██  ████ ███  ████  ██                  ║
║                                                                 ║
║                         视频复刻工作室                                 ║
║                                                                 ║
╚═════════════════════════════════════════════════════════════════╝
```

# Video Replica Studio / 视频复刻工作室

参考视频复刻、拆解、对齐质检和动效组件沉淀。不是“凭感觉复刻”，而是先抽帧、写时间线，再用候选视频做对照验证；如果目标是 HyperFrames / Remotion 重制，会通过多轮对比和返修改代码，把参考视频里的动效拆成可复用组件。

## 示例成片：Presenton 复刻 Bitexact 成片

[▶ Watch Presenton Replica Bitexact Showcase](https://github.com/user-attachments/assets/f792bd12-d8b3-43b7-b751-98aeb033713b)

- 类型：参考视频复刻结果
- 级别：bit-exact / pixel-aligned 交付成片
- 时长：35.136 秒
- 规格：1920x1080，30fps，H.264 + AAC
- 文件：`assets/showcases/presenton-replica-pixel-aligned-bitexact.mp4`

0.5 秒对照抽帧：

![0.5 秒对照图](assets/images/video-replica-studio-compare.jpg)

> 将实际 0.5 秒对照 contact sheet 存为 `assets/images/video-replica-studio-compare.jpg` 后，上面的占位图会生效。

## 这个 Skill 能做什么

- 参考视频复刻
- HyperFrames / Remotion 动效重制
- 可复用视频动效组件沉淀
- 像素级 / 视觉级 / 风格级对齐判断
- HyperFrames / Remotion 重制视频的质检
- “当前仍然没有对齐”这类返修定位
- 自动生成抽帧、时间线、运动剖面、diff 报告和组件脚手架

## 核心方法

这是一个质检和拆解 skill，本身不固定某种视觉风格。它关注证据：

- 每 `0.5s` 抽帧，失败窗口用 `0.1s` 或指定时间点密采样
- 秒级行为时间线与运动剖面（activity / static segment / hard cut / mutation）
- side-by-side contact sheet 与 render diff 热图
- 局部 crop / overlay / 组件级对齐证据
- 自动差异分类：`hard_cut`、`static_segment`、`scene_boundary_mismatch`、`timing_offset`、`missing_secondary_motion`
- 返修日志和相邻时间点回测
- PSNR / SSIM / SHA-256 等硬指标
- 第一个失败时间点和修复清单

每个可复用组件都应该记录：

- 组件描述和适用场景
- 输入参数和内容槽位
- 时间线、缓动、状态变化
- 技术栈：HyperFrames / Remotion / React / CSS / SVG / GSAP
- 对齐证据和已知限制

## 快速开始

```bash
# 1. 分析参考视频：抽帧 + 场景检测 + 运动剖面
python3 cli/replica.py analyze reference.mp4 --out analysis/reference

# 2. 粗略对比候选视频
python3 cli/replica.py quick reference.mp4 candidate.mp4 --out analysis/quick

# 3. 完整对比：哈希、PSNR/SSIM、render diff、差异分类、报告
python3 cli/replica.py diff reference.mp4 candidate.mp4 --out analysis/diff --report

# 4. 生成可运行的反 PPT 项目脚手架
python3 cli/replica.py scaffold remotion --out my-replica/
python3 cli/replica.py scaffold hyperframes --out my-hyperframes/
```

依赖：`Python 3.11+`、`Pillow`、`ffmpeg/ffprobe`（优先自动发现 `static_ffmpeg` / `imageio-ffmpeg` 或系统 PATH）。
Remotion 脚手架需要 `Node.js 18+`。

## fidelity 级别

| 级别 | 适用场景 | 验收证据 |
| --- | --- | --- |
| Pixel-level | 用户明确要求 pixel-perfect / bit-exact | 文件 SHA-256 一致、PSNR `average:inf`、SSIM `All:1.000000` |
| Visual-level | 常说的“复刻”“做一个一样的”“对齐这个视频” | 0.5s 抽帧 side-by-side、时间线报告、差异清单、分类报告 |
| Style-level | “这种风格”“参考这个感觉” | 提取配色、字体行为、运动语法、节奏、转场词汇 |

手写 HyperFrames / Remotion 通常只能达到 Visual-level，Pixel-level 需要源流复用或完全一致的视频流。

## 反 PPT 检查清单

参考视频真正“有视频感”的共性。把这些当作设计要求，而不是可选润色：

1. **连续镜头 / 转场** —— 整段画面不要静止，用 push、morph、camera rig 替代硬切。
2. **二级动效** —— 每个主体入场都伴随 glow、sheen、颗粒、光标或环境层。
3. **纹理层** —— film grain、vignette、ambient glow 以低透明度覆盖在最上层。
4. **丰富缓动** —— 避免线性淡入淡出和默认 ease-in-out，使用 `power3.inOut`、`back.out`、`elastic.out` 或自定义 spring。
5. **场景重叠生命周期** —— 下一场景应在前一场景结束前开始进入，不要先黑屏再切换。

## CLI 速查

| 子命令 | 作用 | 关键输出 |
| --- | --- | --- |
| `analyze` | 抽帧、场景检测、运动剖面 | `frames/`、`contact/`、`frames-manifest.json`、`motion-profile.json`、`scene-transitions.json` |
| `quick` | 预览帧 + 1.0s 粗粒度 render diff | `ref/`、`cand/`、`diff/` |
| `diff` | 完整对比：哈希、指标、分类、render diff、组件 crop | `comparison.json`、`comparison-report.md`、`render-diff/`、`component-crop/` |
| `scaffold remotion` | 自包含可运行的 Remotion 反 PPT 项目 | `package.json`、`tsconfig.json`、`src/`、`components/`、`shared/` |
| `scaffold hyperframes` | 可运行的 HyperFrames host composition | `index.html` |

详见 `scripts/README-scripts.md` 与 `SKILL.md`。

## 目录结构

```
.
├── README.md
├── SKILL.md
├── agents/
│   └── openai.yaml
├── assets/
│   ├── images/video-replica-studio-compare.jpg
│   └── showcases/presenton-replica-pixel-aligned-bitexact.mp4
├── cli/
│   └── replica.py
├── references/
│   ├── alignment-workflow.md
│   ├── presenton-lessons.md
│   └── replica-levels.md
├── scripts/
│   ├── extract_frames.py
│   ├── compare_videos.py
│   ├── motion_profile.py
│   ├── render_diff.py
│   ├── component_crop.py
│   ├── _utils.py
│   └── README-scripts.md
└── templates/
    ├── remotion/
    │   ├── components/
    │   ├── shared/
    │   └── example/
    └── hyperframes/
        ├── components/
        ├── blocks/
        ├── motion-grammar.md
        └── example/
```

## 安装

```bash
npx skills add https://github.com/<your-username>/video-replica-studio
```

## 设计边界

- 不凭感觉宣称像素级对齐；像素级需要一致哈希、PSNR infinity 或 SSIM 1.0 等硬证据。
- 手写 HyperFrames / Remotion 复刻通常目标是视觉级对齐和组件沉淀。
- 不是风格化原创 skill，也不是片头生成 skill；它专注于参考视频的拆解、复刻和质检。
