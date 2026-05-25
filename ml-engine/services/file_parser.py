# ml-engine/services/file_parser.py
import re
from datetime import datetime
from io import BytesIO, StringIO

import fitz  # PyMuPDF
import pandas as pd

# ─────────────────────────────────────────────────────────────────────────────
# BANK COLUMN MAPS (unchanged from original)
# ─────────────────────────────────────────────────────────────────────────────

BANK_COLUMN_MAPS = {
    "HDFC": {
        "date": ["date"],
        "description": ["narration", "description", "remarks", "remark", "particular"],
        "debit": ["withdrawal", "debit", "dr"],
        "credit": ["deposit", "credit", "cr"],
    },
    "SBI": {
        "date": ["txn date", "transaction date", "date"],
        "description": ["description", "narration", "remarks"],
        "debit": ["debit", "withdrawal", "dr"],
        "credit": ["credit", "deposit", "cr"],
    },
    "ICICI": {
        "date": ["transaction date", "value date", "date"],
        "description": ["transaction remarks", "remarks", "description", "narration"],
        "debit": ["debit amount", "debit", "withdrawal"],
        "credit": ["credit amount", "credit", "deposit"],
    },
    "AXIS": {
        "date": ["tran date", "transaction date", "date"],
        "description": ["particulars", "description", "narration"],
        "debit": ["dr", "debit", "withdrawal"],
        "credit": ["cr", "credit", "deposit"],
    },
    "KOTAK": {
        "date": ["date", "transaction date"],
        "description": ["description", "narration", "remarks"],
        "debit": ["debit", "withdrawal", "dr"],
        "credit": ["credit", "deposit", "cr"],
    },
    "IDFC": {
        "date": ["value date", "transaction date", "date"],
        "description": ["narration", "description", "remarks"],
        "debit": ["withdrawal", "debit", "dr"],
        "credit": ["deposit", "credit", "cr"],
    },
}

GENERIC_COLUMN_HINTS = {
    "date": ["date", "txn", "posting", "value date"],
    "description": [
        "narration", "description", "remark", "particular",
        "details", "transaction details", "payee", "merchant",
    ],
    "debit": ["withdrawal", "debit", "dr", "paid", "payment"],
    "credit": ["deposit", "credit", "cr", "received"],
    "amount": ["amount", "amt", "transaction amount"],
    "type": ["dr/cr", "dr / cr", "type", "debit/credit", "cr/dr"],
}

DATE_PATTERN = re.compile(
    r"\b(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}|\d{1,2}[-\s][A-Za-z]{3}[-\s]\d{2,4})\b"
)
DATE_LINE_PATTERN = re.compile(r"^\d{1,2}-\d{1,2}-\d{4}$")
DATE_LINE_PATTERN_SLASH = re.compile(r"^\d{1,2}/\d{1,2}/\d{4}$")
AMOUNT_LINE_PATTERN = re.compile(r"^[\d,]+\.\d{2}$")
SR_NO_LINE_PATTERN = re.compile(r"^\d{1,4}$")
STATEMENT_TABLE_HEADERS = ["Sr No", "Date", "Remarks", "Debit", "Credit", "Balance"]
AMOUNT_PATTERN = re.compile(r"[\d,]+\.\d{2}|\b[\d,]+\b")

SKIP_LINE_KEYWORDS = frozenset({
    "sr no", "date", "remarks", "debit", "credit", "balance",
    "transaction date", "detailed statement", "account holder",
    "customer id", "ifsc", "branch name", "transaction type",
    "account number", "account holder name", "account holder address",
})


# ─────────────────────────────────────────────────────────────────────────────
# ① FORMAT DETECTION  (NEW)
# ─────────────────────────────────────────────────────────────────────────────

def _detect_pdf_source(first_page_text: str) -> str:
    """
    Inspect the first page of a PDF and return which app/bank produced it.
    Returns one of: 'GPAY' | 'PHONEPE' | 'PAYTM' | 'UNION' | 'BANK_GENERIC'
    """
    t = first_page_text.lower()

    # Google Pay — exact header from your real PDF
    if "google pay" in t and (
        "transaction statement" in t or "paid to" in t or "received from" in t
    ):
        return "GPAY"

    # PhonePe — their PDF always starts with "PhonePe" and uses "Debited" / "Credited"
    if "phonepe" in t or ("phone pe" in t and "utr" in t):
        return "PHONEPE"

    # Paytm
    if "paytm" in t and ("transaction history" in t or "wallet" in t):
        return "PAYTM"

    # Union Bank — from your other real PDF
    if "union bank" in t or "ubin" in t:
        return "UNION"

    return "BANK_GENERIC"


# ─────────────────────────────────────────────────────────────────────────────
# ② GOOGLE PAY PARSER  (NEW — based on your real gpay PDF)
# ─────────────────────────────────────────────────────────────────────────────

