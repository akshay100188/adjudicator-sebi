# Deployment — Vercel (frontend) + Render (backend)

The agent backend is long-running (each `/analyze` takes 30–60s) and needs a persistent process +
DB + API keys, so it **cannot** run on Vercel's serverless functions. Render runs a persistent server,
so long requests are fine. The working split:

```
Browser ──► Vercel (Next.js UI) ──HTTPS──► Render (FastAPI agent) ──► Supabase (adjudicator schema)
                                                         └──► Anthropic + OpenAI
```

> **Prototype, not a product. No auth is configured** — anyone who finds the backend URL can trigger
> agent runs that bill your Anthropic/OpenAI keys. Don't share the URL widely, or add a gate later
> (`docs/deploy.md` → "Adding auth").

---

## 1. Backend → Render

Prereqs: a Render account, this repo on GitHub (see §3). The repo ships a `render.yaml` Blueprint.

**Option A — Blueprint (one click):**
1. Render → **New → Blueprint** → connect this GitHub repo. It reads `render.yaml` and creates the
   `adjudicator-sebi-backend` web service (rootDir `backend`, build/start commands preset).
2. It will prompt for the secret env vars (`sync:false`): paste from your local `backend/.env` —
   `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `DATABASE_URL`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`.
   (`DB_SCHEMA`, `CORS_ORIGINS`, `PYTHON_VERSION` come from the Blueprint.)
3. Apply → Render builds and serves at `https://adjudicator-sebi-backend.onrender.com`.
   Verify: open `…/health` → `{"status":"ok",...}`.

**Option B — Manual web service:** New → Web Service → this repo → Root Directory `backend`,
Build `pip install -r requirements.txt`, Start `uvicorn app.main:app --host 0.0.0.0 --port $PORT`,
then add the same env vars.

> Free plan spins down after ~15 min idle; the first request after a nap cold-starts (~50s) **on top
> of** the agent time. Upgrade to a paid instance to keep it warm, or just expect a slow first hit.

## 2. Frontend → Vercel

1. **Add New → Project** → import this GitHub repo.
2. **Root Directory:** `frontend`  (Framework preset: Next.js, auto-detected).
3. **Environment Variables:**
   ```
   NEXT_PUBLIC_API_URL=https://adjudicator-sebi-backend.onrender.com
   ```
4. Deploy. Vercel gives `https://<your-app>.vercel.app`.
5. Back in Render, set `CORS_ORIGINS` to that Vercel URL and redeploy.

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
- **Region/latency:** Supabase pooler is in `ap-northeast-2`. If Render runs in a US/EU region, expect
  some added DB round-trip latency (the warm connection mitigates it). Render free spin-down adds a
  ~50s cold start to the first request after idle.

## Adding auth later (optional)
Add a FastAPI dependency that checks an `Authorization` header / HTTP Basic against an env secret, and
attach it to the `analyze` and `code_analysis` routers. ~10 lines.
