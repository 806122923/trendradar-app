# TrendRadar — DESIGN.md

> 本文件是 AI 编码助手的设计宪法。任何生成 UI 的请求都应先读此文档。
> 灵感来自 VoltAgent/awesome-design-md 思路，并借鉴 Linear / Vercel / Raycast / Sanity 的执行手法，针对 TrendRadar 品牌定制。
> Last updated: 2026-04-17

---

## 0 · 品牌定位

**硬核、极简、带锋芒。** TrendRadar 是雷达，不是花园。界面应当像瑞士军刀，不像奶茶店菜单。

- **声调**：冷静、精确、一点点冒犯性的自信。像 Linear 的工程语感，但更锋利。
- **反模式**：不要"友好亲切"、不要"温暖治愈"、不要 emoji 堆砌、不要"AI 生成感"的紫蓝渐变。
- **中文为主**，标签/元数据/代码/数字用英文大写等宽字体 —— 像 Raycast 对待 keycap 的方式。

### 审美坐标

| 维度 | 取向 | 参照 |
|---|---|---|
| 密度 | 高密度但留白锋利 | Linear, Sanity |
| 色彩纪律 | 无彩色灰阶 + 单一强调色 | Sanity, Vercel |
| 层级手法 | 硬阴影 + 1px 边框，**不用**柔光 | 自家手法（Vercel 的反向） |
| 微交互 | 瞬切为主，缓动仅用于焦点环和数值补间 | Raycast |
| 字体感 | 几何 display + 人本 body + 机器 mono 的三重对比 | Vercel (Geist) + Raycast |

---

## 1 · 颜色 Tokens

### 1.1 基础 Token（对齐 `globals.css`）

| Token | 值 | 用途 |
|---|---|---|
| `--bg` | `#FFFFFF` | 页面底 |
| `--ink` | `#000000` | 正文 / 主要边框 / 深色区块底 |
| `--muted` | `#8A8A8A` | 次要信息、辅助元数据 |
| `--line` | `#E5E5E5` | 分隔线、静态卡片边框 |
| `--acid` | `#FF4F1A` | **唯一强调色（酸橙）** |
| `--acid-deep` | `#D93E0E` | 强调色按压/选中态 |
| `--green` | `#00C853` | 正向指标（极少，仅数据表真增长） |

### 1.2 语义分层（命名纪律，借鉴 Sanity 的 token 分层）

| 语义 | 映射 | 使用场景 |
|---|---|---|
| `surface.default` | `--bg` | 大区块底 |
| `surface.inverse` | `--ink` | 反色 hero / 终端面板 |
| `surface.sunken` | `#FAFAFA` | 代码块、引文、抽屉底 |
| `border.default` | `--line` | 静态边框 |
| `border.strong` | `--ink` | 按钮、focus、强调卡片 |
| `text.default` | `--ink` | 正文 |
| `text.muted` | `--muted` | 元数据、时间戳、标签辅助字 |
| `text.inverse` | `--bg` | 反色底上的文字 |
| `accent.default` | `--acid` | 唯一强调色 |
| `accent.pressed` | `--acid-deep` | 按压/持续高亮态 |

### 1.3 规则（红线）

- 除 `--acid` 外**不允许任何彩色**。图表、状态、警告都用黑白 + 酸橙。
- **禁止渐变**（`linear-gradient`、`radial-gradient` 一律禁用）。
- **禁止软阴影**（`box-shadow: 0 4px 20px rgba(0,0,0,.1)` 这种一律禁）。
- 允许**硬阴影**：`box-shadow: 4px 4px 0 var(--ink);`（neobrutalism 风，仅用于突出交互/互动卡）。
- **禁止彩色焦点环**。focus 用 `outline: 2px solid var(--acid); outline-offset: 2px;` —— 酸橙是全站唯一"彩"。

---

## 2 · 字体

### 2.1 字族