# Matches: "10 Apr, 2026"  or  "10 Apr 2026"
_GPAY_DATE_RE = re.compile(
    r"(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[,\s]+\d{4})",
    re.IGNORECASE,
)
_GPAY_TIME_RE = re.compile(r"(\d{1,2}:\d{2}\s*[AP]M)", re.IGNORECASE)
_GPAY_AMOUNT_RE = re.compile(r"₹\s*([\d,]+(?:\.\d{1,2})?)")
_GPAY_TXN_ID_RE = re.compile(r"UPI\s+Transaction\s+ID[:\s]+(\d+)", re.IGNORECASE)

# Merchant keywords for categorizing clean GPay names
_GPAY_CATEGORY_RULES = {
    "Food": [
        "swiggy", "zomato", "dominos", "mcdonald", "kfc", "burger king",
        "pizza", "starbucks", "cafe", "restaurant", "biryani", "dhaba",
        "kitchen", "food", "tiffin", "canteen", "blinkit", "zepto",
        "instamart", "dunzo", "bakery", "sweet", "juice", "chai",
        "snack", "eatsure", "box8", "faasos", "freshmenu",
    ],
    "Shopping": [
        "apparel", "apparels", "garment", "garments", "readymade",
        "fashion", "boutique", "saree", "textile", "cloth",
        "amazon", "flipkart", "myntra", "ajio", "meesho", "nykaa",
        "mart", "bazaar", "bazar", "electronics", "mobile", "hardware",
        "furniture", "decor",
    ],
    "Education": [
        "pustak", "bhandar", "book", "library", "school", "college",
        "university", "tuition", "coaching", "academy", "institute",
        "education", "study", "stationery",
    ],
    "Transport": [
        "ola", "uber", "rapido", "metro", "railway", "irctc",
        "petrol", "fuel", "fastag", "parking", "cab", "taxi", "travel",
        "indigo", "spicejet", "air india", "redbus",
    ],
    "Utilities": [
        "electric", "electricity", "power", "water", "gas", "internet",
        "broadband", "airtel", "jio", "bsnl", "vi telecom", "recharge", "bill",
    ],
    "Other": [
        "pan", "aadhar", "aadhaar", "service center", "government",
        "municipal", "hospital", "clinic", "doctor", "medical",
        "pharmacy", "health", "tax",
    ],
}

_GPAY_PERSON_SUFFIXES = re.compile(
    r"\b(kumar|prasad|gupta|sharma|singh|yadav|patel|verma|ram|devi|"
    r"lal|das|chauhan|jha|mishra|tiwari|mahato|barnwal|srivastva|prajapati|"
    r"ahmad|ahmed|narayan|so |s\/o|d\/o|w\/o)\b",
    re.IGNORECASE,
)


def _gpay_categorize(name: str, direction: str) -> tuple[str, str]:
    """Return (category, cleaned_name) for a Google Pay transaction."""
    if direction == "credit":
        if "google pay reward" in name.lower() or "cashback" in name.lower():
            return "Income", "Google Pay Cashback"
        return "Income", name.title()

    name_lower = name.lower()

    for category, keywords in _GPAY_CATEGORY_RULES.items():
        if any(kw in name_lower for kw in keywords):
            return category, name.title()

    # Heuristic: names with person-surname patterns → P2P Transfer
    if _GPAY_PERSON_SUFFIXES.search(name):
        return "Transfer", name.title()

    # 2+ words with no business keyword → probably a person
    words = name.strip().split()
    if len(words) >= 2 and all(w.isalpha() for w in words[:2]):
        return "Transfer", name.title()

    return "Other", name.title()


