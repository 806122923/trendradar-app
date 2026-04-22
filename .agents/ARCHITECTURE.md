# TrendRadar 后端架构设计

**版本**：v1.0-draft
**最后更新**：2026-04-22
**状态**：待 review · 未开始编码

---

## 0. TL;DR（30 秒版）

- **后端**：FastAPI（Python 3.12）+ SQLAlchemy 2.0 + Alembic migrations
- **数据库**：Neon Postgres（Serverless PG，免费层 3GB）
- **AI 编排**：LangGraph（状态机式 Agent）+ DeepSeek API（OpenAI 兼容）
- **数据抓取**：全 Apify（TikTok Shop Scraper + 1688 Image Search Actor）
- **任务队列**：Postgres-based（`arq` 或 SQLAlchemy 原生 job queue）
- **部署**：Railway（后端）+ Vercel（前端）+ Neon（DB）
- **存储**：Cloudflare R2（图片、档案 PDF）
- **监控**：Sentry + Logtail + Plausible
- **预估月成本（100 beta 用户）**：$60-80

---

## 1. 目录结构

```
trendradar-app/
├── apps/
│   ├── web/                    · Next.js 前端（已存在）
│   └── api/                    · 🆕 FastAPI 后端（本次新建）
│       ├── pyproject.toml
│       ├── alembic.ini
│       ├── alembic/            · DB 迁移
│       │   └── versions/
│       ├── src/
│       │   └── trendradar/
│       │       ├── __init__.py
│       │       ├── main.py           · FastAPI app 入口
│       │       ├── config.py         · Pydantic Settings (env vars)
│       │       ├── deps.py           · FastAPI 依赖注入（DB session / auth）
│       │       │
│       │       ├── api/              · HTTP 路由层
│       │       │   ├── __init__.py
│       │       │   ├── auth.py       · /auth/*
│       │       │   ├── users.py      · /users/*
│       │       │   ├── dossiers.py   · /dossiers/*（选品档案）
│       │       │   ├── scans.py      · /scans/*（风口扫描）
│       │       │   ├── agent.py      · /agent/chat（AI 对话）
│       │       │   └── webhooks.py   · /webhooks/*（Apify 回调、支付回调）
│       │       │
│       │       ├── models/           · SQLAlchemy ORM
│       │       │   ├── __init__.py
│       │       │   ├── base.py       · Declarative base + UUID mixin
│       │       │   ├── user.py
│       │       │   ├── shop.py
│       │       │   ├── dossier.py
│       │       │   ├── product.py
│       │       │   ├── scan.py
│       │       │   ├── conversation.py
│       │       │   └── subscription.py
│       │       │
│       │       ├── schemas/          · Pydantic I/O schemas（和 ORM 分开）
│       │       │   └── (对应 models)
│       │       │
│       │       ├── services/         · 业务逻辑层
│       │       │   ├── auth_service.py
│       │       │   ├── dossier_service.py
│       │       │   ├── scan_service.py
│       │       │   ├── profit_calc.py        · 利润测算
│       │       │   └── risk_scoring.py       · 风险评分
│       │       │
│       │       ├── agents/           · LangGraph Agent 定义
│       │       │   ├── __init__.py
│       │       │   ├── dossier_agent.py      · 选品档案生成
│       │       │   ├── scan_agent.py         · 风口扫描
│       │       │   ├── chat_agent.py         · 通用对话
│       │       │   ├── tools/                · Agent 可调用的工具
│       │       │   │   ├── apify_tiktok.py
│       │       │   │   ├── apify_1688.py
│       │       │   │   ├── db_query.py
│       │       │   │   └── profit_calc_tool.py
│       │       │   └── prompts/              · 系统提示模板
│       │       │       ├── dossier.md
│       │       │       └── scan.md
│       │       │
│       │       ├── integrations/     · 外部服务封装
│       │       │   ├── apify_client.py
│       │       │   ├── deepseek_client.py
│       │       │   ├── resend_client.py
│       │       │   └── stripe_client.py      · （或 wechatpay / alipay）
│       │       │
│       │       ├── workers/          · 后台任务
│       │       │   ├── __init__.py
│       │       │   ├── queue.py              · 任务队列（arq-based）
│       │       │   └── jobs/
│       │       │       ├── run_scan.py
│       │       │       ├── generate_dossier.py
│       │       │       └── sync_tiktok_shop.py
│       │       │
│       │       └── utils/
│       │           ├── logging.py
│       │           ├── errors.py
│       │           └── security.py
│       │
│       └── tests/
│           ├── conftest.py
│           ├── test_api/
│           ├── test_services/
│           └── test_agents/
│
└── .agents/                    · 战略 / 架构文档
    ├── ARCHITECTURE.md         · 本文件
    ├── product-marketing-context.md
    └── email-sequences/
```

