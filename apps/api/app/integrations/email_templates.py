"""Transactional email templates.

Kept inline (not Jinja files) for two reasons:
  1. Only a handful of emails — the complexity isn't worth a template engine yet
  2. Everything ships in the Python package, no template path issues in Docker

When we add more templates (subscription receipt, password reset, etc.) we'll
split into individual modules.
"""
from __future__ import annotations


def _shared_styles() -> str:
    """Inline CSS — kept tight because Gmail / Outlook strip most things."""
    return """
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
               background: #FAFAFA; color: #111; margin: 0; padding: 0; }
        .wrap { max-width: 560px; margin: 40px auto; padding: 0 24px; }
        .card { background: #FFF; border: 1px solid #E5E5E5; padding: 32px; }
        h1 { font-size: 22px; margin: 0 0 16px; font-weight: 600; }
        p { line-height: 1.6; margin: 0 0 16px; font-size: 15px; color: #333; }
        .accent { color: #FF4F1A; font-weight: 600; }
        .pos { display: inline-block; padding: 6px 12px; border: 1px solid #111;
               font-family: 'Courier New', monospace; font-size: 13px; font-weight: 600; }
        .btn { display: inline-block; padding: 14px 28px; background: #111;
               color: #FFF !important; text-decoration: none; font-weight: 500;
               margin: 8px 0 20px; }
        .foot { font-size: 12px; color: #888; margin-top: 32px; text-align: center; }
        .foot a { color: #888; }
        hr { border: none; border-top: 1px solid #E5E5E5; margin: 24px 0; }
    """


def welcome_email(
    *,
    email: str,
    position: int,
    site_url: str,
    founders_cap: int = 100,
    unsubscribe_url: str | None = None,
) -> tuple[str, str, str]:
    """Email 1 · Waitlist welcome / confirmation.

    Returns (subject, html, plain_text).
    Mirrors the copy in .agents/email-sequences/waitlist.md Email 1.
    """
    is_founder = position <= founders_cap
    remaining = max(0, founders_cap - position)
    unsub = unsubscribe_url or f"{site_url}/unsubscribe?email={email}"

    badge = "前 100 名 · 终身 5 折锁定" if is_founder else f"候补名单 · 第 {position} 位"
    hero = (
        "<p>刚收到你的邮箱了。你是第 "
        f'<span class="pos">#{position}</span> 位加入 TrendRadar waitlist 的人。</p>'
    )

    if is_founder:
        perk_line = (
            f'<p>✓ <span class="accent">前 100 名终身 5 折</span> — '
            f"Pro 年卡 ¥899 → 你锁的是 <strong>¥449/年，永久</strong>"
            f"（当前还剩 {remaining} 个名额）</p>"
        )
    else:
        perk_line = (
            "<p>✓ 上线后你将享受 <strong>首月 ¥49</strong> 优惠（续费回到 ¥99）</p>"
        )

    subject = "你锁住了 ✓ TrendRadar 前 100 名终身 5 折" if is_founder \
        else "你在 TrendRadar waitlist 上了"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>{_shared_styles()}</style>
</head>
<body>
<div class="wrap">
  <div class="card">
    <h1>Hey，</h1>
    {hero}
    <p>我们正在做的事，一句话：</p>
    <p style="border-left: 3px solid #FF4F1A; padding-left: 14px; color: #111;">
      <strong>用 AI Agent 帮 TikTok Shop 美区新手卖家选品 — 不是给你一堆报表，是直接替你拍板。</strong>
    </p>
    <hr>
    <p><strong>{badge}</strong></p>
    {perk_line}
    <p>✓ 上线前 3 天收到专属邀请链接（不公开发售）</p>
    <p>✓ 每月一次产品进展速报（不是营销，是真进度）</p>
    <hr>
    <p>接下来 6 周你会收到 3-4 封邮件：</p>
    <p>
      · 为什么我们做这个<br>
      · TikTok Shop 选品 5 大坑（纯干货）<br>
      · 产品上线前的抢先体验链接
    </p>
    <p>先看点东西：</p>
    <p>
      <a class="btn" href="{site_url}/alternatives">对比 Kalodata / 嘀嗒狗 / EchoTik →</a>
    </p>
    <hr>
    <p>有问题直接回这封邮件，我们是真人在看。</p>
    <p>— TrendRadar Team</p>
  </div>
  <div class="foot">
    不想再收到？<a href="{unsub}">这里取消</a>。<br>
    TrendRadar · AI product-research agent for TikTok Shop US sellers
  </div>
</div>
</body>
</html>"""

    text = f"""Hey，

刚收到你的邮箱了。你是第 #{position} 位加入 TrendRadar waitlist 的人。

我们正在做的事：用 AI Agent 帮 TikTok Shop 美区新手卖家选品 — 不是给你一堆报表，是直接替你拍板。

你现在拥有的：
{'- 前 100 名终身 5 折 — Pro 年卡 ¥899 → 你锁的是 ¥449/年，永久' if is_founder else '- 上线后享受首月 ¥49 优惠'}
- 上线前 3 天收到专属邀请链接
- 每月一次产品进展速报

接下来 6 周你会收到 3-4 封邮件，涵盖为什么我们做这个 / TikTok Shop 选品 5 大坑 / 上线抢先链接。

先看点东西：{site_url}/alternatives

有问题直接回这封邮件。

— TrendRadar Team

---
不想再收到？{unsub}
"""
    return subject, html, text