def _parse_gpay_pdf(file_bytes: bytes) -> list[dict]:
    """
    Parse a Google Pay transaction statement PDF.

    Real format (verified against gpay_statement_20260201_20260430.pdf):

        Date & time          Transaction details                    Amount
        ─────────────────────────────────────────────────────────────────
        10 Apr, 2026         Paid to Abhinash Mahato               ₹500
        03:18 PM             UPI Transaction ID: 646690656657
                             Paid by Union Bank of India 7123

        10 Apr, 2026         Received from Google Pay rewards       ₹21
        03:18 PM             UPI Transaction ID: 372349901006
                             Paid to Union Bank of India 7123

    Strategy:
      1. Split full text on every GPay date ("10 Apr, 2026").
      2. Inside each block find: time, Paid-to/Received-from name,
         UPI Transaction ID, and ₹ amount.
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    full_text = "".join(page.get_text() for page in doc)
    doc.close()

    transactions: list[dict] = []

    # Split at every date occurrence — each slice is one transaction block
    segments = _GPAY_DATE_RE.split(full_text)
    # segments = [preamble, date1, block1, date2, block2, …]

    i = 1
    while i + 1 < len(segments):
        date_raw = segments[i].strip()
        block    = segments[i + 1]
        i += 2

        # ── time ──────────────────────────────────────────────────
        time_m = _GPAY_TIME_RE.search(block)
        time_str = time_m.group(1) if time_m else ""

        # ── direction + counterparty name ─────────────────────────
        paid_m = re.search(
            r"Paid\s+to\s+(.+?)(?:\n|UPI\s+Transaction)", block, re.IGNORECASE
        )
        recv_m = re.search(
            r"Received\s+from\s+(.+?)(?:\n|UPI\s+Transaction)", block, re.IGNORECASE
        )

        if paid_m:
            direction = "debit"
            raw_name  = paid_m.group(1).strip()
        elif recv_m:
            direction = "credit"
            raw_name  = recv_m.group(1).strip()
        else:
            continue  # not a transaction block

        # ── UPI transaction ID ────────────────────────────────────
        txn_m = _GPAY_TXN_ID_RE.search(block)
        upi_ref = txn_m.group(1) if txn_m else ""

        # ── amount (last ₹NNN in block is the transaction amount) ─
        amounts = _GPAY_AMOUNT_RE.findall(block)
        if not amounts:
            continue
        amount_str = amounts[-1].replace(",", "")
        try:
            amount = float(amount_str)
        except ValueError:
            continue
        if amount <= 0:
            continue

        # ── parse date ────────────────────────────────────────────
        std_date = _parse_gpay_date(date_raw)

        # ── categorize ───────────────────────────────────────────
        category, merchant = _gpay_categorize(raw_name, direction)

        transactions.append({
            "date":            std_date,
            "raw_description": f"{'Paid to' if direction == 'debit' else 'Received from'} {raw_name}",
            "merchant":        merchant,
            "amount":          amount,
            "type":            direction,
            "category":        category,
            "upi_ref":         upi_ref,
            "source":          "gpay",
        })

    return transactions


def _parse_gpay_date(raw: str) -> str:
    """Convert '10 Apr, 2026' → '2026-04-10'."""
    cleaned = raw.replace(",", "").strip()
    for fmt in ("%d %b %Y", "%d %B %Y"):
        try:
            return datetime.strptime(cleaned, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return cleaned


# ─────────────────────────────────────────────────────────────────────────────
# ③ PHONEPE PARSER  (NEW)
# ─────────────────────────────────────────────────────────────────────────────

# PhonePe exports two different PDF layouts depending on the app version:
#
# Layout A (older app):
#   DEBITED
#   Paid to Swiggy
#   Date: 10 Apr 2026, 03:18 PM
#   Amount: -₹450.00
#   UTR: 646652487595
#   Status: Completed
#
# Layout B (newer app / web export):
#   Apr 10, 2026 03:18 PM   Swiggy               -₹450.00   Completed
#                            UTR: 646652487595
#
# We handle both.

_PE_BLOCK_SPLIT = re.compile(
    r"(?:DEBITED|CREDITED|Sent|Received|Paid to|Received from)",
    re.IGNORECASE,
)
_PE_DATE_RE = re.compile(
    r"(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[,\s]+\d{4}"
    r"|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4})",
    re.IGNORECASE,
)
_PE_AMOUNT_RE = re.compile(r"[+\-]?₹\s*([\d,]+(?:\.\d{1,2})?)")
_PE_UTR_RE    = re.compile(r"UTR[:\s]+(\d+)", re.IGNORECASE)
_PE_STATUS_RE = re.compile(r"\b(Completed|Failed|Pending|Reversed)\b", re.IGNORECASE)

# PhonePe table layout B — tab/space separated
_PE_TABLE_ROW_RE = re.compile(
    r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4})"
    r"\s+(\d{1,2}:\d{2}\s*[AP]M)\s+"
    r"(.+?)\s+"
    r"([+\-]₹[\d,]+(?:\.\d{2})?)\s+"
    r"(Completed|Failed|Pending)",
    re.IGNORECASE,
)


def _parse_phonepe_pdf(file_bytes: bytes) -> list[dict]:
    """
    Parse a PhonePe transaction history PDF.

    Handles both Layout A (block-per-transaction) and
    Layout B (table row per transaction).
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    full_text = "".join(page.get_text() for page in doc)
    doc.close()

    # Try Layout B (table) first — faster and cleaner
    transactions = _parse_phonepe_table(full_text)
    if transactions:
        return transactions

    # Fall back to Layout A (block format)
    return _parse_phonepe_blocks(full_text)