---

## 2. 数据库 Schema

**约定**：
- 所有表 `id` 为 UUID（不暴露自增 ID，防爬）
- 所有表有 `created_at` / `updated_at`
- 软删用 `deleted_at`，不真删
- 金额字段用 `NUMERIC(12,2)`（美分），不用 float
- 所有 FK 加索引

---

### 2.1 核心表

```sql
-- 用户（账号系统）
CREATE TABLE users (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email         VARCHAR(255) UNIQUE NOT NULL,
  phone         VARCHAR(32),
  password_hash VARCHAR(255),              -- NULL 表示仅 OAuth
  display_name  VARCHAR(64),
  avatar_url    TEXT,
  plan          VARCHAR(32) NOT NULL DEFAULT 'free',  -- free / pro / team
  plan_expires_at  TIMESTAMPTZ,
  lifetime_discount BOOLEAN DEFAULT FALSE,    -- 前 100 名终身 5 折
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at    TIMESTAMPTZ
);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_plan ON users(plan);

-- Waitlist（上线前留邮箱的人）
CREATE TABLE waitlist (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email         VARCHAR(255) UNIQUE NOT NULL,
  position      INT NOT NULL,              -- 第 N 位加入
  source        VARCHAR(64),               -- utm_source
  converted_user_id UUID REFERENCES users(id),  -- 上线后转成 user
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX idx_waitlist_email ON waitlist(email);

-- TikTok Shop 店铺绑定
CREATE TABLE shops (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  region        VARCHAR(8) NOT NULL DEFAULT 'US',
  shop_name     VARCHAR(128),
  shop_url      TEXT,
  seller_id     VARCHAR(64),
  sync_status   VARCHAR(32) DEFAULT 'pending',  -- pending / syncing / ready / failed
  last_synced_at TIMESTAMPTZ,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_shops_user ON shops(user_id);

-- 商品（抓取或用户关注的 TikTok Shop 商品）
CREATE TABLE products (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tiktok_product_id VARCHAR(64) UNIQUE,
  category      VARCHAR(128),
  title         TEXT,
  price_usd     NUMERIC(10,2),
  image_url     TEXT,
  -- 抓取快照（JSONB，省表数量）
  snapshot      JSONB NOT NULL DEFAULT '{}',  -- { gmv_30d, orders_30d, rating, reviews_count, ... }
  first_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_scraped_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_tiktok_id ON products(tiktok_product_id);

-- 选品档案（AI 生成的核心输出）
CREATE TABLE dossiers (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  product_id    UUID REFERENCES products(id),
  query         TEXT NOT NULL,             -- 用户原始输入（可能是 URL / 关键词 / 图片）
  status        VARCHAR(32) NOT NULL DEFAULT 'pending',
  verdict       VARCHAR(32),               -- recommend / avoid / caution
  -- 核心 AI 输出（JSONB 分节存）
  demand_analysis    JSONB,                -- { is_real_demand, trend_90d, peak_risk, ... }
  profit_model       JSONB,                -- { cost_breakdown, target_price, margin, ... }
  supplier_matches   JSONB,                -- [{ 1688_url, image, price_cny, moq, ... }]
  risk_assessment    JSONB,                -- { compliance, ip, platform_risk, ... }
  agent_reasoning    TEXT,                 -- LLM 推理全文（用于调试）
  llm_cost_usd       NUMERIC(8,4),         -- 本次生成消耗
  apify_cost_usd     NUMERIC(8,4),
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at  TIMESTAMPTZ,
  deleted_at    TIMESTAMPTZ
);
CREATE INDEX idx_dossiers_user ON dossiers(user_id);
CREATE INDEX idx_dossiers_status ON dossiers(status);
CREATE INDEX idx_dossiers_verdict ON dossiers(verdict);

-- 风口扫描（批量选品建议）
CREATE TABLE scans (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  category_filters JSONB,                  -- { categories: [...], budget: ..., ... }
  status        VARCHAR(32) NOT NULL DEFAULT 'pending',
  recommendations   JSONB,                 -- [{ product_id, rank, score, ... }]
  total_cost_usd    NUMERIC(8,4),
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at  TIMESTAMPTZ
);
CREATE INDEX idx_scans_user ON scans(user_id);

-- AI 对话会话
CREATE TABLE conversations (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title         VARCHAR(255),
  -- 关联档案（对话可能围绕一个档案展开）
  dossier_id    UUID REFERENCES dossiers(id),
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_conversations_user ON conversations(user_id);

CREATE TABLE messages (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
  role          VARCHAR(16) NOT NULL,      -- user / assistant / tool
  content       TEXT NOT NULL,
  tool_calls    JSONB,                     -- Agent 调用的工具记录
  tokens_in     INT,
  tokens_out    INT,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_messages_conversation ON messages(conversation_id, created_at);

-- 订阅 / 支付
CREATE TABLE subscriptions (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  plan          VARCHAR(32) NOT NULL,      -- pro_monthly / pro_yearly / team
  status        VARCHAR(32) NOT NULL,      -- active / past_due / canceled
  provider      VARCHAR(32),               -- wechat / alipay / stripe
  provider_sub_id VARCHAR(128),
  amount_cny    NUMERIC(10,2),
  current_period_start TIMESTAMPTZ,
  current_period_end   TIMESTAMPTZ,
  canceled_at   TIMESTAMPTZ,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);

-- 使用配额（按月重置）
CREATE TABLE usage_quotas (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  period_start  DATE NOT NULL,             -- 月初
  dossiers_used INT NOT NULL DEFAULT 0,
  scans_used    INT NOT NULL DEFAULT 0,
  ai_messages_used INT NOT NULL DEFAULT 0,
  UNIQUE (user_id, period_start)
);

-- 任务队列（Apify 抓取、档案生成等异步任务）
CREATE TABLE jobs (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  type          VARCHAR(64) NOT NULL,      -- generate_dossier / run_scan / sync_shop
  payload       JSONB NOT NULL,
  status        VARCHAR(32) NOT NULL DEFAULT 'queued',  -- queued / running / completed / failed
  attempts      INT NOT NULL DEFAULT 0,
  max_attempts  INT NOT NULL DEFAULT 3,
  error         TEXT,
  scheduled_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  started_at    TIMESTAMPTZ,
  completed_at  TIMESTAMPTZ
);
CREATE INDEX idx_jobs_status_scheduled ON jobs(status, scheduled_at);
CREATE INDEX idx_jobs_type ON jobs(type);
```

