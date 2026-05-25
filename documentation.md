# Finance Tracker — Complete Vibe Coding Documentation
> Version 2.0 — 95% Codex-ready. Every section is actionable.

---

## QUICK START FOR CODEX

Copy this into your terminal to begin:
```bash
mkdir finance-tracker && cd finance-tracker
codex "read AGENTS.md and scaffold the full project structure as defined"
```

---

## SECTION 1: AGENTS.md
> Paste this file as `/finance-tracker/AGENTS.md` — Codex reads this before every task.

```markdown
# AGENTS.md — Finance Tracker

## What we are building
An ML-powered expense tracker for Indian users. Users upload their bank
statements (CSV or PDF), the backend parses and categorizes every
transaction using a hybrid rule-based + scikit-learn ML model, then the
frontend displays charts, spending summaries, and plain-language insights
in English and Hindi.

## Tech stack (exact — do not deviate)
- Frontend : Next.js 14 (App Router) + Tailwind CSS + Recharts + Lucide React
- Backend  : Python FastAPI only (NO Node.js — single backend for hackathon speed)
- Database : PostgreSQL via Supabase (free tier)
- ML       : scikit-learn MultinomialNB + TfidfVectorizer + IsolationForest
- PDF parse: PyMuPDF (fitz)
- CSV parse: pandas
- Deploy   : Vercel (frontend) + Railway (backend)

## Ports
- Frontend : http://localhost:3000
- Backend  : http://localhost:8000
- DB       : Supabase (remote only, use DATABASE_URL from .env)

## Absolute rules — never break these
1. NO authentication or login for MVP — every endpoint is public
2. NO image/OCR parsing — CSV and PDF only
3. NO push notifications — in-app alerts only
4. NO XGBoost — MultinomialNB is faster, good enough at 94%+
5. NO Node.js backend — FastAPI handles everything
6. NO paid APIs — all ML runs locally
7. ALL currency in Indian Rupees, formatted as ₹1,23,456 (Indian numbering)
8. ALWAYS handle errors with try/except (Python) and try/catch (JS)
9. NEVER store raw file bytes in the database — only extracted text + metadata
10. ALWAYS add CORS middleware to FastAPI (frontend is on a different port)

## Fixed category list (8 categories — never add or remove)
Food, Transport, Groceries, Rent, EMI, Shopping, Investments, Other

## Color map for categories (use exact hex in all charts and badges)
Food        → #F59E0B  (amber)
Transport   → #3B82F6  (blue)
Groceries   → #10B981  (emerald)
Rent        → #8B5CF6  (violet)
EMI         → #EF4444  (red)
Shopping    → #EC4899  (pink)
Investments → #06B6D4  (cyan)
Other       → #64748B  (slate)

## Icon map (Lucide React — use exact icon names)
Food        → UtensilsCrossed
Transport   → Car
Groceries   → ShoppingCart
Rent        → Home
EMI         → CreditCard
Shopping    → ShoppingBag
Investments → TrendingUp
Other       → MoreHorizontal

## Design system (exact values — do not change)
Primary bg  : #F8FAFC
Header/nav  : #1E293B
Success     : #10B981
Warning     : #F59E0B
Error       : #EF4444
Neutral     : #64748B
Font        : Inter (import from Google Fonts)
Border radius: 8px on all cards and inputs
Spacing grid : 4px / 8px system
Shadows     : shadow-sm on cards, no shadow on buttons unless hovered

## What to build in order (follow this sequence)
1. FastAPI backend skeleton with CORS and health check
2. ML categorizer (rule-based + trained MultinomialNB)
3. PDF + CSV file parsers
4. POST /api/upload endpoint (full pipeline)
5. GET /api/stats and GET /api/insights endpoints
6. PostgreSQL schema + Supabase connection
7. Next.js frontend scaffold with Tailwind
8. Upload page with drag-and-drop
9. Dashboard page with charts (Recharts donut + bar)
10. Transaction table with search and re-categorize
11. Insights panel (plain language + Hindi toggle)
12. Demo mode with mock data
13. Deploy config (Vercel + Railway)

## File to never touch
- .env (exists, do not read or modify — just reference env variable names)
- /ml-engine/data/training_data.py (exists, do not regenerate)
```

---

## SECTION 2: PROJECT DESCRIPTION

The Finance Tracker App is a financial management tool for Indian college
students and salaried professionals. It solves "reckless spending" caused by
high-frequency UPI transactions by automatically parsing bank statements
(PDF or CSV), categorizing every transaction with ML, and showing clear
charts and plain-language insights in English and Hindi.

**Core loop:**
Upload statement → ML parses + categorizes → Dashboard shows charts →
Insights explain spending in plain language → User understands their money.

---

## SECTION 3: PRODUCT REQUIREMENTS DOCUMENT (PRD)

### 3.1 Executive Summary
Finance Tracker is a zero-friction expense analytics tool. No manual entry,
no bank login, no complex setup. Upload one file, get instant clarity.

### 3.2 Goals
- Automate extraction and categorization of bank transaction data
- Provide a clean dashboard for spending visualization
- Offer intelligent, human-readable insights into spending habits
- Support English and Hindi (static translation, not live chatbot)

### 3.3 Target Users
- **Primary:** College students managing pocket money (₹5,000–25,000/month)
- **Secondary:** Salaried professionals managing UPI habits (₹30,000–1,00,000/month)

### 3.4 Functional Requirements (MVP scope — hackathon)

| Feature | In Scope | Out of Scope |
|---------|----------|--------------|
| CSV upload + parse | ✅ | — |
| PDF upload + parse | ✅ | — |
| Image/screenshot OCR | ❌ | Phase 2 |
| ML categorization | ✅ | — |
| Donut + bar charts | ✅ | — |
| Transaction table | ✅ | — |
| Plain-language insights | ✅ | — |
| Hindi translation (static) | ✅ | — |
| Re-categorize transaction | ✅ | — |
| Anomaly detection | ✅ | — |
| User authentication/login | ❌ | Phase 2 |
| Push notifications | ❌ | Phase 2 |
| Budget goal setting | ❌ | Phase 2 |
| Live chatbot | ❌ | Phase 2 |
| Multi-user isolation | ❌ | Phase 2 |

### 3.5 Non-Functional Requirements

**Performance:**
- Dashboard load: under 2 seconds
- ML inference on 500-row CSV: under 5 seconds
- API response (stats): under 300ms

**Security:**
- No raw banking credentials ever stored
- Files processed in-memory where possible, deleted after parsing
- TLS in transit (handled by Vercel + Railway automatically)

**Design:**
- Minimalist, flat UI — no gradients, no particle effects
- High contrast, readable at small sizes
- Mobile-first responsive layout

---

## SECTION 4: TECH STACK (SIMPLIFIED — HACKATHON OPTIMIZED)

### 4.1 Why we removed Node.js
The original design had Node.js as an API gateway + FastAPI as an ML sidecar.
This adds complexity for zero benefit in MVP. FastAPI handles everything:
routing, file uploads, DB queries, and ML inference. One backend = faster build.

### 4.2 Frontend
```
Framework   : Next.js 14 (App Router)
Styling     : Tailwind CSS 3
Charts      : Recharts 2
Icons       : Lucide React
HTTP client : Axios
Language    : TypeScript

Install commands:
npx create-next-app@latest frontend --typescript --tailwind --app
cd frontend
npm install recharts lucide-react axios
```

### 4.3 Backend
```
Framework   : FastAPI
Language    : Python 3.11+
ORM         : SQLAlchemy 2 + asyncpg
Migrations  : Alembic
Server      : Uvicorn

Install commands:
pip install fastapi uvicorn sqlalchemy asyncpg alembic
pip install python-multipart pandas PyMuPDF scikit-learn
pip install python-dotenv psycopg2-binary
```

### 4.4 Machine Learning
```
Text vectorizer : TfidfVectorizer (scikit-learn)
Classifier      : MultinomialNB (scikit-learn)
Anomaly detect  : IsolationForest (scikit-learn)
PDF parsing     : PyMuPDF (fitz) — better than PyPDF2 for tables
CSV parsing     : pandas
Model storage   : pickle (saved to /ml-engine/models/)

DO NOT USE: XGBoost (overkill), spaCy (heavy, slow startup),
            Tesseract (OCR not in scope), Googletrans (flaky API)
```