| 用途 | 字体 | 说明 |
|---|---|---|
| 标题 (display) | **Space Grotesk** | 600/700，几何 display，收紧字距 |
| 正文 (sans) | **Inter** | 400/500，人本 body，CJK 回落 PingFang SC / 微软雅黑 |
| 标签 & 代码 (mono) | **JetBrains Mono** | 400/500，等宽，标签全大写 |

**备选**：若不使用 Google Fonts，可用自托管 Geist (display+mono) + Inter 本地文件，审美接近不打折。

### 2.2 完整 Type Scale

| Level | Size / Line | Weight | Tracking | 字族 | 用途 |
|---|---|---|---|---|---|
| Display XL | 72 / 80 | 700 | -0.03em | display | 仅 landing hero |
| Display L | 56 / 60 | 700 | -0.025em | display | 章节 hero |
| H1 | 40 / 44 | 600 | -0.02em | display | 页面大标题 |
| H2 | 28 / 34 | 600 | -0.015em | display | 区块标题 |
| H3 | 20 / 26 | 600 | -0.01em | display | 卡片标题 |
| Body L | 18 / 28 | 400 | 0 | sans | 引言、slogan |
| Body | 15 / 24 | 400 | 0 | sans | 正文 |
| Body S | 13 / 20 | 400 | 0 | sans | 辅助说明 |
| Caption | 12 / 16 | 400 | 0 | sans | 图注、时间戳 |
| Label | 11 / 14 | 500 | **+0.14em** | mono, UPPER | `01 · QUERY` 区块编号 |
| Code | 13 / 20 | 400 | 0 | mono | 代码、API 路径、product_id |
| Metric | 32 / 36 | 600 | -0.01em | mono | 大数字 (Score 87, $29.9) |

### 2.3 中文排版（CJK 规则）

- `word-break: keep-all;` 默认开启，避免中文内词被拆。
- `text-spacing-trim: trim-start;`（现代浏览器）剪掉行首多余空白。
- **中英混排**：中英间不手动加空格，依靠 `font-feature-settings: "palt"` 类字偶简调（若字体支持）或直接让浏览器处理。
- 数字/货币/单位用 mono：`$29.9`、`+47%`、`USD/件`。
- 标点避免用全角时的美式引号；使用中文标点「」『』，英文内容内用 `"..."`。

---

## 3 · 间距 & 圆角 & 边框

### 3.1 Spacing Scale（4px 基准）

| Token | Value | 典型用途 |
|---|---|---|
| `space-1` | 4px | icon 与文字间距 |
| `space-2` | 8px | 标签组 gap、小按钮内 padding-y |
| `space-3` | 12px | 卡片内元素间距 |
| `space-4` | 16px | 卡片 padding 最小值 |
| `space-5` | 24px | 标准卡片 padding、区块内 gap |
| `space-6` | 32px | 区块间小距 |
| `space-7` | 48px | 区块间中距 |
| `space-8` | 64px | 区块间大距 |
| `space-9` | 96px | 页面级 section gap |
| `space-10` | 128px | landing 巨型留白 |

### 3.2 圆角

- **全站固定 `border-radius: 2px`**。**不允许 8px+ 的圆角**。头像圆形除外。

### 3.3 边框

- 静态：`1px solid var(--line)`
- 交互/强调：`1.5px solid var(--ink)`（按钮实际值）
- 反色底部：`1px solid rgba(255,255,255,0.16)`

---

## 4 · 区块编号（页面锚点）

聊天页 / 主要内容页用等宽字体编号，Raycast 式正字距放大 + Sanity 式两级标题：

```
00 · OVERVIEW
01 · QUERY
02 · ONE-LINER
03 · SCORE DISTRIBUTION
04 · PICKS
```

- 编号 + `·` 分隔符 + 全大写英文标签。
- 字号 11px，颜色 `--ink`（非 `--muted`，保证锋芒）。
- `letter-spacing: 0.14em`，字重 500。
- 区块编号上方可跟 1px `--line` 分隔线，下方 `space-4` 间距再接内容。

---

## 5 · 组件模式

### 5.1 Button 全状态表

所有按钮：`border-radius: 2px`，`transition-property: background, color, border-color`，`transition-duration: 0ms`（硬切，仅 focus ring 有过渡）。