---

### 2.2 Schema 设计亮点说明

**为什么用 JSONB 而不是拆表？**
档案的 4 大板块（需求 / 利润 / 货源 / 风险）字段多、结构会频繁调整。JSONB 让 schema 随产品演进不用每次 migration。查询性能够用（PG GIN 索引）。**等 beta 完后字段稳定了再决定是否拆表**。

**为什么 `products` 表单独存 `snapshot` 不分表？**
同一个商品的多次抓取快照暂时不需要。如果后面做「商品历史趋势图」，再加 `product_snapshots` 时序表。

**为什么 `jobs` 表用 Postgres 而不是 Redis？**
Redis 要额外部署 + 额外 $5-10/月。Postgres-based queue 在 < 1000 并发任务场景下性能完全够。用 `arq` + `pgmq` 扩展或直接 `SELECT ... FOR UPDATE SKIP LOCKED`。

---

## 3. API Endpoints

所有 API 前缀 `/api/v1`，返回 JSON。错误码遵循 HTTP 语义。

### 3.1 认证（`/auth`）

```
POST   /auth/signup          · 邮箱注册（发验证邮件）
POST   /auth/login           · 邮箱 + 密码登录，返回 JWT
POST   /auth/logout          · 吊销 token
POST   /auth/waitlist        · 加入 waitlist（公开，无需登录）
POST   /auth/password-reset  · 请求重置密码
```

### 3.2 用户（`/users`）

```
GET    /users/me             · 当前用户信息 + 配额
PATCH  /users/me             · 改头像 / 显示名
DELETE /users/me             · 软删账号
GET    /users/me/usage       · 本月用量详情
```

### 3.3 店铺（`/shops`）

```
POST   /shops                · 绑定新店铺（触发 Apify 抓取）
GET    /shops                · 我的店铺列表
GET    /shops/{id}           · 单店铺详情
DELETE /shops/{id}
POST   /shops/{id}/resync    · 手动刷新
```

### 3.4 档案（`/dossiers`）—— 核心功能

