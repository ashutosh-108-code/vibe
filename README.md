# Finance Tracker — ML-Powered Indian Expense Tracker

Finance Tracker is an ML-powered expense tracking application tailored for Indian bank statements (PDF/CSV) and high-frequency UPI transaction habits. It parses bank statements, automatically categorizes transactions using a hybrid rule-based and scikit-learn machine learning classifier, runs anomaly detection on unusual expenditures, and provides plain-language visual summaries and bilingual (English/Hindi) insights.

---

## 🚀 Features

- **Automated Statement Parsing**: Direct ingestion of CSV and PDF bank statements (supported banks include HDFC, SBI, ICICI, AXIS, KOTAK, IDFC).
- **Hybrid Categorization**: Multi-layered classifier combining regex keyword matching with a trained scikit-learn Naive Bayes (`MultinomialNB`) classifier.
- **Anomaly Detection**: Uses scikit-learn's `IsolationForest` to flag unusual transaction spikes per category.
- **Plain-Language Insights**: Bilingual insights toggleable between English and Hindi.
- **Interactive Dashboard**: Recharts-powered donut and daily transaction spending charts.
- **Transaction Table**: Filter, search, and manually update categories on the fly.
- **Demo Mode**: Seeded mock data to instantly explore all pages and charts.

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Icons**: Lucide React
- **HTTP Client**: Axios

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL (via Supabase)
- **ORM**: SQLAlchemy 2 (Async) + Alembic
- **Machine Learning**: scikit-learn (`MultinomialNB`, `TfidfVectorizer`, `IsolationForest`)
- **PDF Ingestion**: PyMuPDF (`fitz`)
- **CSV Ingestion**: pandas

---

## 💻 Local Development Setup

### Prerequisite Environment Configuration

Copy `.env.example` to `.env` (or configure system env variables):

**macOS / Linux / Git Bash:**
```bash
cp .env.example .env
```

**Windows PowerShell (VS Code terminal):**
```powershell
Copy-Item .env.example .env
```

> **Note:** PowerShell does not support `&&` to chain commands. Run each command on its own line, or use `;` between commands (e.g. `cd ml-engine; python -m uvicorn main:app --reload --port 8000`).

### Quick start (two terminals)

**Terminal 1 — backend (PowerShell):**
```powershell
cd ml-engine
python -m uvicorn main:app --reload --port 8000
```

**Terminal 2 — frontend (PowerShell):**
```powershell
cd frontend
npm.cmd run dev
```

If `npm` fails with *running scripts is disabled*, use `npm.cmd` (above) or run once:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then open [http://localhost:3000/upload](http://localhost:3000/upload) and click **Load Demo**.

### 1. Backend Service Setup (Port 8000)

Navigate to the `ml-engine` directory:
```powershell
cd ml-engine
```

Create a Python virtual environment and activate it:
```bash
python -m venv venv
# On Windows (Command Prompt)
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

Install the dependencies:
```bash
pip install -r requirements.txt
```

Run Alembic migrations to construct the database schema (ensure `DATABASE_URL` is configured in your `.env`):
```bash
alembic upgrade head
```

Run the backend server (use `python -m` so it works even when `uvicorn` is not on PATH):
```powershell
python -m uvicorn main:app --reload --port 8000
```
API Documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs).

Without a `DATABASE_URL` in `.env`, the backend uses a local SQLite file at `ml-engine/local.db` automatically.

**Supported PDF layouts:** HDFC/SBI-style tables, plus **Bank of India** / UPI statements where each field (Date, Remarks, Debit, Credit) is on separate lines. Restart the backend after parser updates.

**Troubleshooting: `[WinError 10013]` on port 8000**

Usually another process is already using port 8000 (often a previous `uvicorn` you did not stop).

```powershell
# See what is using port 8000
netstat -ano | findstr ":8000"

# Stop it (replace 12345 with the PID from the last column)
Stop-Process -Id 12345 -Force
```

Then start the backend again. Or use another port:

```powershell
python -m uvicorn main:app --reload --port 8001
```

If you use port 8001, set `NEXT_PUBLIC_API_URL=http://localhost:8001` in `frontend/.env.local`.

### 2. Frontend Application Setup (Port 3000)

Navigate to the `frontend` directory:
```powershell
cd frontend
```

Install npm packages:
```bash
npm install
```

Configure `frontend/.env.local` (optional for local dev):

```powershell
Copy-Item .env.local.example .env.local
```

For **local development**, leave `NEXT_PUBLIC_API_URL` **unset**. Next.js proxies `/api` to the backend automatically (no CORS issues).

Only set `NEXT_PUBLIC_API_URL` in production (your Railway URL).

Start the development server:
```powershell
npm.cmd run dev
```

**Troubleshooting: `npm.ps1 cannot be loaded` / execution policy**

PowerShell may block `npm` scripts. Use either fix:

```powershell
# Option A — no policy change (recommended quick fix)
npm.cmd run dev

# Option B — allow local scripts for your user only (one-time)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
npm run dev
```

In VS Code you can also open a **Command Prompt** terminal (not PowerShell): `Terminal → New Terminal →` pick **Command Prompt**, then `npm run dev`.

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🏗️ Deployment Guide

### Database (Supabase)
1. Set up a free-tier PostgreSQL instance at [Supabase](https://supabase.com).
2. Execute the initialization SQL script inside Supabase's SQL Editor to set up tables (`statements`, `categories`, `transactions`, `insights`).
3. Set your project's transaction connection string as the `DATABASE_URL`.

### Backend (Railway)
1. Deploy the `/ml-engine` directory onto Railway.
2. Railway will auto-detect the `Dockerfile` inside `ml-engine/`.
3. Set the required backend environment variables in Railway:
   - `DATABASE_URL`
   - `SECRET_KEY`
   - `DEBUG=False`
   - `ALLOWED_ORIGINS=https://your-frontend.vercel.app`

### Frontend (Vercel)
1. Deploy the `/frontend` directory onto Vercel.
2. Vercel will auto-detect the configuration using the standard setup and the `vercel.json` wrapper.
3. Configure the environment variable:
   - `NEXT_PUBLIC_API_URL=https://your-backend.railway.app`