### 4.5 Database
```
Engine    : PostgreSQL 15
Hosting   : Supabase (free tier, 500MB)
ORM       : SQLAlchemy
Access    : Connection string in DATABASE_URL env var
```

### 4.6 Deployment
```
Frontend  : Vercel (push to GitHub, auto-deploy)
Backend   : Railway (Dockerfile or requirements.txt detected)
DB        : Supabase (always-on free tier)
```

---

## SECTION 5: PROJECT STRUCTURE

```
/finance-tracker/
│
├── AGENTS.md                        ← Codex reads this first
├── .env                             ← Never commit this
├── .env.example                     ← Commit this (empty values)
├── README.md
│
├── /frontend/                       ← Next.js App Router
│   ├── app/
│   │   ├── layout.tsx               ← Root layout (Inter font, nav)
│   │   ├── page.tsx                 ← Redirect to /dashboard
│   │   ├── dashboard/
│   │   │   └── page.tsx             ← Main dashboard with charts
│   │   ├── upload/
│   │   │   └── page.tsx             ← File upload page
│   │   └── insights/
│   │       └── page.tsx             ← Insights + Hindi toggle
│   ├── components/
│   │   ├── Navbar.tsx               ← Top nav with language toggle
│   │   ├── SpendingDonut.tsx        ← Recharts donut chart
│   │   ├── DailyBarChart.tsx        ← Recharts bar chart
│   │   ├── TransactionTable.tsx     ← Searchable transaction list
│   │   ├── InsightCard.tsx          ← Single insight with icon
│   │   ├── CategoryBadge.tsx        ← Colored pill for each category
│   │   ├── UploadZone.tsx           ← Drag-and-drop file upload
│   │   ├── AnomalyAlert.tsx         ← Red alert for unusual transactions
│   │   └── EmptyState.tsx           ← Shown when no data uploaded
│   ├── lib/
│   │   ├── api.ts                   ← Axios instance + all API calls
│   │   ├── formatters.ts            ← Indian number formatting (₹1,23,456)
│   │   └── translations.ts          ← English/Hindi string map
│   ├── hooks/
│   │   └── useTransactions.ts       ← React hook for transaction state
│   ├── types/
│   │   └── index.ts                 ← TypeScript interfaces
│   └── public/
│       └── demo-data.json           ← 50 mock transactions for demo mode
│
├── /ml-engine/                      ← FastAPI + ML (single backend)
│   ├── main.py                      ← FastAPI app entry point
│   ├── requirements.txt
│   ├── Dockerfile                   ← For Railway deployment
│   ├── /routers/
│   │   ├── upload.py                ← POST /api/upload
│   │   ├── stats.py                 ← GET /api/stats
│   │   ├── insights.py              ← GET /api/insights
│   │   ├── transactions.py          ← GET/PATCH /api/transactions
│   │   └── health.py                ← GET /health
│   ├── /services/
│   │   ├── file_parser.py           ← CSV + PDF text extraction
│   │   ├── categorizer.py           ← Rule-based + ML categorization
│   │   ├── anomaly_detector.py      ← IsolationForest spike detection
│   │   └── insight_generator.py     ← Plain language insight strings
│   ├── /db/
│   │   ├── database.py              ← SQLAlchemy async engine + session
│   │   ├── models.py                ← ORM table definitions
│   │   └── schemas.py               ← Pydantic request/response schemas
│   ├── /data/
│   │   └── training_data.py         ← 150+ labeled transactions
│   └── /models/
│       └── categorizer.pkl          ← Saved trained model (gitignore this)
│
└── /scripts/
    ├── train_model.py               ← Run once to train + save model
    ├── seed_db.py                   ← Populate DB with demo transactions
    └── test_api.sh                  ← curl commands to test all endpoints
```

---

## SECTION 6: ENVIRONMENT VARIABLES

### `.env` (never commit — add to .gitignore)
```bash
# ─── Database ───────────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres

# ─── FastAPI ────────────────────────────────────────────────
SECRET_KEY=your-random-32-char-string-here
DEBUG=True
ALLOWED_ORIGINS=http://localhost:3000,https://your-vercel-app.vercel.app

# ─── ML Model ───────────────────────────────────────────────
MODEL_PATH=./models/categorizer.pkl
MAX_FILE_SIZE_MB=10

# ─── Frontend (Next.js) ─────────────────────────────────────
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Finance Tracker
```

### `.env.example` (commit this)
```bash
DATABASE_URL=
SECRET_KEY=
DEBUG=True
ALLOWED_ORIGINS=http://localhost:3000
MODEL_PATH=./models/categorizer.pkl
MAX_FILE_SIZE_MB=10
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Finance Tracker
```

---

## SECTION 7: API CONTRACTS (COMPLETE)

### Base URL
- Development: `http://localhost:8000`
- Production: `https://your-app.railway.app`

### 7.1 Health Check
```
GET /health

Response 200:
{
  "status": "ok",
  "model_loaded": true,
  "db_connected": true
}
```

### 7.2 Upload Statement (Primary endpoint)
```
POST /api/upload
Content-Type: multipart/form-data

Body:
  file: File (.csv or .pdf, max 10MB)
  session_id?: string  (optional UUID for grouping uploads)

Response 200:
{
  "statement_id": "uuid-string",
  "filename": "hdfc_jan_2024.csv",
  "bank_detected": "HDFC",
  "total_transactions": 87,
  "transactions": [
    {
      "id": "uuid",
      "date": "2024-01-15",
      "merchant": "Swiggy",
      "raw_description": "UPI-SWIGGY-BANGALORE-9876543210",
      "amount": 450.00,
      "type": "debit",
      "category": "Food",
      "confidence": 0.97,
      "is_anomaly": false
    }
  ],
  "summary": {
    "total_debit": 32450.00,
    "total_credit": 50000.00,
    "by_category": {
      "Food": 8400.00,
      "Transport": 2100.00,
      "Groceries": 4500.00,
      "Rent": 12000.00,
      "EMI": 3000.00,
      "Shopping": 1800.00,
      "Investments": 5000.00,
      "Other": 1650.00
    },
    "anomalies": [
      {
        "transaction_id": "uuid",
        "merchant": "Amazon",
        "amount": 8999.00,
        "reason": "Amount is 3.2x above your usual Amazon spending (₹2,800)"
      }
    ]
  }
}

Response 400:
{
  "error": "UNSUPPORTED_FORMAT",
  "message": "Only CSV and PDF files are supported. Received: .xlsx"
}

Response 422:
{
  "error": "PARSE_FAILED",
  "message": "Could not extract transactions from this PDF. Try exporting as CSV from your bank app.",
  "rows_extracted": 0
}

Response 413:
{
  "error": "FILE_TOO_LARGE",
  "message": "File size 12.4MB exceeds the 10MB limit."
}
```

### 7.3 Get Statistics
```
GET /api/stats?statement_id=uuid&period=monthly

Query params:
  statement_id: string (required)
  period: "weekly" | "monthly" | "all"  (default: monthly)

Response 200:
{
  "period": "monthly",
  "total_debit": 32450.00,
  "total_credit": 50000.00,
  "net_savings": 17550.00,
  "savings_rate": 35.1,
  "by_category": {
    "Food": { "amount": 8400.00, "percentage": 25.9, "transaction_count": 34 },
    "Transport": { "amount": 2100.00, "percentage": 6.5, "transaction_count": 12 }
  },
  "daily_spending": [
    { "date": "2024-01-01", "amount": 450.00 },
    { "date": "2024-01-02", "amount": 1200.00 }
  ],
  "top_merchants": [
    { "merchant": "Swiggy", "amount": 3200.00, "count": 14 },
    { "merchant": "Ola", "amount": 1800.00, "count": 8 }
  ]
}
```