```
POST   /dossiers             · 创建档案（异步，立即返回 job_id）
       body: { query: "手持风扇 / URL / 图片 URL", shop_id?: UUID }
GET    /dossiers             · 我的档案列表（分页）
GET    /dossiers/{id}        · 档案详情（完整 JSON）
GET    /dossiers/{id}/pdf    · 导出 PDF（Pro）
DELETE /dossiers/{id}        · 软删
POST   /dossiers/{id}/share  · 生成分享链接（只读）
```

### 3.5 扫描（`/scans`）

```
POST   /scans                · 启动风口扫描（异步）
       body: { categories: [...], budget_range, risk_tolerance }
GET    /scans/{id}           · 扫描结果（含 N 条推荐）
```

### 3.6 AI 对话（`/agent`）

```
POST   /agent/conversations          · 新建会话
GET    /agent/conversations          · 会话列表
GET    /agent/conversations/{id}     · 会话 + 全部 messages
POST   /agent/conversations/{id}/messages   · 发一条消息（SSE 流式返回）
```

### 3.7 Webhooks（`/webhooks`）—— 外部回调

```
POST   /webhooks/apify              · Apify run 完成回调
POST   /webhooks/wechatpay          · 微信支付回调
POST   /webhooks/alipay             · 支付宝回调
```

### 3.8 管理后台（`/admin`）—— 内部使用

```
GET    /admin/metrics               · 关键指标（DAU、付费率、LLM 成本）
GET    /admin/users                 · 用户列表
POST   /admin/users/{id}/grant      · 手动授予订阅（如 beta 用户终身 Pro）
```

---

## 4. AI Agent 架构（LangGraph）

### 4.1 三个主 Agent

**Dossier Agent · 档案生成**

状态流：
```
[开始] → [解析输入 · query_parser]
      → [TikTok 数据抓取 · apify_tiktok_tool]
      → [需求分析 · demand_analyzer] ──┐
      → [1688 图搜 · apify_1688_tool]    │
      → [利润测算 · profit_calc_tool]    ├→ [综合判断 · verdict_maker]
      → [风险扫描 · risk_scanner]  ──────┘   → [输出 JSON] → [结束]
```

每步失败可重试（指数退避），失败 3 次整体 job 标记 failed。

**Scan Agent · 风口扫描**

```
[接收用户参数] → [TikTok 热榜抓取]
              → [规则过滤（类目 / 预算 / 风险偏好）]
              → [LLM 排序 + 打分]
              → [输出 Top N 推荐] → [结束]
```

**Chat Agent · 通用对话**

```
[收到 user message] → [判断意图 · intent_router]
                   ├─ 闲聊 / FAQ → 直接回
                   ├─ 要查档案 → 调 db_query tool
                   ├─ 要新档案 → 触发 Dossier Agent（后台任务）
                   └─ 问风险 / 数据 → 调 apify_tool
              → [流式返回给前端]
```

### 4.2 Agent 工具清单

| 工具 | 功能 | 平均耗时 | 成本估算 |
|------|------|---------|---------|
| `apify_tiktok` | 抓 TikTok Shop 商品 / 类目数据 | 15-40 秒 | $0.05-0.15 / 次 |
| `apify_1688_image` | 以图搜图找 1688 同款 | 8-20 秒 | $0.03-0.08 / 次 |
| `db_query` | 查自家 DB（历史档案 / 用户数据） | < 100 ms | 免费 |
| `profit_calc` | 本地计算利润模型（Python） | < 50 ms | 免费 |
| `risk_score` | 规则 + LLM 混合风险打分 | 2-5 秒 | $0.001 |

### 4.3 单次档案生成成本模型

```
Apify TikTok 抓取         ≈ $0.08
Apify 1688 图搜          ≈ $0.05
DeepSeek LLM 推理（~8k tokens in / 2k out） ≈ $0.004
───────────────────────────────────
合计                     ≈ $0.134 / 档案
```

Pro 用户档案配额 = 30 份/月 = **成本上限 $4.02/月/用户** · 收入 ¥99 ≈ $13.6 · **毛利 ~70%**

重度用户（月跑 50+）毛利会下滑到 50%，但属于少数。

---

## 5. 数据流图

### 5.1 用户创建档案的完整链路

