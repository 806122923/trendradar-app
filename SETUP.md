# TrendRadar App · 本地启动指南

这是 MVP 的 monorepo 启动包。读完这份文档你能跑出一个**能用自然语言问选品的本地版本**。预计**首次配置 30–45 分钟**。

## 这个包里有什么

```
trendradar-app/
├── docker-compose.yml      本地 Postgres + Redis
├── .env.example            环境变量模板
├── .gitignore
├── SETUP.md                ← 你正在看的
├── apps/
│   ├── api/                FastAPI 后端（代码完整）
│   │   ├── pyproject.toml
│   │   ├── alembic.ini
│   │   ├── alembic/
│   │   │   ├── env.py
│   │   │   ├── script.py.mako
│   │   │   └── versions/001_initial.py   初始数据库 schema
│   │   └── app/
│   │       ├── main.py          FastAPI 入口
│   │       ├── core/
│   │       │   ├── config.py    环境变量读取
│   │       │   ├── db.py        异步 SQLAlchemy
│   │       │   └── llm_router.py  Claude + DeepSeek 双路由
│   │       ├── models/          ORM 模型（users / products / chat）
│   │       ├── prompts/
│   │       │   └── picker.py    选品 prompt 模板
│   │       ├── schemas/         Pydantic 请求/响应
│   │       └── api/v1/
│   │           ├── health.py    /api/v1/health
│   │           └── chat.py      /api/v1/chat/query  (SSE 流式)
│   └── web/                Next.js 前端
│       ├── README.md            创建 Next.js 项目的命令
│       └── _custom_files/       创建后要复制进去的定制文件
│           └── src/
│               ├── lib/api.ts          API 客户端 + SSE reader
│               └── app/chat/page.tsx   最简聊天页
```

---

## 一次性环境准备

你需要装 4 个东西。Windows 10/11 为例：

### 1. Git（如果还没有）

<https://git-scm.com/download/win> — 一路下一步。

### 2. Node.js 20 LTS（给前端）

<https://nodejs.org> → LTS 版本 → 下一步安装。装完打开 PowerShell 验证：

```powershell
node --version     # 应该显示 v20.x
npm --version
```

### 3. Python 3.11+（给后端）

<https://www.python.org/downloads/windows/> → 下载 Python 3.12.x → 安装时**务必勾选 "Add Python to PATH"**。验证：

```powershell
python --version   # 应该显示 Python 3.11 或更高
```

### 4. Docker Desktop（给本地 Postgres + Redis）

<https://www.docker.com/products/docker-desktop/> → 下载 → 安装后重启电脑。安装后打开 Docker Desktop，等到左下角显示"Engine running"。验证：

```powershell
docker --version
docker compose version
```

> 如果你不想装 Docker，也可以用云数据库（Supabase + Upstash）替代。跳到文末的"无 Docker 方案"。

---

## 首次启动流程

### Step 0 · 把文件夹复制到你电脑上

把整个 `trendradar-app/` 文件夹放到一个没有中文路径的位置，比如：

```
C:\Users\Mqx95\Documents\Claude\Projects\trendradar-app
```

打开 PowerShell，`cd` 进去。

```powershell
cd C:\Users\Mqx95\Documents\Claude\Projects\trendradar-app
```

### Step 1 · 准备 `.env` 文件

```powershell
# 把模板复制成实际用的 .env 文件
Copy-Item .env.example .env
```

打开 `.env` 编辑（用 VS Code / 记事本都行），**至少填一项**：

```
DEEPSEEK_API_KEY=sk-...  ← 这一行填上你的 DeepSeek key
```

去 <https://platform.deepseek.com> 注册，免费送 1 块钱的 token 额度，够你测几百次。Claude key 可选，暂时可以不填。

其他项（`DATABASE_URL`、`REDIS_URL`）暂时保持默认就行。

### Step 2 · 启动本地数据库（Docker）

```powershell
docker compose up -d
```

第一次会下载镜像，需要几分钟。完成后验证容器跑起来了：

```powershell
docker compose ps
```

应该看到 `trendradar-postgres` 和 `trendradar-redis` 两个 `running` 的容器。