def _parse_phonepe_table(text: str) -> list[dict]:
    """PhonePe Layout B: one transaction per table row."""
    transactions: list[dict] = []

    for match in _PE_TABLE_ROW_RE.finditer(text):
        date_raw, time_raw, name, amount_raw, status = match.groups()

        if status.lower() in ("failed", "reversed"):
            continue

        amount_str = amount_raw.replace("₹", "").replace(",", "").strip()
        direction  = "credit" if amount_str.startswith("+") else "debit"
        try:
            amount = abs(float(amount_str.lstrip("+-")))
        except ValueError:
            continue

        std_date = _parse_pe_date(date_raw)
        category, merchant = _gpay_categorize(name.strip(), direction)

        transactions.append({
            "date":            std_date,
            "raw_description": name.strip(),
            "merchant":        merchant,
            "amount":          amount,
            "type":            direction,
            "category":        category,
            "upi_ref":         "",
            "source":          "phonepe",
        })

    return transactions


def _parse_phonepe_blocks(text: str) -> list[dict]:
    """PhonePe Layout A: block of lines per transaction."""
    transactions: list[dict] = []

    # Typical block:
    #   DEBITED\nPaid to Swiggy\nDate: 10 Apr 2026, 03:18 PM\n
    #   Amount: -₹450.00\nUTR: 646652487595\nStatus: Completed

    # Split by the DEBITED / CREDITED header line
    blocks = re.split(r"\n(?=DEBITED|CREDITED)", text, flags=re.IGNORECASE)

    for block in blocks:
        if not block.strip():
            continue

        # Direction
        first_line = block.strip().split("\n")[0].upper()
        if "CREDIT" in first_line:
            direction = "credit"
        else:
            direction = "debit"

        # Counterparty name — line after DEBITED/CREDITED
        lines = [l.strip() for l in block.strip().split("\n") if l.strip()]
        name = ""
        for line in lines[1:3]:
            if re.match(r"(Paid to|Sent to|Received from)\s+.+", line, re.IGNORECASE):
                name = re.sub(r"^(Paid to|Sent to|Received from)\s+", "", line, flags=re.IGNORECASE)
                break
            if not re.search(r"(Date|Amount|UTR|Status|UPI)", line, re.IGNORECASE):
                name = line
                break

        # Date
        date_m = _PE_DATE_RE.search(block)
        std_date = _parse_pe_date(date_m.group(1)) if date_m else datetime.today().strftime("%Y-%m-%d")

        # Amount
        amount_m = _PE_AMOUNT_RE.search(block)
        if not amount_m:
            continue
        try:
            amount = abs(float(amount_m.group(1).replace(",", "")))
        except ValueError:
            continue
        if amount <= 0:
            continue

        # Skip failed / reversed
        status_m = _PE_STATUS_RE.search(block)
        if status_m and status_m.group(1).lower() in ("failed", "reversed"):
            continue

        # UTR
        utr_m = _PE_UTR_RE.search(block)
        utr = utr_m.group(1) if utr_m else ""

        category, merchant = _gpay_categorize(name or "Unknown", direction)

        transactions.append({
            "date":            std_date,
            "raw_description": f"{'Paid to' if direction == 'debit' else 'Received from'} {name}",
            "merchant":        merchant,
            "amount":          amount,
            "type":            direction,
            "category":        category,
            "upi_ref":         utr,
            "source":          "phonepe",
        })

    return transactions