```
前端 Chat UI
  ↓ POST /dossiers { query: "手持风扇" }
FastAPI Router
  ↓ dispatch_job("generate_dossier", {dossier_id, user_id, query})
Jobs Table (pending)
  ↓
Worker Process · 轮询 jobs 表
  ↓
LangGraph Dossier Agent
  ├─ 调 apify_tiktok_tool
  │    ↓ Apify API
  │    ← 商品数据 JSON
  ├─ 调 apify_1688_image
  ├─ 调 profit_calc
  ├─ 调 risk_scanner
  └─ DeepSeek LLM 综合推理
      ↓
  写 dossiers 表 (status=completed)
  ↓
  发 SSE 事件给前端（如果用户还在线）
  ↓
前端 polling 或 SSE 接收 → 显示档案
```

### 5.2 AI 对话（同步流式）

```
前端 POST /agent/conversations/{id}/messages
  ↓
FastAPI 立即创建 message 行（role=user）
  ↓
返回 SSE stream:
  ├─ LangGraph Chat Agent 判断意图
  ├─ 调工具时 yield: { type: "tool_call", name: "apify_tiktok" }
  ├─ LLM 流式输出 yield: { type: "delta", text: "根据数据..." }
  ├─ 完成 yield: { type: "done", message_id, tokens }
  └─ 写 message 行（role=assistant）
```

---

## 6. 外部依赖清单

| 服务 | 用途 | 免费层 | 付费起 | 备注 |
|------|------|-------|--------|------|
| **Neon** | Postgres | 3GB | $19/月 | Serverless，冷启动 ~500ms 可接受 |
| **Railway** | 后端部署 | $5 额度 | $5/月起 | 或换 Fly.io |
| **Vercel** | 前端 | 免费 | — | 已用 |
| **Cloudflare R2** | 图片 / PDF 存储 | 10GB | — | S3 兼容、无出站费 |
| **Apify** | 数据抓取 | $5 额度 | 按量 | 核心成本项 |
| **DeepSeek** | LLM | — | $0.14/1M tokens | 极便宜 |
| **Resend** | 邮件发送 | 3k/月 | $20/月 | |
| **Sentry** | 错误监控 | 5k events | $26/月 | |
| **Logtail** | 日志聚合 | 1GB | $10/月 | |
| **Plausible** | 分析 | — | $9/月 | |
| **Tally.so** | Waitlist 表单 | 免费 | — | |

**预估月成本（100 beta 用户活跃）**：
- 固定：Neon($19) + Railway($5) + Resend($20) + Plausible($9) = **$53**
- 变动：Apify($15-25) + DeepSeek($2-5) = **$17-30**
- **合计：$70-83/月**

---

## 7. 部署拓扑

```
用户浏览器
  ↓
Cloudflare DNS (trendradar.app)
  ├→ Vercel CDN · Next.js 静态页 + React UI
  │    ↓ API calls
  └→ api.trendradar.app (Railway)
       ↓
       FastAPI 容器（2 副本，水平扩展）
          ├→ Neon Postgres（us-east-1）
          ├→ Cloudflare R2（对象存储）
          ├→ Apify API（抓取）
          ├→ DeepSeek API（LLM）
          └→ Resend API（邮件）

       Worker 容器（1 副本）
          └→ 同上
```

**环境分层**：
- `production`：主分支自动部署
- `preview`：每个 PR 自动创建 Vercel + Railway preview
- `local`：docker-compose（PG + MinIO 本地模拟 R2）

---

## 8. 安全 / 合规清单

- **密码**：bcrypt hash，cost factor 12
- **JWT**：HS256，access token 15min，refresh token 7 days
- **API rate limit**：`slowapi` 限流，未登录 60/分钟，登录用户 600/分钟
- **CORS**：只允许 `trendradar.app` + Vercel preview 域名
- **SQL 注入**：SQLAlchemy ORM + Pydantic 校验，禁止拼字符串 SQL
- **XSS**：前端 React 默认转义 + 档案导出 PDF 时 sanitize
- **数据隔离**：所有查询必须按 `user_id` 过滤（dep 注入 + 测试覆盖）
- **日志脱敏**：email / phone / jwt 不进日志
- **备份**：Neon 自动每日快照 + 周度导出到 R2

---

## 9. 可观测性

**三根日志**：

1. **Application Logs** → Logtail
   - 每个 request 一条结构化日志（user_id、latency、status）
   - LangGraph 每步执行记录 agent_step 日志

2. **Error Tracking** → Sentry
   - 所有 5xx 和 Agent 失败自动上报
   - 按 release 分组