### Step 3 · 启动后端（FastAPI）

**3a. 新开一个 PowerShell 窗口**，进到项目根目录：

```powershell
cd C:\Users\Mqx95\Documents\Claude\Projects\trendradar-app\apps\api
```

**3b. 创建 Python 虚拟环境 + 安装依赖**：

```powershell
# 一次性：创建 venv
python -m venv .venv

# 激活（每次新开终端都要激活一次）
.\.venv\Scripts\Activate.ps1

# 如果报错 "running scripts is disabled"，执行一次（只需要一次）：
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 装依赖
pip install --upgrade pip
pip install -e .
```

这一步装依赖可能要 2–3 分钟。

**3c. 初始化数据库（跑 Alembic 迁移）**：

```powershell
alembic upgrade head
```

成功后会看到 `INFO Running upgrade -> 001, Initial schema`。Postgres 里就有了 `users`、`products`、`chat_sessions`、`chat_messages` 四张表。

**3d. 跑 smoke 测试，一次确认所有层都通**（强烈建议）：

```powershell
python scripts/smoke_test.py
```

正常输出应该是 4 个 ✓：

```
[1/4] ✓ Config loads
[2/4] ✓ Database connects (SELECT 1 returned 1)
[3/4] ✓ LLM Router responds  (model=deepseek-chat, got: 'ok')
[4/4] ✓ FastAPI app imports (12 routes registered)

🎉 All smoke tests passed. MVP backend is ready to go.
```

- 卡在 [1/4]：`.env` 没读到，检查文件路径和变量名
- 卡在 [2/4]：Postgres 没起来或 `DATABASE_URL` 错了
- 卡在 [3/4]：`DEEPSEEK_API_KEY` 错了或 key 被 revoke 了
- 卡在 [4/4]：代码层面的 bug，发错误给我

**3e. 启动 API 服务器**：

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

看到 `Uvicorn running on http://0.0.0.0:8000` 就成功了。

浏览器打开 <http://localhost:8000/docs> 可以看 Swagger 交互文档。试试 `GET /api/v1/health`，应该返回 `{"status": "ok", "env": "development"}`。

保持这个窗口开着。

### Step 4 · 启动前端（Next.js）

**4a. 再开一个新 PowerShell 窗口**：

```powershell
cd C:\Users\Mqx95\Documents\Claude\Projects\trendradar-app\apps\web
```

**4b. 首次创建 Next.js 项目**：

```powershell
npx create-next-app@latest .
```

一路回车用默认即可。当被问到时确认：

- TypeScript → **Yes**
- ESLint → **Yes**
- Tailwind CSS → **Yes**
- `src/` directory → **Yes**
- App Router → **Yes**
- Customize default import alias (`@/*`) → **No**

**4c. 安装 shadcn/ui**：

```powershell
npx shadcn@latest init
```

选 Default / Slate / yes CSS variables。

```powershell
npx shadcn@latest add button input textarea card badge
```

**4d. 把定制文件复制到 src/ 下**：

```powershell
# 从 _custom_files 复制 lib/api.ts 和 app/chat/page.tsx
Copy-Item _custom_files\src\lib\api.ts src\lib\api.ts -Force
New-Item -ItemType Directory -Force -Path src\app\chat
Copy-Item _custom_files\src\app\chat\page.tsx src\app\chat\page.tsx -Force
```

**4e. 创建前端的 `.env.local`**：

```powershell
"NEXT_PUBLIC_API_BASE_URL=http://localhost:8000" | Out-File -Encoding UTF8 .env.local
```

**4f. 启动前端开发服务器**：

```powershell
npm run dev
```

看到 `Ready in xs - Local: http://localhost:3000` 就成功了。

### Step 5 · 跑通第一个查询

浏览器打开 <http://localhost:3000/chat>。输入一句：

> 给我 3 个美区 50 美金以内、家居类、最近 7 天增速最快的品

点"提交查询"。几秒后下方会**流式**出现 AI 返回的 JSON 推荐。

🎉 **首个 MVP 端到端跑通了。**

---

## 日常开发流程

