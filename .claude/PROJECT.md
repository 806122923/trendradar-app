# TrendRadar · 项目全景文档

> **用途**：这是 AI 编码助手 + 团队成员的**单一信息源**。读完这份文档，你应该能独立理解：项目在做什么、现在进行到哪一步、下一步该做什么、为什么这么做。
> **最后更新**：2026-04-23
> **当前阶段**：P1 完成 · P2 阻塞中（等待域名 + Railway 部署）
> **代码库**：`C:\Users\Mqx95\Documents\Claude\Projects\trendradar-app`（Windows 本地） · 沙盒挂载在 `/sessions/*/mnt/trendradar-app`
> **Owner**：Hemu（GitHub: 806122923 / Mqx95）· git author `Hemu <806122923@qq.com>`

---

## 目录

1. [30 秒版](#30-秒版)
2. [产品定位 · Why](#产品定位--why)
3. [技术架构 · How](#技术架构--how)
4. [设计系统](#设计系统)
5. [目录结构（真实代码）](#目录结构真实代码)
6. [关键文件与职责](#关键文件与职责)
7. [数据库 Schema](#数据库-schema)
8. [定价策略](#定价策略)
9. [Waitlist 链路](#waitlist-链路)
10. [邮件序列](#邮件序列)
11. [分析 · Plausible](#分析--plausible)
12. [截至今天做了什么 · 时间线](#截至今天做了什么--时间线)
13. [接下来要做什么 · 路线图](#接下来要做什么--路线图)
14. [域名决策](#域名决策)
15. [环境变量清单](#环境变量清单)
16. [Gotchas · 踩过的坑](#gotchas--踩过的坑)
17. [开发 · 部署 workflow](#开发--部署-workflow)
18. [与 AI Agent 协作规则](#与-ai-agent-协作规则)

---

## 30 秒版

**TrendRadar** 是一个**面向中国卖家、服务 TikTok Shop 美区**的 AI 选品 Agent。

- **它不是数据面板**（Kalodata / FastMoss 那种给你图表让你自己判断的工具）
- **它是会推理的 Agent**——你问"给我 3 个美区 30 美金以内、宠物类、增速最快的品"，它给你 Top 3 推荐 + 评分 + 推理链 + 风险点 + 下一步动作
- **核心差异**：中文原生 · 便宜 1/7（¥99/月 vs Kalodata $99/月）· Agent 而非面板
- **技术栈**：Next.js 14（前端） + FastAPI（后端） + Neon Postgres（DB） + DeepSeek（LLM）· 前端部署 Vercel · 后端规划部署 Railway
- **当前状态**：landing 页上线、/chat demo 可用、waitlist 链路跑通、Plausible 已接入；**后端 Railway 部署 + 域名 + Email 2-5 自动化**尚未启动

---

## 产品定位 · Why

### 一句话

> **用 AI Agent 帮 TikTok Shop 美区新手卖家选品——不是给你一堆报表，是直接替你拍板。**

### 目标用户

**单一画像**：**TikTok Shop 美区新手卖家**
- 零收入 或 月 GMV < 3k 美金的**尝试型卖家**
- 个体 / 夫妻店 / 2-3 人微团队
- **决策链 = 使用链 = 付费链 = 同一个人**（没有 B2B 多方决策）
- 身处中国境内，但业务在海外（他们日常已经在用梯子做 TikTok Shop）

### 用户语言（VOC，来自 6 个独立来源的调研）

**Push（逼他们离开旧方式）**：
- "还没出第一单就先交 700 多块工具费"
- "踩了 2 万块坑才第一次没亏钱"
- "清单 9.9 → 进阶 399 → VIP 2999，推的全是红海"
- "英文 dashboard 点半天找不到那一栏"
- "每天两三个小时翻数据还是判断不出来"

**Pull（期待我们给的）**：
- "能不能有一个中文版的 Kalodata，直接告诉我做什么品"
- "ChatGPT 能不能接 TikTok 数据，我就问它该选啥"
- "真希望有个懂 TikTok Shop 的 AI 顾问"

### Jobs To Be Done

1. **判断一个品值不值得做**（不是只给数据，而是给结论 + 推理）
2. **找货源**（图搜 1688 同款直接拿报价，算毛利）
3. **拆解竞品痛点**（评论差评归纳 → 反向改款建议）

### 真实使用场景

- "给我 3 个美区 30 美金以内、宠物类、增速最快的品"
- "粘贴竞品链接 → AI 归纳 48 条电池续航差吐槽 → 建议改款点"
- "输入成本 → 输出 $24.99 定价 + 58% 毛利 + 1.72 盈亏 ROAS"
- "新手上路：美区家居 30 天起盘模板"

### 竞品 & 差异化

| 竞品 | 定位 | 月费 | 威胁级别 | 我们的差异 |
|---|---|---|---|---|
| **EchoTik** | 中文 + 全链路数据 + AI 工具 | 免费+付费 | 🔴 高 | 我们只做选品不做全链路，更垂直 |
| **Kalodata** | 英文数据面板 | $99+ | 🟡 中 | 中文 · 便宜 1/7 · Agent 而非面板 |
| **FastMoss** | 百万 SKU + 达人/广告数据 | $99+ | 🟡 中 | 同上 |
| **嘀嗒狗** | 永久免费 | 免费 | 🟠 高 | 免费只给数据，我们给结论 |
| **蝉妈妈 / 抖查查** | 国内抖音 | — | 🟢 低 | 他们不覆盖 TikTok Shop 海外 |
| **付费社群 / 跟单老师** | 非工具替代 | ¥99-2999 | 🟡 中 | 透明推理链 vs 割韭菜黑盒 |

**Anti-persona（不是我们的用户）**：
- 月 GMV 10万+ 的成熟品牌方（该用 Kalodata/FastMoss）
- 非中国市场卖家（我们专攻中文）
- 只想要数据不要判断的资深用户（我们是 Agent 不是数据面板）
- 独立站 / 纯 Amazon 卖家（首发只做 TikTok Shop US）

---

## 技术架构 · How

### 架构图

```
用户浏览器（中国大陆，已挂梯子做 TikTok Shop）
     ↓ HTTPS
┌─────────────────────────────────────────┐
│  Vercel · Next.js 14 前端                │
│  （香港/东京 PoP 对国内访问较快）           │
│  ├─ /  · 静态 landing.html（设计师级）     │
│  ├─ /alternatives/*  · 4 个 SEO 对比页     │
│  ├─ /chat            · React demo 页      │
│  └─ /api/tally/*     · Tally 同源代理 rewrite │
└─────────────────────────────────────────┘
         ↓ fetch
┌─────────────────────────────────────────┐
│  Railway · FastAPI 后端（Python 3.12）   │
│  （待部署 · 已有 Dockerfile + 代码骨架）     │
│  ├─ /api/v1/health                        │
│  ├─ /api/v1/chat/query  · SSE 流式选品     │
│  └─ /api/v1/waitlist/*  · 3 个端点         │
└─────────────────────────────────────────┘
    ↓                     ↓
┌──────────────┐   ┌──────────────────┐
│ Neon Postgres│   │ DeepSeek API     │
│（Serverless  │   │（OpenAI 兼容，    │
│  US-East-2） │   │  国内直连 OK）     │
└──────────────┘   └──────────────────┘

旁路服务：
- Tally.so              收集 waitlist 邮箱（表单托管）
- Resend                发送邮件（Email 1-5 + 上线邀请）
- Plausible Analytics   隐私优先的访问分析（已接入，等域名）
- Cloudflare R2         图片 / 档案 PDF（P3 启用）
- Apify Actors          TikTok Shop + 1688 数据抓取（P3 启用）
```

### 云端栈总览

| Layer | Service | URL / 位置 | 状态 |
|---|---|---|---|
| 前端 | **Vercel** | `trendradar-app-sigma.vercel.app` | ✅ 上线 |
| 后端 | **Railway** | 待生成 `*.up.railway.app` | ⏸ 待部署（P2） |
| 数据库 | **Neon Postgres** | US-East-2 (Ohio) | ⏸ 待创建 |
| LLM | **DeepSeek** | `platform.deepseek.com` | ✅ 开发用 key 已获取 |
| Email | **Resend** | `resend.com` | ⏸ 待绑定域名 |
| 表单 | **Tally.so** | 表单 ID `pbPg1Z`（已上线） | ✅ 运行中 |
| 分析 | **Plausible** | 自建 or Plausible Cloud | ⏸ 待用户注册账号 |
| 域名 | Cloudflare Registrar（首选） | 待购买 | ⏸ 付款卡住 |
| CI/CD | Vercel 自动（git push main） | — | ✅ |

### 为什么这么选

- **Next.js 14 App Router** + **静态 HTML 混用**：landing 是 1932 行手写静态页（设计师品），App Router 只服务 /chat 这种 React 页。用 `next.config.mjs` 的 `beforeFiles` rewrite 让 `/` 走 landing.html。
- **FastAPI + asyncpg**：Python 生态下 async 最成熟的选择；SSE 流式原生支持；Pydantic 模型 + 类型检查。
- **Neon**：真正 serverless Postgres，scale-to-zero，免费层 3GB 够 beta 阶段。
- **DeepSeek**：国内直连、OpenAI 兼容 SDK、中文推理效果好、成本约 $0.14/1M tokens（Claude Sonnet 的 1/40）。
- **Vercel + Railway 组合**：前端静态 + 后端容器分开，各自最擅长的事；前端免费额度大，后端按用量计费便宜。

---

## 设计系统

见 `DESIGN.md`（389 行完整宪法）。核心原则：

### 审美坐标

**硬核、极简、带锋芒。TrendRadar 是雷达，不是花园。**

- 声调：冷静、精确、一点点冒犯性的自信（像 Linear 的工程语感，但更锋利）
- 反模式：不要"友好亲切"、不要"温暖治愈"、不要 emoji 堆砌、不要"AI 生成感"的紫蓝渐变
- 中文为主，标签/元数据/代码/数字用英文大写等宽字体

### 颜色 Tokens（红线：除 `--acid` 外**不允许任何彩色**）

| Token | 值 | 用途 |
|---|---|---|
| `--bg` | `#FFFFFF` | 页面底 |
| `--ink` | `#000000` | 正文 / 主要边框 |
| `--muted` | `#8A8A8A` | 次要信息、辅助元数据 |
| `--line` | `#E5E5E5` | 分隔线、静态卡片边框 |
| `--acid` | `#FF4F1A` | **唯一强调色（酸橙）** |
| `--acid-deep` | `#D93E0E` | 按压/选中态 |
| `--green` | `#00C853` | 正向指标（极少，仅数据表真增长） |

### 字体

- **标题 (display)**：Space Grotesk 600/700
- **正文 (sans)**：Inter 400/500/600
- **标签 & 代码 (mono)**：JetBrains Mono 400/500，标签全大写
- **CJK 回落**：PingFang SC → Microsoft YaHei → system-ui
- **自托管**：2026-04-23 起通过 `@fontsource/*` 本地化（见后文 P1 记录）

### 禁止清单（AI 写码红线）

- ❌ 所有渐变（`linear-gradient` / `bg-gradient-to-*` / 紫蓝双色）
- ❌ 所有软阴影（`shadow-sm/lg/xl/2xl`、`backdrop-blur`）
- ❌ 大圆角（`rounded-lg/xl/2xl/3xl`）—— **全站固定 `border-radius: 2px`**
- ❌ `hover:scale-105` 等缩放动画
- ❌ emoji 当功能图标
- ❌ "请输入..." 这类亲切语 → 改为 `TYPE HERE.`

### 允许清单

- ✅ **硬阴影**：`box-shadow: 4px 4px 0 var(--ink)`（neobrutalism 风）
- ✅ **硬切**：0ms transition（除了 focus ring 120ms 和数值补间 600ms）
- ✅ **区块编号**：`00 · QUERY` / `01 · ONE-LINER` / ... mono caps + `letter-spacing: 0.14em`

### 动效纪律

| 场景 | Duration | 说明 |
|---|---|---|
| Focus ring 出现 | 120ms | `cubic-bezier(0.22, 1, 0.36, 1)` |
| 数值补间（0→87） | 600ms | 同曲线 |
| 骨架屏呼吸 | 1200ms infinite | linear，1%→6%→1% 透明度 |
| 折叠/展开 | 160ms | ease-out，只改 max-height |
| Hover 变色 | **0ms** | 硬切 |
| 页面切换 | **0ms** | 不做路由过渡 |

---

## 目录结构（真实代码）

```
trendradar-app/
├── .agents/                              · AI 战略文档
│   ├── ARCHITECTURE.md                   · 后端架构设计（v1.0 draft · 未编码）
│   ├── product-marketing-context.md      · V3 产品营销上下文
│   ├── waitlist-integration.md           · Waitlist 集成指南
│   └── email-sequences/
│       └── waitlist.md                   · Email 1-5 + Email 4-B fallback（v1.1）
│
├── .claude/
│   ├── CLAUDE.md                         · Claude Code 项目入口规则
│   ├── PROJECT.md                        · 本文件
│   └── references/awesome-design-md-cn/  · 参考品牌的 DESIGN.md 集合
│
├── apps/
│   ├── api/                              · FastAPI 后端
│   │   ├── Dockerfile                    · 生产构建（含 alembic upgrade head）
│   │   ├── alembic.ini
│   │   ├── alembic/
│   │   │   ├── env.py
│   │   │   ├── script.py.mako
│   │   │   └── versions/
│   │   │       ├── 001_initial.py        · 初始 schema（users/products/chat）
│   │   │       └── 002_add_waitlist.py   · waitlist 表
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py                   · FastAPI 入口（70 行）
│   │   │   ├── core/
│   │   │   │   ├── config.py             · Pydantic Settings · walk-up 查找 .env
│   │   │   │   ├── db.py                 · 异步 SQLAlchemy
│   │   │   │   └── llm_router.py         · DeepSeek/Claude 双路由
│   │   │   ├── api/v1/
│   │   │   │   ├── health.py             · /health + /health/ready
│   │   │   │   ├── chat.py               · /chat/query（SSE 流）
│   │   │   │   └── waitlist.py           · 3 个 endpoint（POST / stats / tally）
│   │   │   ├── models/                   · SQLAlchemy ORM
│   │   │   │   ├── user.py
│   │   │   │   ├── product.py
│   │   │   │   ├── chat.py
│   │   │   │   └── waitlist.py
│   │   │   ├── schemas/                  · Pydantic I/O（与 ORM 分开）
│   │   │   │   ├── chat.py
│   │   │   │   └── waitlist.py
│   │   │   ├── prompts/
│   │   │   │   └── picker.py             · 选品系统 prompt
│   │   │   └── integrations/
│   │   │       ├── resend_client.py      · Resend API 封装
│   │   │       └── email_templates.py    · Email 1 模板
│   │   ├── scripts/
│   │   │   ├── seed_products.py          · 70 条种子数据
│   │   │   └── smoke_test.py             · 4 层启动自检
│   │   ├── tests/
│   │   │   └── test_waitlist.py
│   │   └── pyproject.toml
│   │
│   └── web/                              · Next.js 14.2.35 前端
│       ├── public/
│       │   ├── landing.html              · 🎨 1932 行静态设计师页
│       │   ├── alternatives/             · 4 个 SEO vs 页
│       │   │   ├── index.html
│       │   │   ├── kalodata.html
│       │   │   ├── didadog.html
│       │   │   └── echotik.html
│       │   ├── fonts/
│       │   │   └── fonts.css             · @font-face（手写）· woff2 由脚本生成
│       │   ├── og-image.png
│       │   └── [vendor/, fonts/*.woff2 ← 构建时生成, gitignored]
│       ├── scripts/
│       │   └── copy-fonts.mjs            · 把 Fontsource + Chart.js 复制到 public/
│       ├── src/
│       │   ├── app/
│       │   │   ├── layout.tsx            · Plausible + font preload
│       │   │   ├── page.tsx              · redirect /landing.html 兜底
│       │   │   ├── chat/page.tsx         · 🎯 主产品 demo 页（SSE 流式）
│       │   │   ├── globals.css           · 设计 tokens + 组件 class
│       │   │   └── favicon.ico
│       │   ├── components/
│       │   │   └── ProductCards.tsx      · SVG chart 组件集
│       │   └── lib/
│       │       └── api.ts                · streamPickerQuery() SSE reader
│       ├── next.config.mjs               · rewrites（/ → landing, Tally 代理）
│       ├── tailwind.config.ts            · 设计 tokens 映射
│       ├── tsconfig.json
│       ├── eslint.config.mjs
│       ├── postcss.config.js
│       ├── .env.example
│       └── package.json
│
├── docker-compose.yml                    · 本地 Postgres + Redis
├── .env.example                          · 根 env 模板
├── .gitignore
├── DESIGN.md                             · 389 行设计系统宪法
├── DEPLOY.md                             · Vercel + Railway + Neon 部署手册
└── SETUP.md                              · 本地 30-45 分钟启动指南
```

---

## 关键文件与职责

### 前端关键文件（按修改频率排序）

| 文件 | 职责 | 修改频率 |
|---|---|---|
| `apps/web/public/landing.html` | 主落地页（1932 行）· 所有品牌视觉的源头 | 🔥 高 |
| `apps/web/src/app/chat/page.tsx` | /chat 选品对话页 · SSE 流式结果 | 🟡 中 |
| `apps/web/src/app/layout.tsx` | 根布局 · Plausible 注入 · 字体 preload | 🟢 低 |
| `apps/web/src/app/globals.css` | 设计 tokens + 组件 class（.btn-tr / .tr-card） | 🟢 低 |
| `apps/web/src/components/ProductCards.tsx` | 内联 SVG 图表组件（无 chart lib） | 🟡 中 |
| `apps/web/src/lib/api.ts` | fetch SSE 流的工具函数 | 🟢 低 |
| `apps/web/next.config.mjs` | rewrites 规则（/ → landing / Tally 代理） | 🟢 低 |
| `apps/web/tailwind.config.ts` | 把设计 tokens 暴露给 Tailwind utilities | 🟢 低 |
| `apps/web/public/alternatives/*.html` | 4 个 SEO vs 页（每个 8-15KB） | 🟡 中 |

### 后端关键文件

| 文件 | 职责 |
|---|---|
| `apps/api/app/main.py` | FastAPI 入口 · CORS · lifespan |
| `apps/api/app/core/config.py` | Pydantic Settings · 88 行 · walk-up 查找 .env 兼容 Docker |
| `apps/api/app/core/llm_router.py` | 按 user plan 路由到 DeepSeek / Claude |
| `apps/api/app/prompts/picker.py` | 选品核心 prompt · 定义 JSON 响应 schema |
| `apps/api/app/api/v1/chat.py` | POST /chat/query · SSE 流式返回 LLM 输出 |
| `apps/api/app/api/v1/waitlist.py` | 3 个 endpoint（POST + stats + tally webhook） |
| `apps/api/alembic/versions/001_initial.py` | 初始 schema · users/products/chat_sessions/chat_messages |
| `apps/api/alembic/versions/002_add_waitlist.py` | waitlist 表 |
| `apps/api/Dockerfile` | 生产镜像 · 含 `alembic upgrade head` |

### 文档文件（重要程度排序）

| 文件 | 内容 |
|---|---|
| `.claude/PROJECT.md` | **本文件** · 项目全景 · 单一信息源 |
| `.claude/CLAUDE.md` | Claude Code 入口规则（极简，指向 PROJECT.md） |
| `DESIGN.md` | 设计系统宪法 · 389 行 · 任何 UI 生成前必读 |
| `.agents/product-marketing-context.md` | V3 营销上下文 · ICP · VOC · 竞品 · objections |
| `.agents/email-sequences/waitlist.md` | v1.1 · Email 1-5 + 4-B fallback |
| `.agents/ARCHITECTURE.md` | 后端架构草案 · v1.0 draft · 未实现的部分有标注 |
| `.agents/waitlist-integration.md` | Waitlist 端到端链路 + 配置步骤 |
| `DEPLOY.md` | Vercel + Railway + Neon 首次部署指南 |
| `SETUP.md` | 本地开发 30-45 分钟启动 |

---

## 数据库 Schema

### 已建好的表（migration 001-002）

**users**（账号系统 · 首版最简）
```sql
id UUID PK · email UNIQUE · password_hash · plan（free/pro/team） · plan_expires_at
· lifetime_discount BOOLEAN · created_at · updated_at · deleted_at
```

**products**（选品数据 · 灌入 70 条种子）
```sql
id UUID PK · tiktok_product_id UNIQUE · category · title · price_usd
· image_url · snapshot JSONB（gmv_30d / orders_30d / rating / reviews_count）
· first_seen_at · last_scraped_at
```

**chat_sessions · chat_messages**（/chat 页对话历史）
```sql
sessions: id / user_id / title
messages: id / session_id / role / content / tokens_in / tokens_out
```

**waitlist**（上线前邮箱池）
```sql
id UUID PK · email UNIQUE · position INT · source · converted_user_id FK → users
```

### 规划但还没建的表（见 `.agents/ARCHITECTURE.md`）

- `shops`（TikTok Shop 店铺绑定）
- `dossiers`（选品档案 · 核心 AI 输出）
- `scans`（风口扫描批量推荐）
- `conversations + messages`（替代当前 chat_*）
- `subscriptions`（订阅与支付）

---

## 定价策略

（V3 确认，2026-04-17，经 pricing-strategy skill 过一轮）

| 档位 | 价格 | 定位 | 包含 |
|---|---|---|---|
| **Free** | ¥0 | 试水 | 每日 3 次对话 · 基础竞品分析 · 不含 1688 反搜 |
| **首周体验** | **¥9.9 / 7 天** | Pro 试用钩子 | Pro 全功能（降低新手试错成本） |
| **首月八折** | **¥79 / 月** | Pro 首月续订价 | Pro 全功能 |
| **Pro 月卡** | **¥99 / 月** | 🏆 主推 | 无限对话 + 痛点分析 + 利润测算 + 爆品日报 + 飞书/Notion 导出 |
| **Pro 年卡** | **¥899 / 年**（≈ ¥75/月，省 25%） | 年付优惠 | 同 Pro 月卡 |
| **Team** | **¥399 / 月 · 5 席** | 工作室/团队 | Pro 全功能 + 共享工作区 + 优先客服 |
| **Launch 限时** | **前 100 名 = 终身 5 折** | 冷启动钩子 | 严格封顶 100 人 |

### 核心锚点
**¥99/月 vs Kalodata $99/月（≈¥700）—— 便宜 7 倍是主武器。**

### Pricing Roadmap

- **T+0 到 T+3 个月**：价格冻结，收集数据（转化率 / ARPU / churn / 功能付费率）
- **T+6 个月**（500-1000 付费用户后）：首次调整
  - 方案 A 保守：Pro ¥99 → ¥129（+30%）/ Team ¥399 → ¥499
  - 方案 B 激进：保留 ¥99，新增 Pro+ ¥199/月（对标 Kalodata Professional，含 API + 白标 + GPT-4 级推理）
- **T+12 个月**（扩展 Amazon / 东南亚后）：按市场分层
  - Pro US-only ¥99 / Pro US+SEA ¥159 / Pro Global ¥229

### Grandfather 铁律
- 每次提价老用户锁价 12 个月
- 每次提价必须同时加功能（tied to value，不能裸涨）

### 风险对冲
- **¥9.9 首周羊毛党** → 绑定手机号 + 新用户定义（首次注册 24h 内）
- **终身 5 折 100 人长期让利约 ¥12 万**（100 × ¥49.5 × 24 月） → **必须严格封顶 100 人**，提前做好计数系统
- **Team ¥399 若 T+3 占比 < 5%** → 降到 ¥299 或拆成 ¥199(3 席) + ¥399(5 席) 两档

---

## Waitlist 链路

### 当前架构（2026-04-22 上线）

```
landing.html 底部表单（原生 HTML form）
       ↓ JS validate (email regex)
fetch POST /api/tally/forms/pbPg1Z/respond
       ↓ Next.js rewrite proxy（same-origin，绕过 CORS）
https://api.tally.so/forms/pbPg1Z/respond
       ↓ Tally 记录到后台
Tally webhook（未来：Resend 发 Email 1）
```

### 为什么选这条路

**iteration 1**：Tally iframe 嵌入 → 🚫 "Made with Tally" 广告格格不入
**iteration 2**：原生表单 + 直接 fetch Tally API → 🚫 CORS 拦截（Tally 只允许 https://tally.so 跨域）
**iteration 3（当前）**：Next.js rewrite `/api/tally/:path* → https://api.tally.so/:path*`，浏览器看到的是同源请求，没有 preflight

### 已在代码中的配置

- 表单 ID：`pbPg1Z`（`.agents/waitlist-integration.md` 里记录 ← 但现在直接 POST 不走 webhook 也 OK）
- 邮箱字段 ID：`c27ad1a8-f574-4016-bf8d-c11293df70f3`
- 验证：`/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/` + type="email"
- 成功状态：自有品牌"锁定 5 折"深色卡片（不用 Tally 的完成页）
- 失败状态：`role="alert"` 可访问报错

### FastAPI 后端备选

已经写好但未部署（因为 Railway 还没启动）：
- `POST /api/v1/waitlist` · 直接给 JS 调用
- `GET /api/v1/waitlist/stats` · 返回总数 + 剩余创始人名额
- `POST /api/v1/waitlist/tally` · Tally webhook 接收端（HMAC 验签）

Tally 集成当时把 Email 1 的自动发送和 Resend 集成写进了代码 —— 部署 Railway + 配置 Resend 后可启用。

---

## 邮件序列

完整版见 `.agents/email-sequences/waitlist.md`（v1.1 · 552 行）

### 序列总览

**触发**：提交 waitlist 邮箱 → 自动进入序列
**节奏**：T+0 → T+3 → T+14 → T+42 → 上线前 3 天（6-8 周周期）
**发件人**：`TrendRadar Team <hi@{{your_domain}}>`（域名确定后替换）
**目标漏斗**：提交 → 开信率 40%+ → 点击率 15%+ → 上线首周付费转化 8-12%

### 五封邮件

| # | 时机 | 主题 | 目标 | 预期打开率 |
|---|---|---|---|---|
| 1 | T+0（60 秒内） | "你锁住了 ✓ TrendRadar 前 100 名终身 5 折" | 确认入列 + 锁定 5 折 + 降低取关 | 55-65% |
| 2 | T+3 | "在美区亏过 3 万块之后" | 创始人故事 · 建立信任 | 35-45% |
| 3 | T+14 | "TikTok Shop 选品 5 大坑（第 3 个最坑）" | 纯教育 · 建立权威 | 30-40% |
| 4 | T+42 | "beta 用户：3 周利润翻倍，不是故事" | 用户案例 · 社会证明 | 25-35% |
| 4-B | T+42 fallback | "产品进度 · 第 6 周 · 3 个新功能上线" | 无 beta 证言时的备用 | 30-40% |
| 5 | 上线前 72h | "周三上线 · 你的 ¥449 锁定还有 72 小时" | **最高 stakes 转化** | 45-55% |

### 关键 2026-04 数据复核（Email 3）

经 2026-04-23 一轮 fact-check，所有 TikTok Shop US 费率都按 2026 年最新政策更正：
- Referral fee **6%**（原 "6-8%" 是错的）· **新手首 30 天 3%** ← 重要红利
- SPS 考核期从 30 天 → **60 天**（2026 调整）
- 退货率平台整体 +23% vs 传统电商
- GMV Max 广告标榜 ROAS 3-5x 扣除 organic 归因后实际 **2.5-3x**
- 退款手续费 = referral fee 的 20%（按 SKU 封顶 $5）

**每 3 个月复核一次费率**（写进了 checklist）。

### Email 5 A/B/C subject 对

最高转化那封不押单 subject：
- A 版（时间+价格锚点）：周三上线 · 你的 ¥449 锁定还有 72 小时
- B 版（个性化+好奇）：{{first_name}}，你是第 {{waitlist_position}} 位 · 邀请链接已就绪
- C 版（稀缺+FOMO）：100 个终身 5 折名额 · 周三早上 10:00 开抢

建议 10%/10%/80% 分流，胜者（开信率+点击率综合）发给主群。

---

## 分析 · Plausible

### 已接入（2026-04-22）

**覆盖范围**：所有公开页面
- `/`（landing.html）
- `/alternatives/{index, kalodata, didadog, echotik}`
- `/chat`（通过 Next.js root layout 注入）

**tracker 变体**：`https://plausible.io/js/script.outbound-links.file-downloads.js`（扩展版 · 自动追踪外链 + 文件下载）

**domain 配置**：目前 `trendradar-app-sigma.vercel.app`。**域名换掉时记得同步改**。

### 自定义事件

| 事件名 | 触发位置 | 备注 |
|---|---|---|
| `Waitlist Signup` | Tally POST 成功后 | landing.html line ~1925 |
| `CTA Click` | 所有 `a.btn` 和 `a[href="#cta"]` 点击 | landing.html line ~2016 · 带 `{ props: { label } }` |
| `Outbound Link Click` | 任何外链 | Plausible 自动 |
| `File Download` | 任何 pdf/csv/xlsx 链接 | Plausible 自动（未来启用） |

### 待办

- 用户注册 Plausible 账号 + 创建 site（domain: `trendradar-app-sigma.vercel.app`, timezone: Asia/Shanghai）
- Verify first pageview

---

## 截至今天做了什么 · 时间线

### 2026-04-16 · 脚手架（commits 5cb8fce → 8f9e8a1）

- `5cb8fce` · TrendRadar MVP 全栈骨架（FastAPI + Next.js + Postgres）
- `f5f6c46` · 修 config .env walk-up 兼容 Docker
- `0eddde3` · 补齐 Next.js 14 骨架 + Tailwind + chat 页
- `facc1d8` · 删掉误嵌的 web-scaffold/ 重复文件夹
- `a9670c3` · bump Next 到 14.2.33（CVE 修复）
- `17748f6` · 清理重复配置 + 移除明文密钥
- `5618e18` · 做正式落地页 + 产品卡片式结果 + 预设查询 chips
- `69b3de6` · 给 landing 换成设计师级橙色页（1932 行 · DESIGN.md 宪法确立）
- `ca25a34` · /chat UI 对齐橙色落地页审美

### 2026-04-21 · 内容与 SEO

- `d0f2360` · 加 vs 页（/alternatives）+ 定价更新 + customer research + chat a11y
- `7fa3416` · 修 /alternatives/* clean URLs（rewrites）+ landing 链接
- `2187319` · vs 页 CTA 卡片、clean URLs、waitlist 邮件草稿

### 2026-04-22 · Waitlist 上线（📦 最密集的一天）

- `f6221a8` · waitlist endpoint + Tally webhook + 欢迎邮件
- `8f9e8a1` · 减少 landing 装饰性英文（中文化）
- `5068f94` · 修 Chart.js · unpkg + cdnjs 双 fallback 解决 jsdelivr CN 问题
- `5efffb8` · 换 Formspree → Tally.so 嵌入（表单 pbPg1Z）
- `bc83784` · 盖住 Tally 免费版 ad 页，替换成品牌成功态
- `c55d990` · 彻底摒弃 iframe，改原生表单
- `769a5aa` · 通过 Next.js rewrite proxy 同源 POST 到 Tally API（绕 CORS）

### 2026-04-22 · 分析接入

- `14c7388` · 激活 Plausible across all pages（landing + 4 alternatives + /chat）

### 2026-04-23（今天）· 打磨 + CDN 本地化

- `63a4261` · 邮件序列加固：
  - Email 3 数据按 2026-04 TikTok Shop 新政复核
  - 新增 Email 4-B 产品进度速报 fallback
  - Email 5 加 A/B/C subject 测试对
- `6228988` · 自托管字体 + Chart.js（CN 加速）：
  - 添加 `@fontsource/*` 3 包 + `chart.js` 依赖
  - `scripts/copy-fonts.mjs` 构建时复制 woff2 + Chart.js UMD 到 `public/`
  - 所有 5 个静态 HTML + React layout 切到本地 `/fonts/` 和 `/vendor/`
  - `globals.css` 手写 `--font-*` CSS 变量，取代 `next/font/google`

### 做完的功能清单（P0 + P1）

**P0 · 已完成**
- [x] 全栈骨架（FastAPI + Next.js + Neon 本地 docker-compose）
- [x] Landing 页（1932 行 · 设计师级 · 橙色品牌）
- [x] /chat demo 页（SSE 流式 · SVG 图表 · 4 预设 chips）
- [x] 4 个 SEO vs 页（index / kalodata / didadog / echotik · 含 clean URLs）
- [x] Design System 宪法（DESIGN.md · 389 行）
- [x] Waitlist 端到端链路（原生表单 → 同源代理 → Tally）
- [x] Email 1 欢迎邮件（代码已写，等 Resend 配完启用）

**P1 · 已完成**
- [x] Plausible 接入所有页面（含 outbound-links + file-downloads）
- [x] 邮件序列 v1.1（Email 1-5 + 4-B fallback · 2026-04 数据核实）
- [x] 字体 + Chart.js 本地化（CN 加速 3-5x）
- [x] ICP / Persona / VOC / 竞品 / Pricing 研究完成（6 个独立来源）

---

## 接下来要做什么 · 路线图

### P2 · 后端上线（阻塞中 · 主线）

**为什么阻塞**：需要域名才能配 Resend DKIM/SPF/DMARC；Railway 部署本身不依赖域名但**发邮件**依赖。

**分步清单**（按顺序）：
1. **买域名**（卡在付款 · 详见下面的"域名决策"章节）
2. **Railway 部署 FastAPI 后端**
   - New Project → Deploy from GitHub repo → apps/api
   - Set env vars（见下方"环境变量清单"）
   - Generate domain（`trendradar-api-production.up.railway.app`）
   - 首次 build 会自动跑 `alembic upgrade head`
3. **Neon Postgres 创建**
   - US-East-2 Ohio
   - 改连接串格式：`postgresql+asyncpg://`、`ssl=require`
4. **Seed 数据**（本地连 Neon 跑一次 `python scripts/seed_products.py`）
5. **Resend 绑域名 + DNS**（SPF/DKIM/DMARC 3 条记录）
6. **接通 Vercel 前端 → Railway 后端**（设置 CORS_ORIGINS + 前端 NEXT_PUBLIC_API_BASE_URL）

### P3 · Email 2-5 自动化

**依赖**：P2 完成（需要 Resend + 任务队列）

- 选队列栈：`arq`（Redis）或 pg-based job queue
- T+3 / T+14 / T+42 / 上线前 3 天的 cron 触发
- 把 `.agents/email-sequences/waitlist.md` 里的文案转成 React Email 模板
- A/B subject 分流机制（Resend 原生支持）
- `/unsubscribe?token=` 端点 + waitlist 表加 `unsubscribed_at` 字段

### P4 · Admin 视图

**依赖**：P2 完成

- `/admin/waitlist`：总数、按 source 分布、每日新增、转化漏斗
- 简单 basic auth 或 magic link 登录
- 可选：导出 CSV

### P5 · 真实数据接入

**依赖**：P2 完成 + 找到数据源

- Apify TikTok Shop scraper（$45/mo plan 起步）
- Apify 1688 Image Search Actor
- Cron 每 24h 灌一次 `products` 表
- `/chat` 的 `_candidates_for` 从 mock 改成真查库

### P6 · Dossier 档案系统

**依赖**：P5 真实数据

- `dossiers` 表（设计完成，未建）
- LangGraph Agent 编排：需求分析 → 利润测算 → 风险评分 → 供应商匹配
- /app/dossier/{id} 详情页（PDF 导出）
- 免费用户限制 3 份/月，Pro 无限

### P7 · 用户系统 + 支付

**依赖**：P6 核心功能稳定

- JWT auth（email + password + 手机号绑定）
- WeChat Pay / Alipay 集成（国内用户优先）
- Stripe（Team 档/未来海外）
- 订阅生命周期：续费提醒、失败重试、降级、cancel 保留
- `lifetime_discount = true` 的 5 折守护

### P8 · 上线前最后冲刺

- Email 4 · 替换真实 beta 用户证言（至少 3 位书面授权）
- Email 5 · 专属邀请链接生成器（token + 48h 过期）
- Terms of Service / Privacy Policy（国内 + GDPR 双版本）
- 上线日期冻结（T-7 天）
- 内部测试发送（Gmail / QQ / 163 / Outlook 四客户端）

---

## 域名决策

### 当前状态（2026-04-23）
**卡在付款环节**。已确认：
- `trendradar.ai` · 被注册（Cloudflare 显示 Unavailable）
- `trendradar.com` · 未查
- `baopin.ai` · 被注册
- 用户最终选择：**`pinsonar.ai`** or `pinsonar.com`（倾向 .com 因价差 $70）

### 候选排序（按中国卖家友好度）

| 候选 | 后缀 | 年费 | 品牌意图 | 中国卖家体感 | 我的建议 |
|---|---|---|---|---|---|
| `pinsonar.com` | .com | ~$10 | 品 + Sonar 声呐 | 陌生但无负担 | ⭐⭐⭐⭐ |
| `pinsonar.ai` | .ai | ~$80 | 同上 + AI 品牌感 | 同上 + 贵 | ⭐⭐⭐ |
| `trendradar.com` | .com | ~$10 | 原品牌名 | 最顺 | ⭐⭐⭐⭐⭐（未查） |
| `trendpick.com` | .com | ~$10 | Trend + Pick（选品） | 好念易懂 | ⭐⭐⭐⭐ |
| `radarpick.com` | .com | ~$10 | Radar + Pick | 较顺 | ⭐⭐⭐⭐ |

### 注册商决策
**首选 Cloudflare Registrar**（成本价 · 免费 WHOIS · 整合 DNS+CDN+SSL）
- 账号里需要先挂一个 free site 才能用 Register Domains
- 不支持国内双币卡（70% 概率被风控）→ 推荐 PayPal

**备选 Porkbun**（无账号依赖 · 界面友好 · 支持支付宝）

### 不能选
- ❌ 阿里云 / 腾讯云（国内备案麻烦，且 `.ai` 经常买不到）
- ❌ GoDaddy / Namecheap（`.ai` 贵、WHOIS 隐私加钱）

### 域名要干的事

一旦拿到域名，需要**立刻改的地方**（7 个文件 + Plausible dashboard）：
- `apps/web/public/landing.html`（line 20 canonical + og URL）
- `apps/web/public/alternatives/*.html` × 4（canonical + og）
- `apps/web/src/app/layout.tsx`（Plausible domain + OG url + metadata URL）
- `apps/api/app/core/config.py`（CORS_ORIGINS default）
- `.agents/email-sequences/waitlist.md`（发件人 `{{your_domain}}` 替换）
- `.env.example` + `.agents/waitlist-integration.md`（SITE_URL）

以及：
- Vercel Dashboard → Project → Settings → Domains → Add
- Cloudflare DNS 加 CNAME（Vercel 提供）+ 等 SSL 签发
- Resend Domains → Add + 配 SPF/DKIM/DMARC 三条 TXT 记录
- Plausible dashboard → Site Settings → 改 domain

---

## 环境变量清单

### 根 `.env`（本地开发）

```env
# ==== LLM ====
DEEPSEEK_API_KEY=sk-...                    # https://platform.deepseek.com
ANTHROPIC_API_KEY=sk-ant-...               # 可选，Pro 用户用
LLM_FREE_TIER_MODEL=deepseek-chat
LLM_PRO_TIER_MODEL=claude-sonnet-4-5

# ==== Database（本地 Docker）====
DATABASE_URL=postgresql+asyncpg://trendradar:trendradar@localhost:5432/trendradar
REDIS_URL=redis://localhost:6379/0

# ==== App ====
APP_ENV=development
SECRET_KEY=生成：openssl rand -hex 32
CORS_ORIGINS=http://localhost:3000
```

### Railway env（生产后端）

```env
# 所有本地 .env 的 + 以下
DATABASE_URL=postgresql+asyncpg://neondb_owner:xxx@ep-xxx.us-east-2.aws.neon.tech/neondb?ssl=require
APP_ENV=production
CORS_ORIGINS=https://pinsonar.com,https://www.pinsonar.com    # 替换为实际域名

# ==== Email ====
SEND_EMAILS=true                           # 默认 false → dry-run
RESEND_API_KEY=re_xxx
RESEND_FROM_EMAIL=TrendRadar Team <hi@pinsonar.com>
RESEND_REPLY_TO=hi@pinsonar.com

# ==== Tally ====
TALLY_SIGNING_SECRET=xxx                   # Tally → Webhooks → 生成

# ==== Site ====
SITE_URL=https://pinsonar.com
FOUNDERS_SEAT_CAP=100
```

### Vercel env（前端）

```env
NEXT_PUBLIC_API_BASE_URL=https://trendradar-api-production.up.railway.app
```

---

## Gotchas · 踩过的坑

### 沙盒环境

1. **Sandbox 无法出网到：** `fonts.gstatic.com` · `tally.so` · `rdap.nic.ai` · `registry.npmjs.org`（部分） → 涉及 CDN 本地化 / 域名查询 / npm install 的任务由**用户在 Windows 跑**
2. **Sandbox 无法 push 到 GitHub**（proxy 403） → 用户从 Windows PowerShell push
3. **next build 在沙盒失败**（需要下载 SWC 二进制） → 本地 build，`tsc --noEmit` 可以在沙盒验证

### Next.js 配置

4. **`/` rewrite 顺序**：`next.config.mjs` 的 `beforeFiles` 才能让 `/ → /landing.html` 赢过 App Router 的 page.tsx
5. **Clean URLs for /alternatives**：也走 `beforeFiles` rewrite（source: `/alternatives/kalodata` · destination: `/alternatives/kalodata.html`）
6. **next/font/google 在沙盒 build 失败**（要联网下字体）· 这也是改用 Fontsource 的原因之一
7. **Tally CORS 绕过**：同源 rewrite `/api/tally/:path* → https://api.tally.so/:path*`，浏览器看到的是同源请求

### 数据库

8. **Neon 连接串格式**：`postgresql://` → `postgresql+asyncpg://` · `sslmode=require` → `ssl=require`（我们用 asyncpg 驱动）
9. **config.py walk-up 查找 .env**：修复过一个 Docker 内 `Path.parents[4]` 越界的 bug（`f5f6c46`）
10. **所有金额字段用 NUMERIC(12,2)**，不用 float（精度问题）
11. **所有表 id 用 UUID**（不暴露自增 ID，防爬）

### Chart.js / 前端

12. **Chart.js 原先用 jsdelivr** → 国内经常加载不出来 → 先改 unpkg + cdnjs 双 fallback（`5068f94`） → 最终 2026-04-23 彻底本地化（`6228988`）
13. **React 端禁用 Chart.js / Recharts / D3**：只用 `ProductCards.tsx` 里的内联 SVG（design system 要求）
14. **字体 preload**：只 preload above-the-fold 的两个 weight（Space Grotesk 600 + Inter 400），否则浪费带宽

### 部署

15. **Vercel "Configuration Settings differ" 警告**：Framework / Build 改过后要 "Redeploy without cache"
16. **重复配置文件**：曾经有过 `next.config.ts` 和 `.mjs` 同时存在 · `postcss.config.mjs`（TW v4 语法，但装的是 v3）· `ds_api_key.txt`（明文密钥） → 已清理
17. **新域名邮件预热**：Resend 新域名前 7 天日发送量 < 1000 封，否则进垃圾箱

### API Key 事故

18. **2026-04-22** 用户曾把 Tally Account API key `tly-ZosdaHYHySfYx4Uq6M8Lsp8R67EuTtPO` 粘到聊天 → **该 key 必须 revoke**（实际上我们用的是 anonymous `/respond` endpoint 不需要 key · 用户已被告知）

---

## 开发 · 部署 workflow

### 本地开发（首次 30-45 分钟）

见 `SETUP.md` 完整版。精简流程：

```powershell
# 一次性
cd C:\Users\Mqx95\Documents\Claude\Projects\trendradar-app
Copy-Item .env.example .env
# 编辑 .env 填 DEEPSEEK_API_KEY
docker compose up -d

cd apps\api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -e .
alembic upgrade head
python scripts/smoke_test.py  # 4 ✓ = 全绿

cd ..\web
npm install  # 会装 @fontsource/* + chart.js，触发 copy-fonts

# 日常开发 · 3 个 PowerShell 窗口
# 窗口 1: docker compose up -d（只需第一次）
# 窗口 2: cd apps\api; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --reload
# 窗口 3: cd apps\web; npm run dev
```

### Git workflow（sandbox ↔ Windows）

**沙盒里 commit**：
```bash
git -c user.name=Hemu -c user.email=806122923@qq.com commit -m "..."
```
**用户在 Windows push**（沙盒 push 被 proxy 拦）：
```powershell
git pull
git push
```

### 部署流（Vercel + Railway + Neon）

见 `DEPLOY.md` 完整 6 步指南。关键点：
1. Vercel 自动部署（git push main 触发）
2. Railway 需要在 Settings 设 Root Directory `apps/api` + Watch Paths `apps/api/**`
3. Neon 连接串改格式（asyncpg + ssl=require）
4. Railway Dockerfile 会自动跑 `alembic upgrade head`
5. 种子数据用本地 shell 连 Neon 跑一次 `python scripts/seed_products.py`
6. CORS：Vercel 域名 → Railway `CORS_ORIGINS`

---

## 与 AI Agent 协作规则

### 必读文件（按重要度）

1. `.claude/PROJECT.md` ← 本文件，全景入口
2. `DESIGN.md` ← UI 生成前必读（389 行，但有 §10 摘要可快读）
3. `.agents/product-marketing-context.md` ← 写文案 / 做营销决策时必读
4. `.agents/email-sequences/waitlist.md` ← 邮件内容决策时必读

### Commit 约定

- Author：`Hemu <806122923@qq.com>`
- 命令：`git -c user.name=Hemu -c user.email=806122923@qq.com commit -m "..."`
- 格式：`<type>(<scope>): <subject>` 偶尔配上下文多段 body
- Type：`feat` / `fix` / `perf` / `style` / `email` / `analytics` / `chore`

### 红线（不要做的事）

- ❌ **不要把 landing.html 改成 React**（它是静态设计师文件，故意保持 vanilla HTML）
- ❌ **不要在 React 端引入 Chart.js / D3 / Recharts**（设计系统只准内联 SVG）
- ❌ **不要加渐变、软阴影、大圆角**（见 DESIGN.md §9）
- ❌ **不要用 emoji 当功能图标**（装饰性偶尔 OK）
- ❌ **不要放 "请输入..." 类亲切 placeholder** → 用 `TYPE HERE.`
- ❌ **不要加新的 npm deps 不先问**（构建体积红线）
- ❌ **不要 skip Hemu 作者**（每次 commit 都要）

### 快速手势（用户对 AI 说的话）

| 用户说 | AI 做 |
|---|---|
| "P0 我已经做过了，现在来 P1" | 参考本文档的路线图推进下一阶段 |
| "继续" | 继续上一个被中断的任务 |
| "这里太 AI 了" | 按 DESIGN.md §9 反模式检查并修改 |
| "帮我打磨文案" | 用 copy-editing skill + 读 product-marketing-context.md |
| "改英文太多" | 把次要标签 / placeholder 中文化，核心 label 保留 mono UPPERCASE |

### 沙盒 vs Windows 分工

| 任务类型 | 谁做 |
|---|---|
| 代码编辑 · grep · 文档写作 · git commit | 沙盒（我） |
| `npm install` / `pip install` / `docker compose` | 用户 Windows |
| `git push` · `git pull` | 用户 Windows |
| 浏览器访问 · Dashboard 配置（Vercel/Railway/Tally/...） | 用户 |
| 域名购买 · DNS 配置 | 用户 |
| Resend DKIM 验证 | 用户（要登 DNS 面板） |
| 查外链 / WHOIS（egress 被限） | 用户截图给我看 |

---

## 附录 A · 当前文件清单（tracked）

```
根级别:
  .env.example
  .gitignore
  DEPLOY.md
  DESIGN.md
  SETUP.md
  docker-compose.yml

.agents/:
  ARCHITECTURE.md                         后端架构 v1.0 草案（未实现）
  product-marketing-context.md            V3 营销上下文（completed）
  waitlist-integration.md                 Waitlist 端到端链路
  email-sequences/waitlist.md             邮件序列 v1.1（完成）

.claude/:
  CLAUDE.md                               极简入口 → PROJECT.md
  PROJECT.md                              本文件

apps/api/:
  Dockerfile · alembic.ini · pyproject.toml
  alembic/env.py · script.py.mako
  alembic/versions/001_initial.py
  alembic/versions/002_add_waitlist.py
  app/__init__.py · main.py
  app/core/{config,db,llm_router}.py
  app/api/v1/{health,chat,waitlist}.py
  app/models/{user,product,chat,waitlist}.py
  app/schemas/{chat,waitlist}.py
  app/prompts/picker.py
  app/integrations/{resend_client,email_templates}.py
  scripts/{seed_products,smoke_test}.py
  tests/test_waitlist.py
  .dockerignore

apps/web/:
  package.json · package-lock.json · tsconfig.json
  next.config.mjs · tailwind.config.ts · postcss.config.js
  eslint.config.mjs · next-env.d.ts
  README.md · CLAUDE.md · AGENTS.md · .env.example · .gitignore
  public/landing.html                     1932 行 · 主落地页
  public/alternatives/index.html          总 vs 页
  public/alternatives/kalodata.html       vs Kalodata
  public/alternatives/didadog.html        vs 嘀嗒狗
  public/alternatives/echotik.html        vs EchoTik
  public/fonts/fonts.css                  手写 @font-face
  public/{favicon,og-image}.png · public/*.svg
  scripts/copy-fonts.mjs                  构建时复制 woff2 + Chart.js
  src/app/{layout,page,globals.css,favicon.ico}.tsx
  src/app/chat/page.tsx                   /chat demo
  src/components/ProductCards.tsx         SVG 图表组件
  src/lib/api.ts                          SSE fetch 客户端
```

## 附录 B · 近期 git log（完整版）

```
6228988 2026-04-23 · perf: self-host fonts + Chart.js (CN-friendly)
63a4261 2026-04-23 · email: harden waitlist sequence (Email 3 data, 4-B fallback, 5 A/B)
14c7388 2026-04-22 · analytics: activate Plausible across all pages
769a5aa 2026-04-22 · feat(waitlist): wire native form to Tally via same-origin proxy
c55d990 2026-04-22 · feat(landing): native waitlist form replaces Tally iframe
bc83784 2026-04-22 · feat(landing): branded success state overrides Tally's ad page
5efffb8 2026-04-22 · feat(landing): replace Formspree form with Tally.so embed
5068f94 2026-04-22 · fix(landing): robust Chart.js loading with unpkg + cdnjs fallback
8f9e8a1 2026-04-22 · style: reduce decorative English on landing UI
f6221a8 2026-04-22 · feat: waitlist endpoint + Tally webhook + welcome email
2187319 2026-04-21 · feat: vs-page CTA cards, clean URLs, waitlist email drafts
7fa3416 2026-04-21 · fix: clean URLs for /alternatives/* + link from landing
d0f2360 2026-04-21 · feat: add vs pages + pricing update + customer research + chat a11y
ca25a34 2026-04-16 · feat(web): overhaul /chat UI to match orange landing aesthetic
69b3de6 2026-04-16 · feat(web): swap generic landing for designer-grade orange page
5618e18 2026-04-16 · feat(web): 做正式落地页 + 产品卡片式结果 + 预设查询 chips
17748f6 2026-04-16 · chore: 清理重复配置文件 + 移除明文密钥
a9670c3 2026-04-16 · chore(web): bump next to 14.2.33 (CVE fix)
facc1d8 2026-04-16 · chore(web): 删掉误嵌的 web-scaffold/ 重复文件夹
0eddde3 2026-04-16 · feat(web): 补齐 Next.js 14 骨架 + Tailwind + chat 页
f5f6c46 2026-04-16 · fix(config): 用 walk-up 查找 .env，避免 Docker 里 parents[4] 越界
5cb8fce 2026-04-16 · feat: TrendRadar MVP 全栈骨架（FastAPI + Next.js + Postgres）
```

---

**文档结束**。这份文档 = **项目的唯一事实源**。有任何与它矛盾的说法，以本文档为准；发现不准的地方就地修正。
