# 视频复刻工作室 / Video Replica Studio

参考视频动效复刻、拆解、对齐质检与组件沉淀，支持多模态视觉理解驱动创作。

不是“凭感觉复刻”，而是先抽帧、用多模态能力**看懂**参考视频的视觉意图，再写时间线、用候选视频做对照验证；如果目标是 HyperFrames / Remotion 重制，会通过多轮对比和返修改代码，把参考视频里的动效拆成可复用组件。对于风格级任务，会提取 Style DNA 并在新内容上重新表达。

---

## Quick Start / 快速开始

```bash
# 1. 分析参考视频：抽帧 + 场景检测 + 运动剖面
python3 cli/replica.py analyze reference.mp4 --out analysis/reference

# 2. 粗略对比候选视频（预览帧 + 1.0s 粗粒度 render diff）
python3 cli/replica.py quick reference.mp4 candidate.mp4 --out analysis/quick

# 3. 完整对比：哈希、PSNR/SSIM、render diff、差异分类、报告模板
python3 cli/replica.py diff reference.mp4 candidate.mp4 --out analysis/diff --report

# 4. 生成可运行的反 PPT 项目脚手架
python3 cli/replica.py scaffold remotion --out my-replica/
python3 cli/replica.py scaffold hyperframes --out my-hyperframes/
```

> **注意**：CLI 目前只接受本地视频路径。如果是 URL，请先下载到本地再执行以上命令。

---

## 能做什么

- 参考视频复刻（像素级 / 视觉级 / 风格级）
- **多模态视觉意图提取** —— 用多模态能力看懂参考帧的视觉叙事、动效意图和情绪
- HyperFrames / Remotion 动效重制
- **早期组件识别** —— 在动手前将参考动效映射到已有组件库
- **Style DNA 提取与重表达** —— 提取风格基因并在新内容上变体应用
- 可复用视频动效组件沉淀
- **运动词汇卡片组** —— 每种动效模式的使用场景、组合配方和决策树
- HyperFrames / Remotion 重制视频的质检
- “当前仍然没有对齐”这类返修定位

---

## 核心工作流

1. **确定输入**：参考视频、候选视频（如有）、目标保真度、渲染栈、输出目录。
2. **分析参考视频**：抽帧、生成 contact sheet、检测场景切换、输出运动剖面。
3. **提取视觉意图**：阅读 contact sheet，描述每段画面的 what / why / mood。
4. **早期组件识别**：将视觉意图与运动词汇卡片组匹配，输出 `component-mapping.json`。
5. **对比候选视频**：生成 side-by-side、render-diff 热图、差异分类报告。
6. **小步修复并重跑**：一次只改一个可见问题，改完立即重跑 `replica diff`。
7. **沉淀可复用组件**：把验证过的动效写入组件库，附带证据、限制和组合配方。

---

## 保真度级别

| 级别 | 适用场景 | 验收证据 |
| --- | --- | --- |
| **像素级** | 用户明确要求 pixel-perfect / bit-exact | SHA-256 一致、PSNR `average:inf`、SSIM `All:1.000000` |
| **视觉级** | “复刻”“做一个一样的”“对齐这个视频” | 0.5s 抽帧 side-by-side、时间线报告、差异清单、分类报告 |
| **风格级** | “这种风格”“参考这个感觉” | Style DNA：配色比例、字体性格、运动节奏、缓动偏好、转场词汇、空间密度，编码为可参数化 token |

手写 HyperFrames / Remotion 通常只能达到视觉级；像素级需要源流复用或完全一致的视频流。

---

## 反 PPT 检查清单

参考视频真正“有视频感”的共性，把这些当作设计要求：

1. **连续镜头 / 转场** —— 整段画面不要静止，用 push、morph、camera rig 替代硬切。
2. **二级动效** —— 每个主体入场都伴随 glow、sheen、颗粒、光标或环境层。
3. **纹理层** —— film grain、vignette、ambient glow 以低透明度覆盖在最上层。
4. **丰富缓动** —— 避免线性淡入淡出和默认 ease-in-out，使用 `power3.inOut`、`back.out`、`elastic.out` 或自定义 spring。
5. **场景重叠生命周期** —— 下一场景应在前一场景结束前开始进入，不要先黑屏再切换。

每种动效模式的详细决策树、组合配方和组件映射见 [`references/motion-vocabulary.md`](references/motion-vocabulary.md)。

---

## CLI 速查

| 子命令 | 作用 | 关键输出 |
| --- | --- | --- |
| `analyze` | 抽帧、场景检测、运动剖面 | `frames/`、`contact/`、`frames-manifest.json`、`motion-profile.json`、`scene-transitions.json` |
| `quick` | 预览帧 + 1.0s 粗粒度 render diff | `ref/`、`cand/`、`diff/` |
| `diff` | 完整对比：哈希、指标、分类、render diff、组件 crop | `comparison.json`、`comparison-report.md`、`render-diff/`、`component-crop/` |
| `scaffold remotion` | 自包含可运行的 Remotion 反 PPT 项目 | `package.json`、`tsconfig.json`、`src/`、`components/`、`shared/` |
| `scaffold hyperframes` | 可运行的 HyperFrames host composition | `index.html` |

详见 [`scripts/README-scripts.md`](scripts/README-scripts.md) 与 [`SKILL.md`](SKILL.md)。

---

## 目录结构

```
.
├── README.md
├── SKILL.md
├── LICENSE
├── agents/openai.yaml          # Agent 配置文件
├── cli/replica.py              # 统一命令行入口
├── scripts/                    # 底层分析脚本
│   ├── extract_frames.py
│   ├── compare_videos.py
│   ├── motion_profile.py
│   ├── render_diff.py
│   ├── component_crop.py
│   ├── _utils.py
│   └── README-scripts.md
├── references/                 # 方法论与参考文档
│   ├── alignment-workflow.md
│   ├── motion-vocabulary.md
│   ├── presenton-lessons.md
│   ├── replica-levels.md
│   ├── style-dna.md
│   └── visual-intent-guide.md
├── templates/                  # 可复用组件与脚手架模板
│   ├── remotion/
│   │   ├── components/
│   │   ├── shared/
│   │   └── example/
│   └── hyperframes/
│       ├── components/
│       ├── blocks/
│       ├── motion-grammar.md
│       └── example/
└── assets/
    └── showcases/              # 复刻案例展示
```

---

## 依赖

- Python 3.11+
- Pillow
- ffmpeg / ffprobe（优先自动发现 `static_ffmpeg` / `imageio-ffmpeg` 或系统 PATH）
- Remotion 脚手架需要 Node.js 18+

---

## 设计边界

- 不凭感觉宣称像素级对齐；像素级需要一致哈希、PSNR infinity 或 SSIM 1.0 等硬证据。
- 手写 HyperFrames / Remotion 复刻通常目标是视觉级对齐和组件沉淀。
- 风格级任务通过 Style DNA 提取与重表达实现变体创作，不是凭感觉模仿。
- 不是片头生成 skill；它专注于参考视频的拆解、复刻、风格提取和质检。
