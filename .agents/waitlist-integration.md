# Waitlist 集成指南

产品上线前用来**收邮箱**的完整链路。6 个步骤配完，整条路走通。

---

## 端到端链路

```
landing.html 底部表单（Tally.so 嵌入）
       ↓ 用户提交邮箱
Tally webhook
       ↓ POST /api/v1/waitlist/tally  （带 Tally-Signature 头）
FastAPI handler
  ├→ HMAC 校验签名
  ├→ 写 waitlist 表（自动计算 position）
  └→ 调 Resend 发 Email 1 欢迎邮件
       ↓
用户收到带「前 100 名终身 5 折」的欢迎邮件
```

---

## 已经落地的代码

| 文件 | 作用 |
|------|------|
| `apps/api/alembic/versions/002_add_waitlist.py` | 建 `waitlist` 表 |
| `apps/api/app/models/waitlist.py` | WaitlistEntry ORM |
| `apps/api/app/schemas/waitlist.py` | Pydantic I/O |
| `apps/api/app/api/v1/waitlist.py` | 3 个 endpoint |
| `apps/api/app/integrations/resend_client.py` | Resend API 封装 |
| `apps/api/app/integrations/email_templates.py` | Email 1 模板（founder/non-founder 分支） |
| `apps/api/tests/test_waitlist.py` | 单元测试 |

---

## 3 个 API Endpoint

### `POST /api/v1/waitlist`

landing 页 JS 直接调用（不走 Tally 也能用）。

```bash
curl -X POST https://api.trendradar.app/api/v1/waitlist \
  -H "Content-Type: application/json" \
  -d '{"email":"seller@example.com","source":"landing_hero"}'
```

响应：

```json
{
  "id": "uuid...",
  "email": "seller@example.com",
  "position": 247,
  "created_at": "2026-04-22T...",
  "already_registered": false
}
```

### `GET /api/v1/waitlist/stats`

给 landing 页用 — 显示「已有 N 人加入 · 剩 X 个终身 5 折名额」。

```json
{ "total": 247, "remaining_founders_seats": 0 }
```

### `POST /api/v1/waitlist/tally`

Tally.so 的 webhook 目标。带 `Tally-Signature` 头，HMAC-SHA256 校验。

---

## 部署配置（需要在 Railway 设置的 env vars）

```env
# Resend
SEND_EMAILS=true                                    # 默认 false → 只 log 不真发
RESEND_API_KEY=re_xxx
RESEND_FROM_EMAIL=TrendRadar Team <hi@trendradar.app>
RESEND_REPLY_TO=hi@trendradar.app

# Tally signing
TALLY_SIGNING_SECRET=xxx                            # Tally → Form → Webhooks 里生成

# Site
SITE_URL=https://trendradar.app                     # 邮件里的链接域名
FOUNDERS_SEAT_CAP=100                               # 前 N 名享终身 5 折
```

---

## Tally 侧配置步骤

1. **注册 Tally.so**（免费）
2. **新建表单** — 一个字段：「你的邮箱」（INPUT_EMAIL 类型）
3. **表单 → Integrations → Webhooks**：
   - URL：`https://api.trendradar.app/api/v1/waitlist/tally`
   - Secret：生成一个，同步填到 Railway 的 `TALLY_SIGNING_SECRET`
4. **Publish** — 拿到 embed 代码
5. **粘到 `apps/web/public/landing.html`** 的 WAITLIST section 底部

---

## Resend 侧配置步骤

1. **注册 Resend.com**（免费 3k/月）
2. **Domains → Add Domain** → 填 `trendradar.app`
3. Resend 给 4 条 DNS 记录（SPF / DKIM × 2 / DMARC），到域名 DNS 面板加
4. **等验证通过**（10-30 分钟）
5. **API Keys → Create** → 复制到 Railway 的 `RESEND_API_KEY`

⚠️ 新域名**前 7 天日发送量不要超过 1000 封**，避免被识别为垃圾邮件源（预热期）。

---

## 本地开发测试

### 1. 跑迁移建表

```bash
cd apps/api
alembic upgrade head
```

### 2. 启动 API（不发真邮件）

```bash
# .env 里保持 SEND_EMAILS=false (默认)
uvicorn app.main:app --reload
```

### 3. 手动触发 waitlist

```bash
curl -X POST http://localhost:8000/api/v1/waitlist \
  -H "Content-Type: application/json" \
  -d '{"email":"me@test.com","source":"manual_test"}'
```

API log 应该会看到类似：

```
📧 [dry-run] Skipping send (SEND_EMAILS=False, key_set=False) → to=me@test.com subject='你锁住了 ✓ TrendRadar 前 100 名终身 5 折'
✅ Waitlist join email=me@test.com position=1
```

### 4. 跑测试

```bash
cd apps/api
pip install -e '.[dev]'
pytest tests/test_waitlist.py -v
```

---

## 上生产前的核查清单

**技术**
- [ ] Railway 设好 5 个 env vars（RESEND_* + TALLY_* + SITE_URL）
- [ ] 域名 DNS 加了 SPF/DKIM/DMARC 记录
- [ ] Resend domain 验证通过（绿色 ✓）
- [ ] `SEND_EMAILS=true` 在 Railway 上设定
- [ ] Tally webhook 指向生产 URL 而不是 localhost

**业务**
- [ ] 给自己的邮箱发一次真实邮件验收视觉
- [ ] 验证 Gmail / QQ / 163 / Outlook 四个客户端显示正常
- [ ] 已读取消订阅链接能工作（TODO：`/unsubscribe` endpoint 暂未实现）
- [ ] Landing 页的 Tally 表单埋点到了 Plausible

---

## 还没实现的相关功能（未来工作）

- **Email 2-5** · 目前只有 Email 1。2-5 封需要任务队列 + cron 触发（Phase 2 Week 6 做）
- **Unsubscribe** · `/unsubscribe?email=` 端点 + 从 waitlist 表打「已退订」标记
- **Waitlist → User 迁移** · 上线当天把 waitlist 邮箱转成正式 user 账号 + 发专属邀请链接
- **Admin 视图** · `/admin/waitlist` 看总数、按 source 分布、转化率
- **双重确认邮件（Double opt-in）** · GDPR 合规需要时再加