每次开始开发，开 3 个 PowerShell 窗口：

```powershell
# 窗口 1：数据库（只需第一次 up -d，之后保持运行）
cd C:\...\trendradar-app
docker compose up -d
docker compose logs -f postgres   # 可选，看 DB 日志

# 窗口 2：后端
cd C:\...\trendradar-app\apps\api
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload

# 窗口 3：前端
cd C:\...\trendradar-app\apps\web
npm run dev
```

代码改动自动热重载。

---

## 后续开发提示

### 当你改了 ORM model 时

```powershell
cd apps\api
.\.venv\Scripts\Activate.ps1

# 自动生成迁移
alembic revision --autogenerate -m "add_something"

# 人工检查 alembic/versions/xxx_add_something.py 是否正确
# 应用
alembic upgrade head
```

### 加新的 API 端点

1. 在 `apps/api/app/api/v1/` 新建一个文件，比如 `products.py`
2. 写 `router = APIRouter(prefix="/products")`
3. 在 `app/api/v1/__init__.py` 注册：`api_router.include_router(products.router)`
4. 热重载会自动生效

### 调用 LLM

```python
from app.core.llm_router import LLMMessage, router as llm

messages = [
    LLMMessage(role="system", content="你是一位专业选品顾问"),
    LLMMessage(role="user", content="给我 3 个宠物类爆品"),
]
result = await llm.complete(messages, plan="free")  # 用 DeepSeek
# or
result = await llm.complete(messages, plan="pro")   # 用 Claude
```

流式：`async for chunk in llm.stream(messages, plan="free"): print(chunk, end="")`

### 切换模型

改 `.env`：

```
LLM_FREE_TIER_MODEL=deepseek-chat        # 免费用户用 DeepSeek
LLM_PRO_TIER_MODEL=claude-sonnet-4-5     # 付费用户用 Claude
```

重启后端生效。

---

## 无 Docker 方案（用云数据库）

如果你不想装 Docker：

1. 去 <https://supabase.com> 免费创建一个项目，拿到 `postgres://` 连接串
2. 去 <https://upstash.com> 免费创建一个 Redis 数据库，拿到 `rediss://` 连接串
3. 把这两个填到 `.env`：
   ```
   DATABASE_URL=postgresql+asyncpg://postgres:[PWD]@[HOST].supabase.co:5432/postgres
   REDIS_URL=rediss://default:[PWD]@[HOST].upstash.io:6379
   ```
4. 跳过 `docker compose up -d`，直接从 Step 3 继续

注意：Supabase 免费额度 500MB 数据库 + 7 天无活动暂停。早期够用。

---

## 常见错误速查

### `alembic upgrade head` 报 "connection refused"

Postgres 没起来。检查 `docker compose ps`，如果容器没在跑，`docker compose up -d`。

### `pip install -e .` 报 "psycopg2" 编译错误

我们用的是 `asyncpg` 不是 `psycopg2`。确认 `pyproject.toml` 里只有 `asyncpg`。如果你误装了 psycopg2，删掉重建虚拟环境。

### 前端 `/chat` 页面报 CORS 错误

检查 `apps/api/app/main.py` 的 `allow_origins` 里有没有 `http://localhost:3000`。有的话后端重启一下。

### DeepSeek 返回 "Invalid API Key"

检查 `.env` 里 `DEEPSEEK_API_KEY` 是否填对了。去 <https://platform.deepseek.com> 重新生成一个。

### PowerShell 报 "running scripts is disabled"

执行一次：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
再激活 venv 就不报错了。

---

## 什么时候打电话给我

- 卡在任何一步超过 30 分钟，直接发错误信息给我
- 想加功能但不知道从哪下手
- Week 3+ 开始，需要接入真实数据源（Apify / TikTok API）时

下一步推进建议：跑通 `/chat` 页面之后，**按 PRD 的 Week 3–4 开始接真实数据**——装 Apify TikTok Shop scraper，跑一次把 500 个真实产品灌进 `products` 表，然后把 `apps/api/app/api/v1/chat.py` 里的 `_candidates_for` 改成真正查表。那时候你就有能给真人用的 MVP 了。