### 7.4 Get Insights
```
GET /api/insights?statement_id=uuid&language=en

Query params:
  statement_id: string (required)
  language: "en" | "hi"  (default: en)

Response 200:
{
  "language": "en",
  "insights": [
    {
      "type": "overspend",
      "category": "Food",
      "icon": "UtensilsCrossed",
      "title": "Food spending is high",
      "body": "You spent ₹8,400 on food this month — 26% of total expenses. Top merchant: Swiggy (₹3,200 across 14 orders).",
      "severity": "warning"
    },
    {
      "type": "positive",
      "category": "Investments",
      "icon": "TrendingUp",
      "title": "Great savings habit",
      "body": "You invested ₹5,000 this month. That's 15% of your income — above the recommended 10%.",
      "severity": "success"
    },
    {
      "type": "anomaly",
      "category": "Shopping",
      "icon": "ShoppingBag",
      "title": "Unusual spending detected",
      "body": "Your Amazon purchase of ₹8,999 on Jan 15 is 3x above your usual shopping amount.",
      "severity": "error"
    }
  ]
}

Hindi response (language=hi):
{
  "language": "hi",
  "insights": [
    {
      "type": "overspend",
      "category": "Food",
      "title": "खाने पर ज़्यादा खर्च",
      "body": "इस महीने आपने खाने पर ₹8,400 खर्च किए — कुल खर्च का 26%। सबसे ज़्यादा Swiggy पर: ₹3,200।",
      "severity": "warning"
    }
  ]
}
```

### 7.5 Get Transactions
```
GET /api/transactions?statement_id=uuid&category=Food&search=swiggy&page=1&limit=20

Query params:
  statement_id: string (required)
  category?: string (filter by category name)
  search?: string (search in merchant name)
  page?: number (default: 1)
  limit?: number (default: 20, max: 100)

Response 200:
{
  "total": 87,
  "page": 1,
  "limit": 20,
  "transactions": [ ...transaction objects... ]
}
```

### 7.6 Re-categorize Transaction
```
PATCH /api/transactions/{transaction_id}/category

Body:
{
  "category": "Food"
}

Response 200:
{
  "transaction_id": "uuid",
  "old_category": "Other",
  "new_category": "Food",
  "updated": true
}
```

### 7.7 Load Demo Data
```
POST /api/demo

Response 200:
{
  "statement_id": "demo-statement-uuid",
  "message": "50 demo transactions loaded",
  "redirect_to": "/dashboard?statement_id=demo-statement-uuid"
}
```

---

## SECTION 8: DATABASE SCHEMA (COMPLETE)

### 8.1 Create tables SQL
```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Statements: tracks uploaded files
CREATE TABLE statements (
  statement_id  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  filename      VARCHAR(255) NOT NULL,
  bank_name     VARCHAR(100),
  file_type     VARCHAR(10) NOT NULL CHECK (file_type IN ('csv', 'pdf')),
  upload_date   TIMESTAMP DEFAULT NOW(),
  status        VARCHAR(20) DEFAULT 'pending'
                  CHECK (status IN ('pending', 'processing', 'completed', 'error')),
  total_rows    INTEGER DEFAULT 0,
  error_message TEXT
);

-- Categories: fixed lookup table
CREATE TABLE categories (
  category_id   SERIAL PRIMARY KEY,
  name          VARCHAR(50) UNIQUE NOT NULL,
  color_hex     VARCHAR(7) NOT NULL,
  icon_key      VARCHAR(50) NOT NULL
);

INSERT INTO categories (name, color_hex, icon_key) VALUES
  ('Food',        '#F59E0B', 'UtensilsCrossed'),
  ('Transport',   '#3B82F6', 'Car'),
  ('Groceries',   '#10B981', 'ShoppingCart'),
  ('Rent',        '#8B5CF6', 'Home'),
  ('EMI',         '#EF4444', 'CreditCard'),
  ('Shopping',    '#EC4899', 'ShoppingBag'),
  ('Investments', '#06B6D4', 'TrendingUp'),
  ('Other',       '#64748B', 'MoreHorizontal');

-- Transactions: core table
CREATE TABLE transactions (
  transaction_id    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  statement_id      UUID REFERENCES statements(statement_id) ON DELETE CASCADE,
  transaction_date  DATE NOT NULL,
  merchant          VARCHAR(255),
  raw_description   TEXT NOT NULL,
  amount            DECIMAL(12, 2) NOT NULL,
  transaction_type  VARCHAR(10) CHECK (transaction_type IN ('debit', 'credit')),
  category_id       INTEGER REFERENCES categories(category_id),
  ml_confidence     FLOAT,
  is_anomaly        BOOLEAN DEFAULT FALSE,
  anomaly_reason    TEXT,
  manually_updated  BOOLEAN DEFAULT FALSE,
  created_at        TIMESTAMP DEFAULT NOW()
);

-- Indexes for fast dashboard queries
CREATE INDEX idx_transactions_statement ON transactions(statement_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_category ON transactions(category_id);

-- Insights: pre-generated plain language summaries
CREATE TABLE insights (
  insight_id    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  statement_id  UUID REFERENCES statements(statement_id) ON DELETE CASCADE,
  insight_type  VARCHAR(30) NOT NULL,
  category      VARCHAR(50),
  title_en      TEXT NOT NULL,
  body_en       TEXT NOT NULL,
  title_hi      TEXT,
  body_hi       TEXT,
  severity      VARCHAR(10) CHECK (severity IN ('success', 'warning', 'error', 'info')),
  created_at    TIMESTAMP DEFAULT NOW()
);
```

### 8.2 SQLAlchemy models (Python)
```python
# ml-engine/db/models.py
from sqlalchemy import Column, String, Float, Boolean, Integer, Date, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class Statement(Base):
    __tablename__ = "statements"
    statement_id  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename      = Column(String(255), nullable=False)
    bank_name     = Column(String(100))
    file_type     = Column(String(10), nullable=False)
    status        = Column(String(20), default="pending")
    total_rows    = Column(Integer, default=0)
    transactions  = relationship("Transaction", back_populates="statement")

class Transaction(Base):
    __tablename__ = "transactions"
    transaction_id   = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    statement_id     = Column(UUID(as_uuid=True), ForeignKey("statements.statement_id"))
    transaction_date = Column(Date, nullable=False)
    merchant         = Column(String(255))
    raw_description  = Column(Text, nullable=False)
    amount           = Column(Float, nullable=False)
    transaction_type = Column(String(10))
    category_id      = Column(Integer, ForeignKey("categories.category_id"))
    ml_confidence    = Column(Float)
    is_anomaly       = Column(Boolean, default=False)
    anomaly_reason   = Column(Text)
    manually_updated = Column(Boolean, default=False)
    statement        = relationship("Statement", back_populates="transactions")
    category         = relationship("Category")

class Category(Base):
    __tablename__ = "categories"
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name        = Column(String(50), unique=True, nullable=False)
    color_hex   = Column(String(7), nullable=False)
    icon_key    = Column(String(50), nullable=False)
```

---

## SECTION 9: ML PIPELINE — COMPLETE IMPLEMENTATION

