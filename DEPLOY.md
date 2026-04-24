# TrendRadar 云端部署指南

把 MVP 从 `localhost` 搬到公网，总耗时约 60 分钟（第一次）。

**架构**

```
用户浏览器
    ↓ HTTPS
Vercel (Next.js 前端) ──fetch──→ Railway (FastAPI 后端) ──→ Neon (Postgres)
                                         │
                                         └──→ DeepSeek API
```

成本：第一个月 **$0**，第二个月后约 $5 / 月（Railway 额度用完后的下限）。

---

## Step 0 — 把代码推到 GitHub（10 分钟）

Vercel 和 Railway 都从 GitHub 拉代码自动部署，所以要先有一个仓库。

先在本地跑一遍和 CI 对齐的检查，确认当前提交是可部署状态：

```powershell
# API
cd C:\path\to\trendradar-app\apps\api
.\.venv\Scripts\python.exe -m ruff check app tests scripts
.\.venv\Scripts\python.exe -m pytest tests -q

# Web
cd C:\path\to\trendradar-app\apps\web
npm ci
npm audit --audit-level=high --omit=dev
npm run lint
npm run typecheck
npm run build
```

```powershell
# 在 trendradar-app 根目录
cd C:\path\to\trendradar-app

# 确认 .env 不会被提交（.gitignore 已配置，但二次确认）
git status                  # 不应该看到 .env

# 初始化（如果还没）
git init
git add .
git commit -m "feat: MVP 全栈落地"

# GitHub 上新建空仓库（名字比如 trendradar-app，私有即可），然后：
git remote add origin https://github.com/你的用户名/trendradar-app.git
git branch -M main
git push -u origin main
```

> ⚠️ 推之前打开 `.env` 看一眼，**里面的 DeepSeek key 不应该被 commit**。
> `git status` 里不出现 `.env` 就是安全的。

---

## Step 1 — Neon 数据库（5 分钟）

1. 打开 https://neon.tech → 用 GitHub 登录
2. 点 **Create project**：
   - Name: `trendradar`
   - Postgres version: 16
   - Region: **US East (Ohio)** — 后面 Railway 也选 US East，降延迟
3. 项目建好后，首页给你一个连接串，长这样：
   ```
   postgresql://neondb_owner:xxxxxxxx@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
4. **把它改成 asyncpg 格式**（我们代码用的是 asyncpg 驱动）：
   ```
   postgresql+asyncpg://neondb_owner:xxxxxxxx@ep-xxx.us-east-2.aws.neon.tech/neondb?ssl=require
   ```
   两处改动：`postgresql://` → `postgresql+asyncpg://`，`sslmode=require` → `ssl=require`
5. 把这串连接复制出来存好，马上要用

---

## Step 2 — Railway 后端（15 分钟）

1. 打开 https://railway.app → GitHub 登录 → **New Project** → **Deploy from GitHub repo**
2. 选刚推的 `trendradar-app` 仓库
3. Railway 自动扫描到根目录不是 Python 项目，点进服务 → **Settings**：
   - **Root Directory**: `apps/api`
   - **Watch Paths**: `apps/api/**`
   - （Dockerfile 已经在 `apps/api/Dockerfile`，Railway 会自动用它）
   - 如果忘了设置 Root Directory，仓库根目录的 `railway.json` + `Dockerfile.railway` 也会兜底，强制 Railway 从根目录构建 API 镜像；但推荐设置 Root Directory，构建上下文更小。
   - **Healthcheck Path**: `/api/v1/health`（`/api/v1/health/ready` 会检查数据库，适合人工排查，不适合做首启健康检查）
4. **Variables** 选项卡，添加以下环境变量：
   ```
   DATABASE_URL=postgresql+asyncpg://...（Step 1 改好的那串）
   DEEPSEEK_API_KEY=sk-你的 key
   APP_ENV=production
   SECRET_KEY=随便一串长字符串，比如 openssl rand -hex 32 生成
   CORS_ORIGINS=（先留空，Vercel 部完再回来填）
   ```