| 变体 | static | hover | focus | pressed | disabled |
|---|---|---|---|---|---|
| `.btn-tr` (black) | bg `--ink`, fg `--bg`, border `--ink` | bg `--acid`, fg `--ink`, border `--acid` | 同 static + outline 2px `--acid` offset 2 | bg `--acid-deep`, fg `--ink` | opacity 0.3, cursor not-allowed |
| `.btn-tr-acid` (primary) | bg `--acid`, fg `--ink`, border `--acid` | bg `--ink`, fg `--bg`, border `--ink` | 同 static + outline 2px `--ink` offset 2 | bg `--acid-deep` | opacity 0.4 |
| `.btn-tr-ghost` (outline) | bg transparent, fg `--ink`, border `--ink` | bg `--ink`, fg `--bg` | 同 static + outline 2px `--acid` offset 2 | bg `--acid-deep`, fg `--ink`, border `--acid-deep` | opacity 0.3 |
| `.tr-chip` (chip) | bg `--bg`, border `--line` | border `--ink` | 同 static + outline 2px `--acid` offset 2 | bg `--ink`, fg `--bg` | opacity 0.4 |

**Loading 态**：文案换成 mono caps（`LOADING…`），可追加闪烁 caret `▋` 每 600ms 瞬切透明度（非淡入淡出）。

### 5.2 Card

```css
.tr-card {
  background: var(--bg);
  border: 1px solid var(--line);
  border-radius: 2px;
  padding: 24px;
}
/* 交互式卡片在 hover 上抬为硬阴影 */
.tr-card--interactive:hover {
  border-color: var(--ink);
  box-shadow: 4px 4px 0 var(--ink);
  transform: translate(-1px, -1px); /* 硬切，无过渡 */
}
```

Vercel 式"shadow-as-border" 在 TrendRadar 里反转：**不是柔和阴影分层**，而是**硬阴影 + 位移 1px 产生"贴标签"感**。

### 5.3 Input / Textarea

- 底色 `--bg`，边框 1px `--line`。
- Placeholder：`TYPE HERE.`（不是"请输入..."）。色 `--muted`。
- Focus：border `--ink`，加外 outline 2px `--acid` offset 2。
- 带 mono caret `▋` 在 hero 输入框（致敬 Raycast 命令行感）。

### 5.4 Chart

- **仅用内联 SVG**，禁止在 React 端引入 Chart.js / D3 / Recharts。
- 线条 2px，填充仅 `--ink` 和 `--acid`。
- 网格线 1px `--line`，坐标轴标签 mono 11px `--muted`。
- Rank-1 用 `--acid` 填充，其余用 `--ink`，从不混用两种以上色。
- 图表标题与轴标题全大写 mono（`SCORE / 100`）。

### 5.5 Table

- `border-collapse: collapse`，全表 1px `--line` 横向分隔，**无竖向分隔**。
- 表头 mono 11px UPPER，字色 `--ink`，下方 1.5px `--ink` 粗线。
- 行高 44px，hover 行 bg `#FAFAFA`（非浮空阴影）。
- 数字列右对齐 mono，文字列左对齐 sans。

### 5.6 Badge / Tag

- 1px `--line` 边框，padding `2px 6px`，11px mono UPPER，radius 2px。
- 正向数据用 `--green` 文字但**无填充**；负向用 `--acid` 文字。
- 普通标签全黑白。

---

## 6 · 层级系统（Depth）

借鉴 Vercel 的层级思路，但 TrendRadar 用**边框变化 + 硬阴影**代替柔和模糊。

| Level | 处理 | 用途 |
|---|---|---|
| L0 | 无边框 | 页面背景 |
| L1 | 1px `--line` | 静态卡片、表单容器 |
| L2 | 1px `--ink` | 活跃卡片、当前选中项 |
| L3 | 1px `--ink` + `box-shadow: 4px 4px 0 var(--ink)` | Hover 交互卡、弹窗/抽屉 |
| L4 | 反色：bg `--ink` / fg `--bg`，无边框 | Hero 终端、最上层提示 |

