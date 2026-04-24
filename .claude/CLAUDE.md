# Claude Instructions for TrendRadar

## Quick Start
Read `.claude/PROJECT.md` first — it has the full architecture, design system, and gotchas.

## Rules
- **Design system**: Pure B/W + `#FF4F1A` acid accent. NO gradients, NO soft shadows, 2px corners, Space Grotesk + Inter + JetBrains Mono. See `apps/web/src/app/globals.css` for tokens and `tailwind.config.ts` for Tailwind mapping.
- **Git commits**: Author is `Hemu <806122923@qq.com>`. Use `-c user.name=Hemu -c 'user.email=806122923@qq.com'` in sandbox. User pushes from Windows.
- **Landing page**: `apps/web/public/landing.html` is the source of truth for brand/visual. Do NOT replace with React — it's intentionally static HTML.
- **Charts**: Use inline SVG. No chart libraries on the React side (Chart.js is only in the static landing.html).
- **Section numbering**: Chat page uses `00 · LABEL` → `01 · ...` → `04 · ...` mono-typed labels for scannability.
- **Chinese-first**: All user-facing copy in Chinese. Labels/tags in English UPPERCASE mono.