### 9.1 Training Data (150+ labeled examples)
```python
# ml-engine/data/training_data.py
# Copy this file as-is. Codex will use it to train the model.

LABELED_TRANSACTIONS = [
    # ─── Food (30 examples) ───────────────────────────────────────────────
    ("Swiggy order Bangalore", "Food"),
    ("SWIGGY*ORDER", "Food"),
    ("Zomato delivery", "Food"),
    ("ZOMATO*PAYMENT", "Food"),
    ("Dominos Pizza", "Food"),
    ("McDonald's payment", "Food"),
    ("KFC order", "Food"),
    ("Pizza Hut", "Food"),
    ("Starbucks Coffee", "Food"),
    ("Cafe Coffee Day", "Food"),
    ("Udupi restaurant", "Food"),
    ("Darshini hotel", "Food"),
    ("UPI food delivery", "Food"),
    ("Dunzo grocery delivery", "Food"),
    ("Blinkit order", "Food"),
    ("Zepto delivery", "Food"),
    ("Instamart delivery", "Food"),
    ("Restaurant payment", "Food"),
    ("Haldiram snacks", "Food"),
    ("Chai sutta bar", "Food"),
    ("Burger King", "Food"),
    ("Subway India", "Food"),
    ("Box8 meals", "Food"),
    ("Faasos order", "Food"),
    ("Lunchbox delivery", "Food"),
    ("Freshmenu order", "Food"),
    ("EatSure payment", "Food"),
    ("Behrouz biryani", "Food"),
    ("Paradise biryani", "Food"),
    ("Biryani by kilo", "Food"),

    # ─── Transport (25 examples) ──────────────────────────────────────────
    ("Ola cab Bangalore", "Transport"),
    ("OLA*RIDE", "Transport"),
    ("Uber ride payment", "Transport"),
    ("UBER*TRIP", "Transport"),
    ("Rapido bike taxi", "Transport"),
    ("BluSmart electric cab", "Transport"),
    ("BMTC bus pass", "Transport"),
    ("Metro card recharge", "Transport"),
    ("DMRC metro card", "Transport"),
    ("Namma Metro recharge", "Transport"),
    ("IRCTC train ticket", "Transport"),
    ("Indian Railways booking", "Transport"),
    ("IndiGo flight", "Transport"),
    ("Air India ticket", "Transport"),
    ("SpiceJet booking", "Transport"),
    ("RedBus ticket", "Transport"),
    ("Petrol pump HPCL", "Transport"),
    ("IOCL fuel", "Transport"),
    ("BPCL petrol", "Transport"),
    ("Shell fuel station", "Transport"),
    ("Fastag recharge", "Transport"),
    ("Parking fee", "Transport"),
    ("MoveInSync cab", "Transport"),
    ("Yulu bike rental", "Transport"),
    ("Bounce scooter", "Transport"),

    # ─── Groceries (20 examples) ──────────────────────────────────────────
    ("BigBasket order", "Groceries"),
    ("BIGBASKET*PAYMENT", "Groceries"),
    ("DMart purchase", "Groceries"),
    ("More supermarket", "Groceries"),
    ("Reliance Fresh", "Groceries"),
    ("Nature's Basket", "Groceries"),
    ("Spar hypermarket", "Groceries"),
    ("Star Bazaar", "Groceries"),
    ("WinMart grocery", "Groceries"),
    ("Grofers delivery", "Groceries"),
    ("JioMart order", "Groceries"),
    ("Milkbasket subscription", "Groceries"),
    ("Daily harvest dairy", "Groceries"),
    ("Country Delight milk", "Groceries"),
    ("Vegetables market", "Groceries"),
    ("Kirana store UPI", "Groceries"),
    ("Subramanian provision", "Groceries"),
    ("General store payment", "Groceries"),
    ("Nilgiris supermarket", "Groceries"),
    ("Spencer's retail", "Groceries"),

    # ─── Rent (10 examples) ───────────────────────────────────────────────
    ("House rent January", "Rent"),
    ("Rental payment landlord", "Rent"),
    ("PG accommodation fee", "Rent"),
    ("Flat rent transfer", "Rent"),
    ("NoBroker rent payment", "Rent"),
    ("MagicBricks rental", "Rent"),
    ("Society maintenance", "Rent"),
    ("Apartment maintenance fee", "Rent"),
    ("Water bill BWSSB", "Rent"),
    ("Property tax payment", "Rent"),

    # ─── EMI (15 examples) ────────────────────────────────────────────────
    ("HDFC Bank EMI", "EMI"),
    ("ICICI Bank EMI debit", "EMI"),
    ("Axis Bank loan EMI", "EMI"),
    ("SBI personal loan", "EMI"),
    ("Bajaj Finserv EMI", "EMI"),
    ("Kreditbee loan repay", "EMI"),
    ("MoneyTap EMI", "EMI"),
    ("ZestMoney installment", "EMI"),
    ("Simpl repayment", "EMI"),
    ("LazyPay repay", "EMI"),
    ("PaySense EMI", "EMI"),
    ("Car loan EMI HDFC", "EMI"),
    ("Two wheeler loan", "EMI"),
    ("Education loan SBI", "EMI"),
    ("Home loan EMI", "EMI"),

    # ─── Shopping (20 examples) ───────────────────────────────────────────
    ("Amazon India purchase", "Shopping"),
    ("AMAZON*PAYMENT", "Shopping"),
    ("Flipkart order", "Shopping"),
    ("FLIPKART*PAYMENT", "Shopping"),
    ("Myntra clothing", "Shopping"),
    ("Ajio fashion", "Shopping"),
    ("Meesho order", "Shopping"),
    ("Nykaa beauty", "Shopping"),
    ("Purplle cosmetics", "Shopping"),
    ("Snapdeal purchase", "Shopping"),
    ("Croma electronics", "Shopping"),
    ("Vijay Sales", "Shopping"),
    ("Reliance Digital", "Shopping"),
    ("Decathlon sports", "Shopping"),
    ("Westside clothing", "Shopping"),
    ("FabIndia", "Shopping"),
    ("Max Fashion", "Shopping"),
    ("Lifestyle store", "Shopping"),
    ("H&M India", "Shopping"),
    ("Zara India", "Shopping"),

    # ─── Investments (15 examples) ────────────────────────────────────────
    ("Zerodha SIP", "Investments"),
    ("Groww mutual fund", "Investments"),
    ("Paytm Money SIP", "Investments"),
    ("Kuvera investment", "Investments"),
    ("Coin by Zerodha", "Investments"),
    ("INDMoney stocks", "Investments"),
    ("Upstox trading", "Investments"),
    ("5Paisa investment", "Investments"),
    ("SBI Mutual Fund", "Investments"),
    ("HDFC Mutual Fund SIP", "Investments"),
    ("Axis Mutual Fund", "Investments"),
    ("NSDL PPFAS fund", "Investments"),
    ("LIC premium payment", "Investments"),
    ("NPS contribution", "Investments"),
    ("Post office RD", "Investments"),

    # ─── Other (15 examples) ──────────────────────────────────────────────
    ("HDFC credit card bill", "Other"),
    ("Electricity bill BESCOM", "Other"),
    ("Airtel mobile recharge", "Other"),
    ("Jio postpaid bill", "Other"),
    ("Vi telecom bill", "Other"),
    ("Tata Sky DTH", "Other"),
    ("Netflix subscription", "Other"),
    ("Spotify premium", "Other"),
    ("Amazon Prime", "Other"),
    ("Hotstar subscription", "Other"),
    ("Google Play purchase", "Other"),
    ("PhonePe transfer", "Other"),
    ("GPay send money", "Other"),
    ("Salary credit", "Other"),
    ("ATM withdrawal", "Other"),
]

# Rule-based keyword map (checked BEFORE ML model)
# Codex: do not modify this dict — it is the source of truth
KEYWORD_RULES = {
    "Food": [
        "swiggy", "zomato", "dominos", "mcdonalds", "kfc", "pizza hut",
        "starbucks", "cafe", "restaurant", "biryani", "blinkit", "zepto",
        "instamart", "dunzo", "faasos", "box8", "lunchbox", "freshmenu",
        "eatsure", "burger king", "subway", "behrouz", "paradise biryani",
        "haldiram", "chai", "udupi", "darshini", "hotel food",
    ],
    "Transport": [
        "ola", "uber", "rapido", "blusmart", "bmtc", "metro", "dmrc",
        "irctc", "indigo", "air india", "spicejet", "redbus", "petrol",
        "iocl", "hpcl", "bpcl", "shell", "fuel", "fastag", "parking",
        "yulu", "bounce", "namma metro",
    ],
    "Groceries": [
        "bigbasket", "dmart", "more supermarket", "reliance fresh",
        "spar", "star bazaar", "grofers", "jiomart", "milkbasket",
        "country delight", "vegetables", "kirana", "provision", "grocery",
        "nilgiris", "spencer",
    ],
    "Rent": [
        "rent", "rental", "pg accommodation", "flat rent", "nobroker",
        "society maintenance", "apartment maintenance", "water bill",
        "bwssb", "property tax",
    ],
    "EMI": [
        "emi", "loan repay", "loan emi", "bajaj finserv", "kreditbee",
        "moneytap", "zestmoney", "simpl repay", "lazypay", "paysense",
        "car loan", "two wheeler loan", "education loan", "home loan",
    ],
    "Shopping": [
        "amazon", "flipkart", "myntra", "ajio", "meesho", "nykaa",
        "purplle", "snapdeal", "croma", "vijay sales", "reliance digital",
        "decathlon", "westside", "fabindia", "max fashion", "lifestyle",
        "h&m", "zara",
    ],
    "Investments": [
        "zerodha", "groww", "kuvera", "upstox", "5paisa", "indmoney",
        "sip", "mutual fund", "lic premium", "nps", "ppfas", "rd ",
        "post office rd",
    ],
}
```