def _parse_pe_date(raw: str) -> str:
    """Convert various PhonePe date strings → YYYY-MM-DD."""
    cleaned = raw.replace(",", "").strip()
    for fmt in ("%d %b %Y", "%b %d %Y", "%d %B %Y", "%B %d %Y"):
        try:
            return datetime.strptime(cleaned, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return cleaned


# ─────────────────────────────────────────────────────────────────────────────
# EVERYTHING BELOW IS YOUR ORIGINAL CODE — UNCHANGED
# ─────────────────────────────────────────────────────────────────────────────

def detect_bank(columns: list[str]) -> str:
    normalized = [_normalize_col_name(c) for c in columns]
    best_bank = "GENERIC"
    best_score = 0
    for bank, hints in BANK_COLUMN_MAPS.items():
        date_col  = _find_column(columns, hints["date"], normalized)
        desc_col  = _find_column(columns, hints["description"], normalized)
        debit_col = _find_column(columns, hints["debit"], normalized, allow_type_column=False)
        credit_col= _find_column(columns, hints["credit"], normalized, allow_type_column=False)
        if not date_col or not desc_col:
            continue
        if not debit_col and not credit_col:
            continue
        score = 3
        if score > best_score:
            best_score = score
            best_bank = bank
    return best_bank if best_score >= 3 else "GENERIC"


def _normalize_col_name(name: str) -> str:
    return re.sub(r"\s+", " ", str(name).strip().lower().replace("_", " "))


def _is_type_column(name: str) -> bool:
    lower = name.lower()
    return any(token in lower for token in ("dr/cr", "dr / cr", "debit/credit", "cr/dr", "type"))


def _find_column(
    columns: list[str],
    keywords: list[str],
    normalized: list[str] | None = None,
    allow_type_column: bool = True,
) -> str | None:
    normalized = normalized or [_normalize_col_name(c) for c in columns]
    for col, col_norm in zip(columns, normalized):
        if not allow_type_column and _is_type_column(col):
            continue
        if _is_balance_column(col):
            continue
        for keyword in keywords:
            kw = keyword.lower()
            if kw == col_norm or kw in col_norm:
                return col
    return None


def _build_column_map(columns: list[str], bank: str) -> dict[str, str | None]:
    hints = BANK_COLUMN_MAPS.get(bank) if bank != "GENERIC" else None
    generic = GENERIC_COLUMN_HINTS

    def pick(key: str, bank_keywords: list[str] | None) -> str | None:
        allow_type = key not in ("debit", "credit")
        if bank_keywords:
            found = _find_column(columns, bank_keywords, allow_type_column=allow_type)
            if found:
                return found
        return _find_column(columns, generic[key], allow_type_column=allow_type)

    col_map: dict[str, str | None] = {
        "date":        pick("date",   hints["date"]        if hints else None),
        "description": pick("description", hints["description"] if hints else None),
        "debit":       pick("debit",  hints["debit"]       if hints else None),
        "credit":      pick("credit", hints["credit"]      if hints else None),
        "amount":      pick("amount", None),
        "type":        _find_column(columns, generic["type"]),
    }
    if col_map["debit"] and col_map["debit"] == col_map["credit"]:
        col_map["debit"] = None
        col_map["credit"] = None
    for key in ("debit", "credit", "amount"):
        col = col_map.get(key)
        if col and _is_balance_column(col):
            col_map[key] = None
    return col_map


def _is_balance_column(name: str) -> bool:
    lower = name.lower()
    return "balance" in lower and "opening" not in lower


def parse_amount(value) -> float:
    if value is None or pd.isna(value) or value == "" or value == "-":
        return 0.0
    clean = str(value).replace(",", "").replace("₹", "").replace("Rs.", "").replace(" ", "").strip()
    clean = clean.replace("(", "-").replace(")", "")
    if clean.startswith("-"):
        try:
            return abs(float(clean))
        except ValueError:
            return 0.0
    try:
        return abs(float(clean))
    except ValueError:
        return 0.0


def parse_date(value: str) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return datetime.today().strftime("%Y-%m-%d")
    text = str(value).strip()
    if not text:
        return datetime.today().strftime("%Y-%m-%d")
    formats = [
        "%d/%m/%Y", "%d-%m-%Y", "%d-%b-%Y", "%d %b %Y",
        "%d/%m/%y", "%d-%m-%y", "%d.%m.%Y", "%d.%m.%y",
        "%Y-%m-%d", "%d-%b-%y", "%d %b %y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    match = DATE_PATTERN.search(text)
    if match:
        return parse_date(match.group(1))
    return text[:10] if len(text) >= 10 else datetime.today().strftime("%Y-%m-%d")


def _read_csv_dataframe(file_bytes: bytes) -> pd.DataFrame:
    raw_text = None
    for encoding in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
        try:
            raw_text = file_bytes.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    if raw_text is None:
        raise ValueError("Could not decode CSV file.")

    separators = [",", ";", "\t", "|"]
    best_df: pd.DataFrame | None = None
    best_score = -1

    for sep in separators:
        try:
            df = pd.read_csv(StringIO(raw_text), sep=sep, engine="python",
                             on_bad_lines="skip", dtype=str)
        except Exception:
            continue
        if df.empty or len(df.columns) < 2:
            continue
        df.columns = [str(c).strip().strip('"').strip("'") for c in df.columns]
        score = _score_header_row(list(df.columns))
        if score > best_score:
            best_score = score
            best_df = df

    if best_df is not None and best_score > 0:
        return best_df

    lines = [line for line in raw_text.splitlines() if line.strip()]
    for sep in separators:
        for index, line in enumerate(lines[:30]):
            try:
                df = pd.read_csv(StringIO(line), sep=sep, header=None, dtype=str)
            except Exception:
                continue
            if len(df.columns) < 2:
                continue
            header_cells = [str(c).strip() for c in df.iloc[0].tolist()]
            score = _score_header_row(header_cells)
            if score < 2:
                continue
            try:
                table = pd.read_csv(
                    StringIO("\n".join(lines[index:])), sep=sep,
                    engine="python", on_bad_lines="skip", dtype=str,
                )
                table.columns = [str(c).strip().strip('"').strip("'") for c in table.columns]
                if _score_header_row(list(table.columns)) >= 2:
                    return table
            except Exception:
                continue

    if best_df is not None:
        return best_df
    raise ValueError("Could not parse CSV structure.")


def _score_header_row(columns: list[str]) -> int:
    score = 0
    joined = " ".join(_normalize_col_name(c) for c in columns)
    if any(k in joined for k in ("date", "txn", "posting")):
        score += 1
    if any(k in joined for k in ("narration", "description", "remark", "particular")):
        score += 1
    if any(k in joined for k in ("debit", "credit", "withdrawal", "deposit", "amount")):
        score += 1
    return score


def _row_value(row: pd.Series, column: str | None, default=0):
    if not column or column not in row.index:
        return default
    return row[column]


def _infer_type_from_text(text: str) -> str | None:
    lower = text.lower().strip()
    if lower in {"dr", "debit", "d", "withdrawal", "paid"}:
        return "debit"
    if lower in {"cr", "credit", "c", "deposit", "received"}:
        return "credit"
    return None


def parse_csv(file_bytes: bytes) -> list[dict]:
    df = _read_csv_dataframe(file_bytes)
    df = df.dropna(how="all")
    df.columns = [str(c).strip() for c in df.columns]
    bank = detect_bank(list(df.columns))
    col_map = _build_column_map(list(df.columns), bank)
    transactions: list[dict] = []

    for _, row in df.iterrows():
        try:
            description = str(_row_value(row, col_map["description"], "")).strip()
            if description.lower() in {"nan", "none", ""}:
                description = ""
            date_raw   = _row_value(row, col_map["date"], "")
            debit      = parse_amount(_row_value(row, col_map["debit"],   0))
            credit     = parse_amount(_row_value(row, col_map["credit"],  0))
            amount_col = parse_amount(_row_value(row, col_map["amount"],  0))
            type_hint  = str(_row_value(row, col_map["type"], "")).strip()

            amount = 0.0
            txn_type = "debit"
            if debit > 0:
                amount, txn_type = debit, "debit"
            elif credit > 0:
                amount, txn_type = credit, "credit"
            elif amount_col > 0:
                amount = amount_col
                inferred = _infer_type_from_text(type_hint)
                if inferred:
                    txn_type = inferred
                elif description:
                    inferred = _infer_type_from_text(description)
                    txn_type = inferred or "debit"
                else:
                    txn_type = "debit"
            else:
                continue

            if not description:
                description = f"Transaction {amount:.2f}"
            if description.lower() in {"narration", "description", "particulars", "remarks"}:
                continue

            transactions.append({
                "date":            parse_date(date_raw),
                "raw_description": description,
                "merchant":        extract_merchant_name(description),
                "amount":          amount,
                "type":            txn_type,
            })
        except Exception:
            continue

    return transactions


def _is_date_line(line: str) -> bool:
    return bool(DATE_LINE_PATTERN.match(line) or DATE_LINE_PATTERN_SLASH.match(line))


def _is_skip_line(line: str) -> bool:
    lower = line.lower().strip()
    if not lower:
        return True
    if lower.startswith("page ") and " of " in lower:
        return True
    return any(key in lower for key in SKIP_LINE_KEYWORDS)


def _normalize_statement_table(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    columns = [str(c).strip() for c in df.columns]
    has_date_header = any("date" in _normalize_col_name(c) for c in columns)
    if not has_date_header and len(columns) >= 4:
        first_cell  = str(df.iloc[0, 0]).strip() if len(df) else ""
        second_cell = str(df.iloc[0, 1]).strip() if len(df.columns) > 1 else ""
        if SR_NO_LINE_PATTERN.match(first_cell) or _is_date_line(second_cell):
            count = min(len(columns), len(STATEMENT_TABLE_HEADERS))
            df = df.copy()
            df.columns = STATEMENT_TABLE_HEADERS[:count] + [
                f"Col{i}" for i in range(count, len(columns))
            ]
    return df


def _table_rows_to_transactions(df: pd.DataFrame) -> list[dict]:
    df = _normalize_statement_table(df)
    if df.empty or len(df.columns) < 2:
        return []
    df.columns = [str(c).strip() for c in df.columns]
    bank    = detect_bank(list(df.columns))
    col_map = _build_column_map(list(df.columns), bank)
    transactions: list[dict] = []

    for _, row in df.iterrows():
        description = str(_row_value(row, col_map["description"], "")).strip()
        description = description.replace("\n", " ").strip()
        if description.lower() in {"nan", "none", ""}:
            description = ""
        date_raw = str(_row_value(row, col_map["date"], "")).strip()
        if not _is_date_line(date_raw) and not DATE_PATTERN.search(date_raw):
            continue
        debit      = parse_amount(_row_value(row, col_map["debit"],   0))
        credit     = parse_amount(_row_value(row, col_map["credit"],  0))
        amount_col = parse_amount(_row_value(row, col_map["amount"],  0))
        if not description and debit == 0 and credit == 0 and amount_col == 0:
            continue
        if debit > 0:
            amount, txn_type = debit, "debit"
        elif credit > 0:
            amount, txn_type = credit, "credit"
        elif amount_col > 0:
            amount = amount_col
            txn_type = _infer_type_from_description(description) or "debit"
        else:
            continue
        if amount <= 0:
            continue
        if description.lower() in {"remarks", "narration", "description"}:
            continue
        transactions.append({
            "date":            parse_date(date_raw),
            "raw_description": description or "PDF transaction",
            "merchant":        extract_merchant_name(description or "PDF transaction"),
            "amount":          amount,
            "type":            txn_type,
        })
    return transactions


def _parse_pdf_tables(doc: fitz.Document) -> list[dict]:
    transactions: list[dict] = []
    for page in doc:
        try:
            tables = page.find_tables()
        except Exception:
            continue
        if not tables or not tables.tables:
            continue
        for table in tables.tables:
            try:
                df = table.to_pandas(dtype=str)
            except Exception:
                continue
            transactions.extend(_table_rows_to_transactions(df))
    return transactions


def _infer_type_from_description(description: str, saw_blank_before_amount: bool = False) -> str:
    upper = description.upper()
    if "/DR/" in upper or re.search(r"\bDR\b", upper):
        return "debit"
    if "/CR/" in upper or re.search(r"\bCR\b", upper):
        return "credit"
    if upper.startswith(("MEDR/", "POS/", "ATM/")):
        return "debit"
    if saw_blank_before_amount:
        return "credit"
    return "debit"


def _parse_pdf_indian_multiline(all_text: str) -> list[dict]:
    lines = [line.strip() for line in all_text.splitlines()]
    transactions: list[dict] = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line or _is_skip_line(line):
            continue
        if SR_NO_LINE_PATTERN.match(line):
            if i < len(lines) and _is_date_line(lines[i].strip()):
                pass
            else:
                continue
        if not _is_date_line(line):
            continue
        date_str = line
        remarks: list[str] = []
        amounts: list[float] = []
        saw_blank_before_amount = False
        saw_content = False
        while i < len(lines):
            current = lines[i].strip()
            i += 1
            if not current:
                if saw_content and not amounts:
                    saw_blank_before_amount = True
                continue
            if _is_skip_line(current):
                continue
            if SR_NO_LINE_PATTERN.match(current):
                if i < len(lines) and _is_date_line(lines[i].strip()):
                    i -= 2
                else:
                    i -= 1
                break
            if _is_date_line(current):
                i -= 1
                break
            if "₹" in current:
                break
            if AMOUNT_LINE_PATTERN.match(current.replace("₹", "").strip()):
                amounts.append(parse_amount(current))
                saw_content = True
                while i < len(lines):
                    nxt = lines[i].strip()
                    if not nxt:
                        i += 1
                        continue
                    if "₹" in nxt:
                        break
                    if AMOUNT_LINE_PATTERN.match(nxt):
                        amounts.append(parse_amount(nxt))
                        i += 1
                        continue
                    if _is_date_line(nxt) or SR_NO_LINE_PATTERN.match(nxt):
                        break
                    break
                break
            remarks.append(current)
            saw_content = True
        description = " ".join(remarks).replace("\n", " ").strip()
        if not description and not amounts:
            continue
        if len(amounts) >= 2:
            first, second = amounts[0], amounts[1]
            if first > 0 and second <= 0:
                amount, txn_type = first, "debit"
            elif second > 0 and first <= 0:
                amount, txn_type = second, "credit"
            elif first > 0:
                amount, txn_type = first, "debit"
            else:
                amount, txn_type = second, "credit"
        elif len(amounts) == 1:
            amount = amounts[0]
            txn_type = _infer_type_from_description(description, saw_blank_before_amount)
        else:
            continue
        if amount <= 0:
            continue
        transactions.append({
            "date":            parse_date(date_str),
            "raw_description": description or "PDF transaction",
            "merchant":        extract_merchant_name(description or "PDF transaction"),
            "amount":          amount,
            "type":            txn_type,
        })
    return transactions


def _parse_pdf_lines(all_text: str) -> list[dict]:
    transactions: list[dict] = []
    patterns = [
        re.compile(
            r"(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}|\d{1,2}[-\s][A-Za-z]{3}[-\s]\d{2,4})"
            r"\s+(.+?)\s+([\d,]+\.\d{2})(?:\s+[\d,]+\.\d{2})?\s*$"
        ),
        re.compile(
            r"(.+?)\s+(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})\s+([\d,]+\.\d{2})"
        ),
    ]
    for line in all_text.splitlines():
        line = line.strip()
        if len(line) < 10:
            continue
        for pattern in patterns:
            match = pattern.search(line)
            if not match:
                continue
            groups = match.groups()
            if len(groups) == 3:
                if DATE_PATTERN.match(groups[0]):
                    date_str, description, amount_str = groups
                else:
                    description, date_str, amount_str = groups
            else:
                continue
            description = description.strip(" |-")
            amount = parse_amount(amount_str)
            if amount <= 0 or len(description) < 2:
                continue
            transactions.append({
                "date":            parse_date(date_str),
                "raw_description": description,
                "merchant":        extract_merchant_name(description),
                "amount":          amount,
                "type":            "debit",
            })
            break
    if not transactions:
        for line in all_text.splitlines():
            line = line.strip()
            date_match = DATE_PATTERN.search(line)
            if not date_match:
                continue
            amounts = [
                parse_amount(match.group())
                for match in AMOUNT_PATTERN.finditer(line)
                if parse_amount(match.group()) > 0
            ]
            if not amounts:
                continue
            date_str = date_match.group(1)
            description = line.replace(date_str, "", 1)
            for value in amounts:
                description = description.replace(str(value), "", 1)
                description = re.sub(r"[\d,]+\.\d{2}", "", description, count=1)
            description = re.sub(r"\s+", " ", description).strip(" |-")
            if len(description) < 2:
                description = "PDF transaction"
            amount = amounts[0] if len(amounts) == 1 else amounts[-2] if len(amounts) >= 2 else amounts[0]
            transactions.append({
                "date":            parse_date(date_str),
                "raw_description": description,
                "merchant":        extract_merchant_name(description),
                "amount":          amount,
                "type":            "debit",
            })
    return transactions


def _dedupe_transactions(transactions: list[dict]) -> list[dict]:
    seen: set[tuple] = set()
    unique: list[dict] = []
    for txn in transactions:
        key = (
            txn.get("date"),
            round(float(txn.get("amount", 0)), 2),
            txn.get("type"),
            (txn.get("raw_description") or "")[:80],
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(txn)
    return unique


# ─────────────────────────────────────────────────────────────────────────────
# ④ MAIN ENTRY POINT — updated to route GPay / PhonePe / bank PDFs
# ─────────────────────────────────────────────────────────────────────────────

def parse_pdf(file_bytes: bytes) -> list[dict]:
    """
    Auto-detect PDF source and route to the right parser.

    Priority:
      1. Google Pay statement  → _parse_gpay_pdf()
      2. PhonePe statement     → _parse_phonepe_pdf()
      3. Bank statement (table)→ _parse_pdf_tables()
      4. Indian multiline layout → _parse_pdf_indian_multiline()
      5. Generic line fallback → _parse_pdf_lines()
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    first_page_text = doc[0].get_text() if len(doc) > 0 else ""
    doc.close()

    source = _detect_pdf_source(first_page_text)

    if source == "GPAY":
        transactions = _parse_gpay_pdf(file_bytes)
        if transactions:
            return _dedupe_transactions(transactions)

    if source == "PHONEPE":
        transactions = _parse_phonepe_pdf(file_bytes)
        if transactions:
            return _dedupe_transactions(transactions)

    # Bank statement path (original logic)
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    all_text = "".join(page.get_text("text") + "\n" for page in doc)

    table_txns      = _parse_pdf_tables(doc)
    multiline_txns  = _parse_pdf_indian_multiline(all_text)
    line_txns       = _parse_pdf_lines(all_text) if not multiline_txns else []
    doc.close()

    candidates = [
        _dedupe_transactions(multiline_txns),
        _dedupe_transactions(table_txns),
        _dedupe_transactions(line_txns),
    ]
    candidates.sort(key=len, reverse=True)
    return candidates[0]


def extract_merchant_name(description: str) -> str:
    """Clean UPI/NEFT/IMPS prefixes to get human-readable merchant name."""
    upi_match = re.search(
        r"UPI/\d+/(DR|CR)/([^/\n]+)", description, flags=re.IGNORECASE
    )
    if upi_match:
        return upi_match.group(2).strip().title()[:40]
    imps_match = re.search(r"IMPS/\d+/(.+)", description, flags=re.IGNORECASE)
    if imps_match:
        return imps_match.group(1).strip().title()[:40]
    prefixes = [
        r"UPI[-/]", r"NEFT[-/]", r"IMPS[-/]", r"ACH[-/]", r"NACH[-/]",
        r"POS[-/]", r"ATM[-/]", r"MEDR[-/]", r"BIL[-/]BILL[-/]",
        r"MMT[-/]", r"P2A[-/]", r"P2M[-/]", r"AP[-/]",
    ]
    merchant = description.upper()
    for prefix in prefixes:
        merchant = re.sub(prefix, "", merchant, flags=re.IGNORECASE)
    parts = re.split(r"[-@/|]", merchant)
    clean = parts[0].strip().title() if parts else merchant
    clean = re.sub(r"\s+\d{6,}$", "", clean).strip()
    return clean or description[:40]