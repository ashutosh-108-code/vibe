# Finance Tracker — ML-Powered Indian Expense Tracker

Finance Tracker parses Indian bank and UPI statements (CSV/PDF), categorizes transactions with a hybrid rule-based + scikit-learn model, and shows charts and bilingual insights on a Next.js dashboard.

**Stack:** Next.js 14 (Vercel) · FastAPI (Railway) · PostgreSQL (Supabase)

---

## Local development

### Prerequisites

- Python 3.11+
- Node.js 18+
- (Optional) Supabase account for a remote database; without `DATABASE_URL`, the backend uses `ml-engine/local.db` (SQLite).

### 1. Environment files

```powershell
Copy-Item .env.example .env
Copy-Item frontend\.env.local.example frontend\.env.local
```

Edit `.env` with your Supabase `DATABASE_URL` if you use PostgreSQL. For local-only testing, you can leave `DATABASE_URL` empty.

### 2. Backend (port 8000)

```powershell
cd ml-engine
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

With Supabase configured:

```powershell
alembic upgrade head
```

Start the API:

```powershell
python -m uvicorn main:app --reload --port 8000
```

Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Frontend (port 3000)

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Open [http://localhost:3000/upload](http://localhost:3000/upload).

**PowerShell notes**

- Use `;` instead of `&&` between commands.
- If `npm` is blocked, use `npm.cmd` or run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` once.
- Leave `NEXT_PUBLIC_API_URL` unset in `frontend/.env.local` so `/api` is proxied to the backend (see `frontend/next.config.js`).

---

## Production deployment

Deploy in this order: **Supabase → Railway (backend) → Vercel (frontend)**.

### Step 1 — Supabase (database)

1. Create a project at [https://supabase.com](https://supabase.com).
2. Open **Project Settings → Database → Connection string → URI**.
3. Copy the URI (transaction pooler `6543` or direct `5432`). Example shape:
   ```text
   postgresql://postgres.[ref]:[PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres
   ```
4. Open **SQL Editor** and run the schema from `documentation.md` **Section 8.1** (tables: `statements`, `categories`, `transactions`, `insights`), **or** run migrations from your machine:

   ```powershell
   cd ml-engine
   # Set DATABASE_URL in .env to the Supabase URI, then:
   alembic upgrade head
   ```

5. Save the connection string — you will use it as `DATABASE_URL` on Railway.

### Step 2 — Railway (backend)

1. Push this repo to GitHub.
2. Go to [https://railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**.
3. Add a service for this repository.
4. Set **Root Directory** to `ml-engine` (Settings → Build).
5. Railway detects `ml-engine/Dockerfile` and builds the image.
6. Add a **public domain** (Settings → Networking → Generate domain).
7. Set **Variables**:

   | Variable | Value |
   |----------|--------|
   | `DATABASE_URL` | Supabase PostgreSQL URI from Step 1 |
   | `SECRET_KEY` | Random 32+ character string |
   | `DEBUG` | `False` |
   | `ALLOWED_ORIGINS` | `https://YOUR-APP.vercel.app` (set after Vercel deploy; add `http://localhost:3000` for local testing) |
   | `MODEL_PATH` | `./models/categorizer.pkl` |
   | `MAX_FILE_SIZE_MB` | `10` |

8. Deploy and confirm health: `https://YOUR-RAILWAY-DOMAIN.up.railway.app/health`  
   Expected: `{"status":"ok","model_loaded":true,"db_connected":true}`

### Step 3 — Vercel (frontend)

1. Go to [https://vercel.com](https://vercel.com) → **Add New Project** → import the same GitHub repo.
2. Set **Root Directory** to `frontend`.
3. Framework preset: **Next.js** (auto-detected).
4. Set **Environment Variables** (Production):

   | Variable | Value |
   |----------|--------|
   | `NEXT_PUBLIC_API_URL` | `https://YOUR-RAILWAY-DOMAIN.up.railway.app` (no trailing slash) |
   | `NEXT_PUBLIC_APP_NAME` | `Finance Tracker` |

5. Click **Deploy**.
6. Copy your Vercel URL (e.g. `https://finance-tracker-xyz.vercel.app`).
7. Return to Railway → update `ALLOWED_ORIGINS` to include that exact URL (comma-separated if multiple).
8. Redeploy the Railway service if you changed `ALLOWED_ORIGINS`.

### Step 4 — Smoke test

1. Open `https://YOUR-APP.vercel.app/upload`
2. Click **Load Demo** or upload a CSV/PDF.
3. Confirm **Dashboard** and **Insights** load.

---

## Environment variables reference

See [.env.example](.env.example) for the full list.

| Variable | Where | Purpose |
|----------|--------|---------|
| `DATABASE_URL` | Railway | Supabase PostgreSQL connection |
| `SECRET_KEY` | Railway | App secret (reserved for future use) |
| `DEBUG` | Railway | `False` in production |
| `ALLOWED_ORIGINS` | Railway | Comma-separated frontend URLs for CORS |
| `MODEL_PATH` | Railway | Path to trained categorizer pickle |
| `MAX_FILE_SIZE_MB` | Railway | Upload size limit |
| `NEXT_PUBLIC_API_URL` | Vercel | Public Railway API base URL |
| `NEXT_PUBLIC_APP_NAME` | Vercel | Display name |
| `API_PROXY_URL` | Local only | Backend URL for Next.js rewrites in dev |

---

## Project layout

```text
finance-tracker/
├── Agents.txt              # Agent rules (same as AGENTS.md spec)
├── .env.example
├── README.md
├── frontend/               # Next.js 14 → deploy to Vercel
│   ├── next.config.js      # API rewrites for local dev
│   └── vercel.json
└── ml-engine/              # FastAPI → deploy to Railway
    ├── Dockerfile
    ├── requirements.txt
    └── main.py
```

---

## Build verification

```powershell
cd frontend
npm.cmd run build
```

Production build must complete with no errors before deploying to Vercel.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `[WinError 10013]` on port 8000 | Another process is using the port; `netstat -ano \| findstr ":8000"` then `Stop-Process -Id <PID> -Force` |
| `npm.ps1 cannot be loaded` | Use `npm.cmd` or adjust PowerShell execution policy |
| CORS / network error on upload | Set `ALLOWED_ORIGINS` on Railway to your Vercel URL; on Vercel set `NEXT_PUBLIC_API_URL` to Railway URL |
| Empty dashboard after upload | Restart backend after parser changes; ensure `DATABASE_URL` is valid |

---

## License

MIT (hackathon / educational use).
