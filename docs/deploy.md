# Deployment — Vercel (frontend) + Railway (backend)

The agent backend is long-running (each `/analyze` takes 30–60s) and needs a persistent process +
DB + API keys, so it **cannot** run on Vercel's serverless functions. The working split:

```
Browser ──► Vercel (Next.js UI) ──HTTPS──► Railway (FastAPI agent) ──► Supabase (adjudicator schema)
                                                          └──► Anthropic + OpenAI
```

> **Prototype, not a product. No auth is configured** — anyone who finds the backend URL can trigger
> agent runs that bill your Anthropic/OpenAI keys. Don't share the URL widely, or add a gate later
> (`docs/deploy.md` → "Adding auth").

---

## 1. Backend → Railway

Prereqs: a Railway account, this repo on GitHub (see §3).

1. **New Project → Deploy from GitHub repo** → pick this repo.
2. **Service → Settings → Root Directory:** `backend`
   (so Railway builds only the backend; it auto-detects `requirements.txt` + `Procfile` + `.python-version`).
3. **Variables** (Settings → Variables) — paste from your local `backend/.env`:
   ```
   SUPABASE_URL=...
   SUPABASE_SERVICE_KEY=...
   DATABASE_URL=postgresql://...pooler.supabase.com:5432/postgres
   DB_SCHEMA=adjudicator
   ANTHROPIC_API_KEY=...
   OPENAI_API_KEY=...
   CORS_ORIGINS=https://<your-vercel-app>.vercel.app
   ```
   (You can set `CORS_ORIGINS=*` first and tighten it once the Vercel URL exists.)
4. Railway builds and gives a public URL like `https://adjudicator-sebi-production.up.railway.app`.
   Verify: open `…/health` → `{"status":"ok",...}`.

Start command is the `Procfile`: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.

## 2. Frontend → Vercel

1. **Add New → Project** → import this GitHub repo.
2. **Root Directory:** `frontend`  (Framework preset: Next.js, auto-detected).
3. **Environment Variables:**
   ```
   NEXT_PUBLIC_API_URL=https://<your-railway-backend>.up.railway.app
   ```
4. Deploy. Vercel gives `https://<your-app>.vercel.app`.
5. Back in Railway, set `CORS_ORIGINS` to that Vercel URL and redeploy.

## 3. GitHub

```
gh repo create adjudicator-sebi --private --source=. --remote=origin --push
```
`.env` is gitignored — no secrets are pushed. `node_modules/` and `.next/` are ignored too.

---

## Known limitations (it's a prototype)
- **Single warm DB connection** (`app/db.py`): great for latency, but not concurrency-safe. Fine for a
  single-user demo; under concurrent public traffic, switch to a small connection pool.
- **No auth / no rate limit** on the cost-incurring endpoints (by choice). Add HTTP Basic Auth or a
  shared-token dependency before any public sharing.
- **Region/latency:** Supabase pooler is in `ap-northeast-2`. If Railway runs in a US/EU region, expect
  some added DB round-trip latency (the warm connection mitigates it).

## Adding auth later (optional)
Add a FastAPI dependency that checks an `Authorization` header / HTTP Basic against an env secret, and
attach it to the `analyze` and `code_analysis` routers. ~10 lines.