5. **Networking** → **Generate Domain**，得到类似 `trendradar-api-production.up.railway.app`
6. 等待 **Deployments** 页显示绿色 ✅（首次构建 3-5 分钟）
7. 浏览器打开 `https://你的 Railway 域名/` 看到：
   ```json
   {"service":"trendradar-api","version":"0.1.0","docs":"/docs"}
   ```
   表示后端活着，并且数据库迁移成功（Dockerfile 里会自动跑 `alembic upgrade head`）

---

## Step 3 — 把 70 条种子数据塞进 Neon（3 分钟）

Railway 只跑了建表，数据还是空的。本地 shell 跑一次种子，数据就进 Neon 了：

```powershell
cd C:\path\to\trendradar-app\apps\api
.\.venv\Scripts\Activate.ps1

# 临时用 Neon 的连接串跑，不改本地 .env
$env:DATABASE_URL = "postgresql+asyncpg://neondb_owner:xxx@ep-xxx.neon.tech/neondb?ssl=require"
python scripts/seed_products.py

# 成功会看到：
# Inserted/updated 70 products. Done.
```

跑完用浏览器访问 `https://你的 Railway 域名/docs` → 找 `/api/v1/chat/query` → **Try it out**，
body 填 `{"query":"给我 3 个美区家居爆品"}`，点 Execute，应该能看到 SSE 流返回。

---

## Step 4 — Vercel 前端（10 分钟）

1. https://vercel.com → **Add New** → **Project** → 选同一个 `trendradar-app` 仓库
2. **Configure Project**：
   - **Framework Preset**: Next.js（应该自动识别）
   - **Root Directory**: `apps/web` ← 重要！
   - **Install Command**: `npm ci`
   - **Build Command**: `npm run build` ← 重要：会先复制静态落地页所需字体和 Chart.js
   - **Output Directory**: 留默认
3. **Environment Variables**：
   ```
   NEXT_PUBLIC_API_BASE_URL=https://你的 Railway 域名（不带尾斜杠）
   NEXT_PUBLIC_APP_URL=https://你的 Vercel 域名
   ```
4. 点 **Deploy**，等 1-2 分钟
5. 拿到类似 `trendradar-app-xyz.vercel.app` 的域名

---

## Step 5 — 把 Vercel 域名告诉后端（3 分钟）

前端拿到域名后，回到 Railway → Variables，更新：

```
CORS_ORIGINS=https://trendradar-app-xyz.vercel.app
```

Railway 会自动重启。

浏览器打开 `https://trendradar-app-xyz.vercel.app/chat`，
问一句"给我 3 个美区家居爆品"，
看到流式出结果 = 端到端活了 ✅

---

## 排错指南

**Railway 构建失败**：去 **Deployments** 点失败那次看 log。90% 是 pyproject.toml 或 Dockerfile 语法问题。

**Railway 启动后 5xx**：点 **View Logs**。最常见：
- `DATABASE_URL` 没改成 `asyncpg`
- Neon 连接串忘了 `?ssl=require`
- `alembic upgrade head` 报错 → 本地先跑一次确认迁移本身 OK

**Vercel 部署成功但 /chat 页面报 CORS 错**：
- 打开浏览器 Console 看具体 origin
- 回 Railway Variables 确认 `CORS_ORIGINS` 里写的是**完整 URL**（带 `https://`、不带尾斜杠）
- 重启 Railway 服务

**SSE 流只出 `start` 然后卡住**：
- 99% 是 DeepSeek key 在 Railway 没配
- 去 Railway Variables 确认 `DEEPSEEK_API_KEY`

**Neon 免费额度**：3GB 存储 + 191.9 小时 compute/月。当前数据量 <1MB，够跑小半年。

---

## 下一步

- 买个域名（Namecheap ~$10/年），在 Vercel Domains 里绑定
- 把 CORS_ORIGINS 更新为你的正式域名
- 把落地页 `trendradar-three.vercel.app` 的"立即试用"按钮改成指向 `/chat`