3. **Business Metrics** → 自建 `/admin/metrics` + Plausible
   - DAU / WAU / MAU
   - 档案生成量 + 成功率
   - 单档案平均成本 vs 定价（毛利监控）
   - 订阅转化漏斗

**关键 SLO**：
- API p95 延迟 < 500ms
- 档案生成 p95 < 90 秒
- 月可用性 > 99.5%

---

## 10. 开发路线图（6 周）

### Week 1 · 骨架 + 认证

- [ ] 初始化 `apps/api` 项目（pyproject + FastAPI hello world）
- [ ] 配好 Neon 连接 + Alembic migration
- [ ] 实现 `users` + `waitlist` 两张表 + 4 个 auth endpoint
- [ ] Railway 部署跑起来（api.trendradar.app）
- [ ] 前端加登录 UI + 调 API
- **交付**：能注册登录，`/users/me` 能返回信息

### Week 2 · 店铺 + 商品 + Apify 接入

- [ ] `shops` + `products` 表 + migration
- [ ] Apify client 封装（带错误重试）
- [ ] `POST /shops` 触发 Apify 抓取（同步跑通）
- [ ] 引入 jobs 表 + 简单 worker（轮询版）
- **交付**：能绑定店铺、后台能看到抓到的商品

### Week 3 · 利润测算 + 风险评分（纯 Python）

- [ ] `services/profit_calc.py` + 单测
- [ ] `services/risk_scoring.py` + 单测
- [ ] 写固定 fixture 数据跑测试，不依赖 Apify
- **交付**：给一份商品 JSON，能算出完整利润模型 + 风险分

### Week 4 · LangGraph Dossier Agent

- [ ] 引入 LangGraph + DeepSeek client
- [ ] 实现 `dossier_agent.py`（全流程）
- [ ] 实现 4 个 tool（apify_tiktok、apify_1688、profit_calc、risk_score）
- [ ] `POST /dossiers` 端到端跑通
- **交付**：命令行测试：输入「手持风扇」→ 输出完整档案 JSON

### Week 5 · Chat Agent + SSE 流式

- [ ] `chat_agent.py` + 意图路由
- [ ] `conversations` + `messages` 表
- [ ] SSE endpoint `/agent/conversations/{id}/messages`
- [ ] 前端 Chat UI 接真 API（去掉 mock）
- **交付**：能在 Chat UI 里问问题，AI 能调工具回答

### Week 6 · 配额 + 订阅 + 打磨

- [ ] `usage_quotas` + `subscriptions` 表
- [ ] Free / Pro / Team 配额 middleware
- [ ] 微信 / 支付宝接入（或先用 Stripe 过渡）
- [ ] E2E 测试 + 监控 + 文档
- **交付**：MVP 可对外邀请 beta 用户使用

---

## 11. 重大不确定性 / 待验证项

| 风险 | 影响 | 缓解策略 |
|------|------|---------|
| Apify TikTok Scraper 准确性 / 时效性 | 整个产品数据源 | Week 2 先测 10 个真实品类，对比 Kalodata 数据 |
| DeepSeek 推理质量（对中文 + 电商领域） | 产品核心价值 | Week 4 准备 20 个人工标注 case，对比 GPT-4o-mini |
| 1688 图搜 API 可用性 / 稳定性 | 货源功能 | 先找 2 个备选 Actor，主备切换 |
| 微信 / 支付宝接入复杂度 | 上线时间 | 先用 Stripe（个人开发者友好），国内支付延后 |
| Neon 冷启动对用户体验影响 | API 首次响应慢 | 考虑升级到付费层（常驻）或用 Fly.io PG |

---

## 12. Review 问题清单（给你的）

看完这份架构文档，请重点确认：

1. **目录结构** — `apps/api/src/trendradar/` 的组织方式 OK 吗？
2. **DB schema** — 有没有字段缺漏 / 不需要的表？
3. **JSONB vs 拆表** — 档案用 JSONB 存 4 大板块的决策接受吗？
4. **LangGraph 工作流** — Agent 的状态流设计合理吗？
5. **开发顺序** — 6 周分 Week 是否太激进 / 太保守？
6. **支付方案** — 先上 Stripe 过渡，还是一开始就做微信支付？
7. **冷启动问题** — Neon serverless 500ms 延迟能接受吗？
8. **Monorepo 结构** — `apps/web` + `apps/api` 放一起 OK 吗？需要 Turborepo / pnpm workspace 吗？

---

**下一步**：你 review 后回复哪些地方要改，我再改架构文档 → 确认后直接进 Week 1 编码。