### 9.2 Categorizer Service
```python
# ml-engine/services/categorizer.py
import pickle
import os
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from data.training_data import LABELED_TRANSACTIONS, KEYWORD_RULES

MODEL_PATH = Path(os.getenv("MODEL_PATH", "./models/categorizer.pkl"))

class ExpenseCategorizer:
    def __init__(self):
        self.rules = KEYWORD_RULES
        self.pipeline = None
        self._load_or_train()

    def _load_or_train(self):
        if MODEL_PATH.exists():
            with open(MODEL_PATH, "rb") as f:
                self.pipeline = pickle.load(f)
        else:
            self._train()

    def _train(self):
        texts = [t[0] for t in LABELED_TRANSACTIONS]
        labels = [t[1] for t in LABELED_TRANSACTIONS]
        self.pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4),
                                      min_df=1, sublinear_tf=True)),
            ("clf", MultinomialNB(alpha=0.1)),
        ])
        self.pipeline.fit(texts, labels)
        MODEL_PATH.parent.mkdir(exist_ok=True)
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(self.pipeline, f)

    def categorize(self, description: str) -> tuple[str, float]:
        """Returns (category, confidence). Tries rules first, ML as fallback."""
        text_lower = description.lower()
        for category, keywords in self.rules.items():
            if any(kw in text_lower for kw in keywords):
                return category, 1.0  # Rule-based: full confidence

        # ML fallback
        proba = self.pipeline.predict_proba([description])[0]
        confidence = float(proba.max())
        category = self.pipeline.classes_[proba.argmax()]
        return category, confidence

    def categorize_batch(self, descriptions: list[str]) -> list[dict]:
        return [
            {"category": cat, "confidence": conf}
            for cat, conf in (self.categorize(d) for d in descriptions)
        ]

# Singleton — import this everywhere
categorizer = ExpenseCategorizer()
```

### 9.3 File Parser (CSV + PDF)
```python
# ml-engine/services/file_parser.py
import pandas as pd
import fitz  # PyMuPDF
import re
from io import BytesIO
from datetime import datetime

# Column name mappings for major Indian banks
BANK_COLUMN_MAPS = {
    "HDFC": {
        "date": "Date",
        "description": "Narration",
        "debit": "Withdrawal Amt.",
        "credit": "Deposit Amt.",
        "balance": "Closing Balance",
    },
    "SBI": {
        "date": "Txn Date",
        "description": "Description",
        "debit": "Debit",
        "credit": "Credit",
        "balance": "Balance",
    },
    "ICICI": {
        "date": "Transaction Date",
        "description": "Transaction Remarks",
        "debit": "Debit Amount",
        "credit": "Credit Amount",
        "balance": "Balance",
    },
    "AXIS": {
        "date": "Tran Date",
        "description": "Particulars",
        "debit": "Dr",
        "credit": "Cr",
        "balance": "Bal",
    },
    "KOTAK": {
        "date": "Date",
        "description": "Description",
        "debit": "Debit",
        "credit": "Credit",
        "balance": "Balance",
    },
    "IDFC": {
        "date": "Value Date",
        "description": "Narration",
        "debit": "Withdrawal",
        "credit": "Deposit",
        "balance": "Running Balance",
    },
}

def detect_bank(columns: list[str]) -> str:
    """Detect which bank's format this CSV is by checking column names."""
    cols_lower = [c.lower().strip() for c in columns]
    for bank, mapping in BANK_COLUMN_MAPS.items():
        required = [mapping["date"].lower(), mapping["description"].lower()]
        if all(r in cols_lower for r in required):
            return bank
    return "GENERIC"

def parse_amount(value) -> float:
    """Safely parse Indian currency strings like '1,45,000.50' → 145000.50"""
    if pd.isna(value) or value == "" or value == "-":
        return 0.0
    clean = str(value).replace(",", "").replace("₹", "").replace(" ", "").strip()
    try:
        return abs(float(clean))
    except ValueError:
        return 0.0

def parse_date(value: str) -> str:
    """Try multiple Indian date formats and return YYYY-MM-DD."""
    formats = ["%d/%m/%Y", "%d-%m-%Y", "%d-%b-%Y", "%d %b %Y",
               "%Y-%m-%d", "%d/%m/%y", "%d-%m-%y"]
    for fmt in formats:
        try:
            return datetime.strptime(str(value).strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return str(value)

def parse_csv(file_bytes: bytes) -> list[dict]:
    """Parse CSV bank statement into standardized transaction list."""
    try:
        df = pd.read_csv(BytesIO(file_bytes), encoding="utf-8", on_bad_lines="skip")
    except UnicodeDecodeError:
        df = pd.read_csv(BytesIO(file_bytes), encoding="latin-1", on_bad_lines="skip")

    # Strip whitespace from column names
    df.columns = [c.strip() for c in df.columns]
    bank = detect_bank(list(df.columns))

    if bank == "GENERIC":
        # Best-effort: look for columns containing "date", "amount", "description"
        col_map = {}
        for col in df.columns:
            col_lower = col.lower()
            if "date" in col_lower and "date" not in col_map:
                col_map["date"] = col
            if any(w in col_lower for w in ["narration", "description", "remark", "particular"]):
                col_map["description"] = col
            if any(w in col_lower for w in ["debit", "withdrawal", "dr", "amount"]):
                col_map["debit"] = col
            if any(w in col_lower for w in ["credit", "deposit", "cr"]):
                col_map["credit"] = col
    else:
        col_map = BANK_COLUMN_MAPS[bank]

    transactions = []
    for _, row in df.iterrows():
        try:
            debit = parse_amount(row.get(col_map.get("debit", ""), 0))
            credit = parse_amount(row.get(col_map.get("credit", ""), 0))
            description = str(row.get(col_map.get("description", ""), "")).strip()

            if not description or (debit == 0 and credit == 0):
                continue

            transactions.append({
                "date": parse_date(row.get(col_map.get("date", ""), "")),
                "raw_description": description,
                "merchant": extract_merchant_name(description),
                "amount": debit if debit > 0 else credit,
                "type": "debit" if debit > 0 else "credit",
            })
        except Exception:
            continue

    return transactions

def parse_pdf(file_bytes: bytes) -> list[dict]:
    """Extract transactions from PDF bank statement using PyMuPDF."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    all_text = ""
    for page in doc:
        all_text += page.get_text()

    transactions = []
    # Pattern: date | description | amount
    # Handles: DD/MM/YYYY or DD-MM-YYYY followed by text and a number
    pattern = re.compile(
        r"(\d{2}[\/\-]\d{2}[\/\-]\d{2,4})"   # date
        r"\s+(.+?)"                             # description
        r"\s+([\d,]+\.?\d*)\s*$",              # amount
        re.MULTILINE
    )
    for match in pattern.finditer(all_text):
        date_str, description, amount_str = match.groups()
        description = description.strip()
        amount = parse_amount(amount_str)
        if amount > 0 and description:
            transactions.append({
                "date": parse_date(date_str),
                "raw_description": description,
                "merchant": extract_merchant_name(description),
                "amount": amount,
                "type": "debit",  # PDF rarely distinguishes — mark all debit
            })

    return transactions

def extract_merchant_name(description: str) -> str:
    """Clean UPI/NEFT/IMPS prefixes to get human-readable merchant name."""
    # Remove common bank prefixes
    prefixes = [
        r"UPI[-/]", r"NEFT[-/]", r"IMPS[-/]", r"ACH[-/]", r"NACH[-/]",
        r"POS[-/]", r"ATM[-/]", r"BIL[-/]BILL[-/]", r"MMT[-/]",
        r"P2A[-/]", r"P2M[-/]", r"AP[-/]",
    ]
    merchant = description.upper()
    for prefix in prefixes:
        merchant = re.sub(prefix, "", merchant, flags=re.IGNORECASE)

    # Take first meaningful segment (before phone numbers, account numbers)
    parts = re.split(r"[-@/|]", merchant)
    clean = parts[0].strip().title() if parts else merchant

    # Remove trailing digits (account/ref numbers)
    clean = re.sub(r"\s+\d{6,}$", "", clean).strip()
    return clean or description[:40]
```