---

## 7 · Motion（动效规范）

克制是纪律。**TrendRadar 默认 0ms 硬切**，仅以下场景允许缓动：

| 场景 | Duration | Easing | 说明 |
|---|---|---|---|
| Focus ring 出现 | 120ms | `cubic-bezier(0.22, 1, 0.36, 1)` | 引用 landing.html 统一曲线 |
| 数值补间 (Score 0→87) | 600ms | `cubic-bezier(0.22, 1, 0.36, 1)` | 仅数字计数，不改变布局 |
| 骨架屏呼吸 | 1200ms infinite | linear | 1%→6%→1% 透明度，非 shimmer 渐变 |
| 折叠/展开 (DEBUG 面板) | 160ms | ease-out | 只改 max-height，不改 opacity |
| Hover 变色 | **0ms** | — | 硬切 |
| 页面切换 | **0ms** | — | 不做路由过渡 |

### 减动偏好

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0ms !important;
    transition-duration: 0ms !important;
  }
}
```

---

## 8 · 响应式

### 8.1 断点

| 名称 | 宽度 | 布局 |
|---|---|---|
| `sm` | ≥640px | 单列保持，chip 行改多行 wrap |
| `md` | ≥768px | 2 列卡片组 |
| `lg` | ≥1024px | 3 列 Picks、侧栏显影 |
| `xl` | ≥1280px | 内容区 960px 居中，两侧留白 |

### 8.2 折叠规则

- 移动端：导航折叠为抽屉；`01 · QUERY` 横向 chip 变竖向堆叠；表格变卡片列表。
- 桌面：最大宽度 1280px，内容区 960px 居中，hero 可突破到 1120px。
- **任何断点都不改变色彩系统**，不牺牲边框锋利度。

---

## 9 · 禁止清单（AI 写码红线）

### 9.1 色彩

- ❌ Tailwind 默认的 `text-blue-500`、`bg-indigo-600`、`from-purple-500 to-pink-500` 等彩色
- ❌ 所有渐变 utility：`bg-gradient-to-r`、`bg-gradient-to-br`、`text-transparent bg-clip-text`
- ❌ 任何紫/蓝双色渐变 —— 这是"AI 生成感"的典型标志

### 9.2 圆角/阴影

- ❌ `rounded-lg`、`rounded-xl`、`rounded-2xl`、`rounded-3xl`、`rounded-full`（头像除外）
- ❌ `shadow-sm` / `shadow` / `shadow-lg` / `shadow-xl` / `shadow-2xl` 等**软阴影**
- ❌ `backdrop-blur-*`、`bg-white/50` 玻璃拟态

### 9.3 动效

- ❌ `hover:scale-105`、`hover:scale-110` 等缩放动画
- ❌ `animate-pulse` 柔化骨架（改用我们的 1% opacity 呼吸）
- ❌ 页面级 fade/slide 过渡

### 9.4 装饰

- ❌ emoji 作为功能图标（装饰例外）
- ❌ 图标左侧"border-left 彩条"的卡片装饰（AI 常见病）
- ❌ 占位图用 `bg-gray-200 animate-pulse` 的柔化块

### 9.5 文案

- ❌ Placeholder 文字使用「请输入...」→ 改为 `TYPE HERE.`
- ❌ "欢迎使用"「您好，有什么可以帮助您的吗？」这类亲切语
- ✅ 用精确名词动词："输入你想要的类目、价格带与地区。"

---

## 10 · 写给 AI 的使用指南（Agent Prompt Guide）

### 10.1 口令（每次生成 UI 前默读）

> **黑白 + 酸橙，2px 圆角，硬阴影，无渐变，无软阴影，中文为主英文 mono。**
> 如果你正要写 `rounded-lg` 或 `bg-gradient-to-r`，停下来。

### 10.2 快速色彩卡（复制粘贴到 prompt）

```
Colors allowed in this project:
  Black      #000000  var(--ink)
  White      #FFFFFF  var(--bg)
  Gray Text  #8A8A8A  var(--muted)
  Gray Line  #E5E5E5  var(--line)
  Acid       #FF4F1A  var(--acid)       ← ONLY accent
  Acid Deep  #D93E0E  var(--acid-deep)
  Green      #00C853  var(--green)      ← positive metrics ONLY
