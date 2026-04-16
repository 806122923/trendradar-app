# TrendRadar Web

Next.js 14 App Router frontend for TrendRadar. Chat page streams LLM picks from
the FastAPI backend via SSE.

## Local dev

```bash
npm install
cp .env.example .env.local
# edit .env.local — set NEXT_PUBLIC_API_BASE_URL
npm run dev
```

Open http://localhost:3000 (auto-redirects to `/chat`).

## Production (Vercel)

1. Import the GitHub repo on Vercel.
2. **Root Directory**: `apps/web`
3. Environment Variables:
   - `NEXT_PUBLIC_API_BASE_URL` = your Railway backend URL
     (e.g. `https://trendradar-app-production.up.railway.app`)
4. Deploy.
5. On Railway, add the Vercel domain to `CORS_ORIGINS` (comma-separated).

## Routes

- `/` → redirects to `/chat`
- `/chat` — conversational product picker (SSE)