### 9.4 Anomaly Detector
```python
# ml-engine/services/anomaly_detector.py
import numpy as np
from sklearn.ensemble import IsolationForest
from collections import defaultdict

def detect_anomalies(transactions: list[dict]) -> list[dict]:
    """
    Flag transactions with unusual amounts per category.
    Returns transactions list with is_anomaly and anomaly_reason fields added.
    """
    if len(transactions) < 5:
        return transactions  # Not enough data to detect anomalies

    # Group by category and detect per-category anomalies
    by_category = defaultdict(list)
    for i, t in enumerate(transactions):
        by_category[t["category"]].append((i, t["amount"]))

    anomaly_indices = set()
    reasons = {}

    for category, items in by_category.items():
        if len(items) < 3:
            continue  # Need at least 3 data points
        amounts = np.array([a for _, a in items]).reshape(-1, 1)
        detector = IsolationForest(contamination=0.1, random_state=42)
        preds = detector.fit_predict(amounts)
        median_amount = float(np.median(amounts))

        for (idx, amount), pred in zip(items, preds):
            if pred == -1:
                multiple = round(amount / median_amount, 1) if median_amount > 0 else 0
                anomaly_indices.add(idx)
                reasons[idx] = (
                    f"Amount ₹{amount:,.0f} is {multiple}x above your "
                    f"usual {category} spending (₹{median_amount:,.0f})"
                )

    for i, t in enumerate(transactions):
        t["is_anomaly"] = i in anomaly_indices
        t["anomaly_reason"] = reasons.get(i)

    return transactions
```

### 9.5 Insight Generator
```python
# ml-engine/services/insight_generator.py

HINDI_TRANSLATIONS = {
    "Food": "खाना",
    "Transport": "यातायात",
    "Groceries": "किराना",
    "Rent": "किराया",
    "EMI": "ईएमआई",
    "Shopping": "खरीदारी",
    "Investments": "निवेश",
    "Other": "अन्य",
}

def generate_insights(summary: dict, language: str = "en") -> list[dict]:
    """Generate 3-5 plain language insights from spending summary."""
    insights = []
    by_cat = summary.get("by_category", {})
    total = summary.get("total_debit", 0)
    if total == 0:
        return []

    # Sort categories by amount
    sorted_cats = sorted(by_cat.items(), key=lambda x: x[1]["amount"], reverse=True)

    for category, data in sorted_cats[:3]:
        pct = data["percentage"]
        amount = data["amount"]
        count = data["transaction_count"]

        if category == "Food" and pct > 30:
            en_body = (
                f"You spent ₹{amount:,.0f} on food this month ({pct:.0f}% of total). "
                f"That's across {count} transactions. Consider meal prepping to cut this by 20%."
            )
            hi_body = (
                f"इस महीने आपने खाने पर ₹{amount:,.0f} खर्च किए (कुल का {pct:.0f}%)। "
                f"यह {count} लेनदेन में था। घर पर खाना बनाने से 20% बचत हो सकती है।"
            )
            insights.append({
                "type": "overspend",
                "category": category,
                "title_en": "Food spending is high",
                "body_en": en_body,
                "title_hi": "खाने पर ज़्यादा खर्च",
                "body_hi": hi_body,
                "severity": "warning",
            })

        elif category == "Investments" and pct >= 10:
            en_body = (
                f"You invested ₹{amount:,.0f} this month ({pct:.0f}% of income). "
                f"That's above the recommended 10% — excellent financial habit."
            )
            hi_body = (
                f"इस महीने आपने ₹{amount:,.0f} निवेश किए ({pct:.0f}%)। "
                f"यह अनुशंसित 10% से अधिक है — बहुत अच्छी आदत।"
            )
            insights.append({
                "type": "positive",
                "category": category,
                "title_en": "Great savings habit",
                "body_en": en_body,
                "title_hi": "बेहतरीन बचत की आदत",
                "body_hi": hi_body,
                "severity": "success",
            })

        elif category == "Transport" and pct > 15:
            en_body = (
                f"Transport costs are ₹{amount:,.0f} ({pct:.0f}%). "
                f"Consider monthly metro/bus pass or carpooling to reduce this."
            )
            hi_body = (
                f"यातायात पर ₹{amount:,.0f} ({pct:.0f}%) खर्च हुए। "
                f"मेट्रो पास या कारपूल से खर्च कम हो सकता है।"
            )
            insights.append({
                "type": "suggestion",
                "category": category,
                "title_en": "High transport costs",
                "body_en": en_body,
                "title_hi": "यातायात पर ज़्यादा खर्च",
                "body_hi": hi_body,
                "severity": "warning",
            })

    # Add anomaly insight if anomalies detected
    anomalies = summary.get("anomalies", [])
    if anomalies:
        a = anomalies[0]
        insights.append({
            "type": "anomaly",
            "category": a.get("category", "Other"),
            "title_en": "Unusual transaction detected",
            "body_en": f"Your {a['merchant']} payment of ₹{a['amount']:,.0f} is unusually high. {a['reason']}",
            "title_hi": "असामान्य लेनदेन मिला",
            "body_hi": f"₹{a['amount']:,.0f} का {a['merchant']} भुगतान असामान्य रूप से अधिक है।",
            "severity": "error",
        })

    # Return based on requested language
    return [
        {
            "type": i["type"],
            "category": i["category"],
            "title": i[f"title_{language}"] or i["title_en"],
            "body": i[f"body_{language}"] or i["body_en"],
            "severity": i["severity"],
        }
        for i in insights
    ]
```

---

## SECTION 10: FRONTEND — KEY FILES

### 10.1 TypeScript interfaces
```typescript
// frontend/types/index.ts
export interface Transaction {
  id: string
  date: string
  merchant: string
  rawDescription: string
  amount: number
  type: "debit" | "credit"
  category: Category
  confidence: number
  isAnomaly: boolean
  anomalyReason?: string
  manuallyUpdated: boolean
}

export type Category =
  | "Food" | "Transport" | "Groceries" | "Rent"
  | "EMI" | "Shopping" | "Investments" | "Other"

export interface CategoryStats {
  amount: number
  percentage: number
  transactionCount: number
}

export interface UploadResponse {
  statementId: string
  filename: string
  bankDetected: string
  totalTransactions: number
  transactions: Transaction[]
  summary: {
    totalDebit: number
    totalCredit: number
    byCategory: Record<Category, CategoryStats>
    anomalies: AnomalyAlert[]
    dailySpending: { date: string; amount: number }[]
  }
}

export interface AnomalyAlert {
  transactionId: string
  merchant: string
  amount: number
  reason: string
}

export interface Insight {
  type: "overspend" | "positive" | "suggestion" | "anomaly"
  category: Category
  title: string
  body: string
  severity: "success" | "warning" | "error" | "info"
}
```

### 10.2 Indian currency formatter
```typescript
// frontend/lib/formatters.ts
export function formatINR(amount: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount)
  // Output: ₹1,23,456
}

export function formatINRCompact(amount: number): string {
  if (amount >= 100000) return `₹${(amount / 100000).toFixed(1)}L`
  if (amount >= 1000) return `₹${(amount / 1000).toFixed(1)}K`
  return `₹${amount.toFixed(0)}`
}

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("en-IN", {
    day: "numeric", month: "short", year: "numeric",
  })
}
```

### 10.3 API client
```typescript
// frontend/lib/api.ts
import axios from "axios"

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  timeout: 30000,
})

export const uploadStatement = async (file: File) => {
  const form = new FormData()
  form.append("file", file)
  const { data } = await api.post("/api/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  })
  return data
}

export const getStats = async (statementId: string, period = "monthly") => {
  const { data } = await api.get("/api/stats", {
    params: { statement_id: statementId, period },
  })
  return data
}

export const getInsights = async (statementId: string, language = "en") => {
  const { data } = await api.get("/api/insights", {
    params: { statement_id: statementId, language },
  })
  return data
}

export const getTransactions = async (
  statementId: string,
  { category, search, page = 1, limit = 20 }: {
    category?: string; search?: string; page?: number; limit?: number
  } = {}
) => {
  const { data } = await api.get("/api/transactions", {
    params: { statement_id: statementId, category, search, page, limit },
  })
  return data
}

export const recategorize = async (transactionId: string, category: string) => {
  const { data } = await api.patch(`/api/transactions/${transactionId}/category`, {
    category,
  })
  return data
}

export const loadDemo = async () => {
  const { data } = await api.post("/api/demo")
  return data
}
```