NO other colors. NO gradients. NO soft shadows.
```

### 10.3 组件复用优先级

1. 优先复用 `.btn-tr` / `.btn-tr-acid` / `.btn-tr-ghost` / `.tr-chip` / `.tr-card` / `.tr-label`（见 `globals.css`）
2. 其次使用本文件 §5 的全状态表 + token 手写
3. 最后才考虑新建 —— 新建必须先在本文件登记

### 10.4 生成示例 Prompt

**示例 A — 卡片**
> 生成一个展示 Top 1 产品的卡片。标题 H3 Space Grotesk 600，分数 32px mono 600 靠右，来源与时间 11px mono UPPER `--muted`。卡片 1px `--line` 边框，2px radius，padding 24。hover 时边框切 `--ink`，加硬阴影 `4px 4px 0 var(--ink)`，位移 `-1px,-1px`，**无过渡**。

**示例 B — 区块标题**
> 在区块顶部加 `01 · QUERY` 样式的标签：11px JetBrains Mono, 500, letter-spacing 0.14em, uppercase, 颜色 `--ink`。标签上方 1px `--line` 分隔线，下方 16px 间距。

**示例 C — 图表**
> 用内联 SVG 画水平条形图。每行高度 32px，条形 2px 描边 + 填充：rank-1 用 `--acid`，其余 `--ink`。网格线 25/50/75/100 四条，1px `--line`。轴标签 11px mono `--muted`。**不得引入 Chart.js / Recharts**。

### 10.5 迭代指令（你可以这么跟我说）

| 你要的效果 | 跟我说 |
|---|---|
| 更安静 | "按 §7 Motion 表，把所有过渡砍到 0ms，只留 focus 和数值补间" |
| 更锋利 | "把 hover 态全换成 L3：1px `--ink` + 硬阴影 + `-1px,-1px` 位移" |
| 更工程味 | "把所有次要元数据改成 mono UPPER，加 `01 · LABEL` 区块编号" |
| 更暗黑 | "反色区块用 L4：bg `--ink`，正文 `--bg`，边框 `rgba(255,255,255,0.16)`" |

### 10.6 自检清单（提交前）

- [ ] 全文件 grep 确认：无 `rounded-lg/xl/2xl/3xl`、无 `shadow-[sm|lg|xl|2xl]`、无 `gradient-`、无 `scale-`
- [ ] 焦点环是 `--acid` outline 而非任何彩色
- [ ] 所有数字/代码/标签是 mono
- [ ] 区块有 `NN · LABEL` 编号
- [ ] 禁止清单 §9 一条未犯

---

## 附录 A — 与现有代码的映射

| 本文件引用 | 真实位置 |
|---|---|
| `.btn-tr` / `.btn-tr-acid` / `.btn-tr-ghost` | `apps/web/src/app/globals.css` §components |
| `.tr-label` / `.tr-display` / `.tr-card` / `.tr-chip` / `.tr-acid-u` | 同上 |
| Tailwind token `acid` / `ink` / `paper` / `line` / `muted` / `pos` | `apps/web/tailwind.config.ts` |
| Landing hero / 区块结构参照 | `apps/web/public/landing.html` |
| Chat 区块编号 00→04 实例 | `apps/web/src/app/chat/page.tsx` |

## 附录 B — 参考范本（长期学习）

本项目 `.claude/references/awesome-design-md-cn/` 收录了以下品牌的 DESIGN.md（结构参照，**审美非直接复制**）：

- **Linear** — 工程语感、状态机式精确度
- **Vercel** — Geist 字体感、层级手法
- **Raycast** — 正字距、focus ring、micro-motion
- **Sanity** — 无彩色灰阶 + 单一强调色的执行纪律

读它们是为了对比、偷手法；但 TrendRadar 的**锋芒属于自己**。