### 10.4 Category color and icon map
```typescript
// frontend/lib/categories.ts
import {
  UtensilsCrossed, Car, ShoppingCart, Home,
  CreditCard, ShoppingBag, TrendingUp, MoreHorizontal,
} from "lucide-react"
import type { Category } from "@/types"

export const CATEGORY_CONFIG: Record<Category, {
  color: string
  bgClass: string
  textClass: string
  Icon: React.ElementType
}> = {
  Food:        { color: "#F59E0B", bgClass: "bg-amber-100",   textClass: "text-amber-800",  Icon: UtensilsCrossed },
  Transport:   { color: "#3B82F6", bgClass: "bg-blue-100",    textClass: "text-blue-800",   Icon: Car },
  Groceries:   { color: "#10B981", bgClass: "bg-emerald-100", textClass: "text-emerald-800",Icon: ShoppingCart },
  Rent:        { color: "#8B5CF6", bgClass: "bg-violet-100",  textClass: "text-violet-800", Icon: Home },
  EMI:         { color: "#EF4444", bgClass: "bg-red-100",     textClass: "text-red-800",    Icon: CreditCard },
  Shopping:    { color: "#EC4899", bgClass: "bg-pink-100",    textClass: "text-pink-800",   Icon: ShoppingBag },
  Investments: { color: "#06B6D4", bgClass: "bg-cyan-100",    textClass: "text-cyan-800",   Icon: TrendingUp },
  Other:       { color: "#64748B", bgClass: "bg-slate-100",   textClass: "text-slate-800",  Icon: MoreHorizontal },
}
```

### 10.5 Demo mock data
```json
// frontend/public/demo-data.json
{
  "statementId": "demo-00000000-0000-0000-0000-000000000000",
  "filename": "demo_statement_jan_2024.csv",
  "bankDetected": "HDFC",
  "totalTransactions": 50,
  "summary": {
    "totalDebit": 42850,
    "totalCredit": 75000,
    "byCatgory": {
      "Food":        { "amount": 8400,  "percentage": 19.6, "transactionCount": 34 },
      "Transport":   { "amount": 3200,  "percentage": 7.5,  "transactionCount": 14 },
      "Groceries":   { "amount": 4500,  "percentage": 10.5, "transactionCount": 8  },
      "Rent":        { "amount": 12000, "percentage": 28.0, "transactionCount": 1  },
      "EMI":         { "amount": 5000,  "percentage": 11.7, "transactionCount": 2  },
      "Shopping":    { "amount": 4750,  "percentage": 11.1, "transactionCount": 6  },
      "Investments": { "amount": 4000,  "percentage": 9.3,  "transactionCount": 2  },
      "Other":       { "amount": 1000,  "percentage": 2.3,  "transactionCount": 5  }
    },
    "anomalies": [
      {
        "transactionId": "demo-anom-001",
        "merchant": "Amazon",
        "amount": 8999,
        "reason": "3.2x above your usual Amazon spending of ₹2,800"
      }
    ]
  }
}
```

---

## SECTION 11: CODEX PROMPTS — COPY AND PASTE

Use these in order. Each prompt builds on the previous.

### Phase 1: Backend (Hours 0–6)

```
Prompt 1 — Scaffold backend:
"Read AGENTS.md. Create the /ml-engine directory with:
- main.py: FastAPI app with CORS for http://localhost:3000, /health route
- requirements.txt with all dependencies
- Empty routers/, services/, db/, data/, models/ folders
- Each folder should have an __init__.py
Run the server and confirm /health returns 200."

Prompt 2 — Database:
"Create ml-engine/db/database.py with async SQLAlchemy engine using
DATABASE_URL from environment. Create models.py with Statement,
Transaction, Category, Insight tables exactly as shown in the
Database Schema section of the documentation. Run Alembic migrations."

Prompt 3 — ML categorizer:
"Create ml-engine/services/categorizer.py using the exact code from
Section 9.2 of the documentation. Also copy ml-engine/data/training_data.py
from Section 9.1. Train the model and save to ml-engine/models/categorizer.pkl.
Print the training accuracy."

Prompt 4 — File parser:
"Create ml-engine/services/file_parser.py using the exact code from
Section 9.3. Test it against two edge cases:
1. A CSV with HDFC column names
2. A PDF with a date-description-amount pattern
Print 3 sample parsed rows from each."

Prompt 5 — Anomaly detector:
"Create ml-engine/services/anomaly_detector.py using Section 9.4.
Test it with a list of 20 transactions where 2 have amounts 5x
the usual — confirm those 2 are flagged as anomalies."

Prompt 6 — Upload endpoint:
"Create ml-engine/routers/upload.py with POST /api/upload.
The endpoint should: accept a file, detect CSV or PDF,
parse it, run the categorizer, run anomaly detection, save to DB,
return the full response shape from Section 7.2 of the documentation.
Include error handling for unsupported formats and empty files."

Prompt 7 — Stats + Insights endpoints:
"Create ml-engine/routers/stats.py with GET /api/stats
and ml-engine/routers/insights.py with GET /api/insights.
Use the exact response shapes from Section 7.3 and 7.4.
Create the insight_generator from Section 9.5.
Wire everything to main.py."

Prompt 8 — Transactions + Demo endpoints:
"Create ml-engine/routers/transactions.py with GET /api/transactions
and PATCH /api/transactions/{id}/category.
Also create POST /api/demo that inserts the 50 mock transactions
from demo-data.json into the database and returns the statement_id."

Prompt 9 — Test everything:
"Create scripts/test_api.sh with curl commands to test all 7 endpoints.
Run it and confirm every endpoint returns 200 with expected response shape."
```

### Phase 2: Frontend (Hours 6–14)

```
Prompt 10 — Frontend scaffold:
"Read AGENTS.md. In /frontend, set up Next.js 14 with App Router,
Tailwind, Recharts, Lucide React. Create the exact file structure
from Section 5. Install all dependencies. Confirm npm run dev works."

Prompt 11 — Types and utilities:
"Create frontend/types/index.ts, frontend/lib/api.ts,
frontend/lib/formatters.ts, and frontend/lib/categories.ts
using the exact code from Section 10.1–10.4. No modifications."

Prompt 12 — Upload page:
"Create frontend/app/upload/page.tsx with a drag-and-drop upload zone.
On file drop or select: call uploadStatement() from api.ts,
show a progress spinner with status text ('Scanning statement...',
'Categorizing transactions...', 'Building your dashboard...'),
then redirect to /dashboard?statement_id=[returned ID].
If demo button is clicked, call loadDemo() and redirect.
Style using the color palette from AGENTS.md."

Prompt 13 — Dashboard charts:
"Create frontend/app/dashboard/page.tsx.
Read statement_id from URL params. Fetch stats via getStats().
Show: 3 summary cards (Total Debit, Total Credit, Net Savings),
a Recharts ResponsiveContainer donut chart for spending by category,
a Recharts bar chart for daily spending over time.
Use exact hex colors from AGENTS.md category config.
Show loading skeleton while fetching."

Prompt 14 — Transaction table:
"Create frontend/components/TransactionTable.tsx.
Show columns: Date, Merchant, Category (colored badge), Amount, Type.
Add search input that filters by merchant name.
Add category filter dropdown.
Highlight anomalous rows with bg-red-50.
Add a 'Change category' button per row that opens a small inline
dropdown to re-categorize (calls recategorize() from api.ts)."

Prompt 15 — Insights page:
"Create frontend/app/insights/page.tsx.
Fetch insights via getInsights().
Add a language toggle button (EN / हिंदी) in the top right.
When Hindi is selected, re-fetch with language=hi.
Render each insight as an InsightCard with the correct severity color,
Lucide icon, title, and body text.
Show anomaly alerts separately at the top."

Prompt 16 — Empty state + nav:
"Create frontend/components/EmptyState.tsx with a friendly message
and 'Upload your first statement' button.
Create frontend/components/Navbar.tsx with logo, nav links
(Dashboard, Upload, Insights), and language toggle.
Wrap app/layout.tsx with the Navbar."
```

### Phase 3: Polish and Deploy (Hours 14–18)

```
Prompt 17 — Error handling:
"Add comprehensive error handling:
- Frontend: show toast notifications (use Sonner or a simple div)
  for upload errors, network errors, and parse failures.
- Backend: ensure all endpoints return helpful error messages
  matching the schema in Section 7.2.
Test by uploading a .txt file and a corrupt PDF."

Prompt 18 — Deploy config:
"Create:
- vercel.json for Next.js frontend deployment
- ml-engine/Dockerfile for Railway Python deployment
- .env.example with all keys from Section 6 (empty values)
- README.md with: what this is, how to run locally, how to deploy
Update NEXT_PUBLIC_API_URL to accept an environment variable.
Test that npm run build completes without errors."

Prompt 19 — Final test:
"Run the complete application end-to-end:
1. Start backend on port 8000
2. Start frontend on port 3000
3. Click Load Demo on the upload page
4. Confirm dashboard shows charts
5. Confirm insights page shows 3+ insights
6. Confirm re-categorize works
7. Confirm Hindi toggle works
Fix any bugs found."
```

---

## SECTION 12: USER FLOW (MVP SCOPE)

### Flow 1: New user with CSV
1. Land on `/upload` page → see drag-and-drop zone + "Load Demo" button
2. Drop HDFC CSV file → progress bar shows three stages
3. Redirect to `/dashboard?statement_id=xxx`
4. See: total spent, net savings, donut chart, daily bar chart
5. Scroll down: transaction table with categories and amounts
6. Click "Insights" tab → see 3 plain-language insights
7. Toggle to Hindi → insights re-render in Hindi
8. Find a miscategorized row → click "Change" → select correct category

### Flow 2: New user with PDF
1. Same as above but upload PDF
2. If PDF extraction fails (scanned image, complex layout):
   - Show error: "Could not read this PDF. Please export as CSV from your bank app."
   - Provide link to instructions for HDFC/SBI/ICICI CSV export

### Flow 3: Demo (hackathon judges)
1. Click "Load Demo Data" on upload page
2. Instantly redirect to dashboard with 50 pre-loaded transactions
3. Full experience with anomalies, insights, charts, Hindi toggle

### Screens (4 total)
| Screen | Route | Purpose |
|--------|-------|---------|
| Upload | `/upload` | File upload + demo button |
| Dashboard | `/dashboard` | Charts and transaction table |
| Insights | `/insights` | Plain-language spending analysis |
| Not Found | `/404` | Friendly error page |

---

## SECTION 13: STYLING GUIDELINES

### 13.1 Design philosophy
Utility-first. Clarity, speed, trust. No gradients, no particles,
no decorative backgrounds. Every element earns its place.

### 13.2 Color tokens (exact hex — use in tailwind.config.js)
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        "ft-navy":   "#1E293B",  // headers, nav
        "ft-bg":     "#F8FAFC",  // page background
        "ft-success":"#10B981",  // income, savings
        "ft-warning":"#F59E0B",  // overspend alerts
        "ft-error":  "#EF4444",  // anomalies, danger
        "ft-neutral":"#64748B",  // secondary text
      },
    },
  },
}
```

### 13.3 Typography
```css
/* globals.css — add to your Next.js project */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

body { font-family: 'Inter', sans-serif; }

/* Scale */
/* H1: text-3xl font-semibold (32px) */
/* H2: text-2xl font-medium  (24px) */
/* Body: text-base font-normal (16px) */
/* Meta: text-sm             (14px) */
```

### 13.4 Component standards
```
Cards:     bg-white rounded-lg shadow-sm p-6 border border-gray-100
Buttons:   bg-ft-navy text-white rounded-md px-4 py-2 font-medium hover:bg-slate-700
Inputs:    border border-gray-200 rounded-md px-3 py-2 focus:ring-2 focus:ring-ft-navy
Badges:    inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium
Table rows: border-b border-gray-100 py-3
Anomaly:   bg-red-50 border-l-4 border-ft-error
```

### 13.5 Category visual treatment
Each category uses its own color consistently across all charts,
badges, and icons. Use the CATEGORY_CONFIG object from Section 10.4.
Never use category colors outside their assigned category.

### 13.6 Number formatting
Always use the `formatINR()` function from `lib/formatters.ts`.
- ₹45,230 — not ₹45230 or Rs 45,230
- ₹1,23,456 — not ₹123,456 (Indian numbering system)
- ₹2.3L — compact format for cards

---

## SECTION 14: DEPLOYMENT CHECKLIST

### Before first deploy
- [ ] `.env` is in `.gitignore`
- [ ] `.env.example` is committed with empty values
- [ ] `npm run build` passes without errors
- [ ] `python -m pytest` passes (if tests added)
- [ ] All API endpoints tested via `scripts/test_api.sh`
- [ ] Demo mode works end-to-end
- [ ] Hindi toggle works
- [ ] Error states tested (bad file, network down)

### Frontend → Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod

# Set env vars in Vercel dashboard:
# NEXT_PUBLIC_API_URL = https://your-backend.railway.app
```

### Backend → Railway
```bash
# In ml-engine/ folder, Railway auto-detects Dockerfile or requirements.txt
# Set env vars in Railway dashboard:
# DATABASE_URL = your supabase connection string
# SECRET_KEY = random 32 char string
# DEBUG = False
# ALLOWED_ORIGINS = https://your-frontend.vercel.app
```

### Database → Supabase
```bash
# 1. Create project at supabase.com
# 2. Go to SQL Editor
# 3. Paste and run the CREATE TABLE statements from Section 8.1
# 4. Copy connection string to DATABASE_URL
```

---

## SECTION 15: KNOWN LIMITATIONS (DOCUMENT FOR JUDGES)

| Limitation | Reason | Phase 2 Fix |
|------------|--------|-------------|
| No user login | Hackathon time constraint | Add Supabase Auth |
| No image/OCR | Tesseract unreliable on bank PDFs | Add unstructured.io |
| Hindi translations are static strings | No live translation API | Add DeepL or Google Translate |
| ML trained on 150 examples | Limited training data | Collect real user corrections |
| No budget goal setting | Not in MVP scope | Add budget_goals table |
| Single user per session | No auth isolation | Add user_id to all queries |
| PDF parsing may fail on complex PDFs | Regex-based extraction | Add LLM-based PDF parsing |

---

## SECTION 16: QUICK REFERENCE CARD

```
┌─────────────────────────────────────────────────────────────────┐
│  FINANCE TRACKER — QUICK REFERENCE                             │
├─────────────────────────────────────────────────────────────────┤
│  Start backend:  cd ml-engine && uvicorn main:app --reload      │
│  Start frontend: cd frontend && npm run dev                     │
│  Train model:    cd ml-engine && python scripts/train_model.py  │
│  Test APIs:      bash scripts/test_api.sh                       │
│  Seed DB:        cd ml-engine && python scripts/seed_db.py      │
├─────────────────────────────────────────────────────────────────┤
│  Backend:   http://localhost:8000                               │
│  API docs:  http://localhost:8000/docs  (FastAPI auto-gen)      │
│  Frontend:  http://localhost:3000                               │
├─────────────────────────────────────────────────────────────────┤
│  Key endpoints:                                                 │
│    POST /api/upload          → parse + categorize statement     │
│    GET  /api/stats           → category totals + daily chart    │
│    GET  /api/insights        → plain language insights          │
│    GET  /api/transactions    → paginated transaction list       │
│    PATCH /api/transactions/{id}/category → re-categorize        │
│    POST /api/demo            → load 50 mock transactions        │
│    GET  /health              → check if server is up            │
├─────────────────────────────────────────────────────────────────┤
│  8 Categories: Food | Transport | Groceries | Rent              │
│                EMI  | Shopping  | Investments | Other           │
├─────────────────────────────────────────────────────────────────┤
│  Supported banks: HDFC, SBI, ICICI, AXIS, KOTAK, IDFC         │
│  Supported files: .csv .pdf (max 10MB)                         │
│  Languages:       English (en), Hindi (hi)                     │
└─────────────────────────────────────────────────────────────────┘
```

---

*End of documentation. This file is the single source of truth.*
*When in doubt, re-read AGENTS.md (Section 1) before prompting Codex.*
