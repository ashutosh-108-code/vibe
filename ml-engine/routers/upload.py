from datetime import date
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import pandas as pd
from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy import select

from db.database import AsyncSessionLocal, get_engine
from db.models import Category, Statement, Transaction
from services.anomaly_detector import detect_anomalies
from services.categorizer import categorizer
from services.file_parser import BANK_COLUMN_MAPS, detect_bank, parse_csv, parse_pdf


router = APIRouter(prefix="/api", tags=["upload"])

MAX_FILE_SIZE = 10 * 1024 * 1024
CATEGORY_META = {
    "Food": {"color_hex": "#F59E0B", "icon_key": "UtensilsCrossed"},
    "Transport": {"color_hex": "#3B82F6", "icon_key": "Car"},
    "Groceries": {"color_hex": "#10B981", "icon_key": "ShoppingCart"},
    "Rent": {"color_hex": "#8B5CF6", "icon_key": "Home"},
    "EMI": {"color_hex": "#EF4444", "icon_key": "CreditCard"},
    "Shopping": {"color_hex": "#EC4899", "icon_key": "ShoppingBag"},
    "Investments": {"color_hex": "#06B6D4", "icon_key": "TrendingUp"},
    "Other": {"color_hex": "#64748B", "icon_key": "MoreHorizontal"},
}


def _error(status_code: int, error: str, message: str, **extra: Any) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": error, "message": message, **extra},
    )


def _detect_csv_bank(file_bytes: bytes) -> str:
    try:
        from io import BytesIO

        df = pd.read_csv(BytesIO(file_bytes), nrows=0, encoding="utf-8", on_bad_lines="skip")
    except UnicodeDecodeError:
        from io import BytesIO

        df = pd.read_csv(BytesIO(file_bytes), nrows=0, encoding="latin-1", on_bad_lines="skip")
    except Exception:
        return "GENERIC"

    df.columns = [c.strip() for c in df.columns]
    return detect_bank(list(df.columns))


def _normalize_transaction(transaction: dict) -> dict:
    category, confidence = categorizer.categorize(transaction["raw_description"])
    return {
        **transaction,
        "id": str(uuid4()),
        "category": category,
        "confidence": confidence,
        "is_anomaly": False,
        "anomaly_reason": None,
    }


def _build_summary(transactions: list[dict]) -> dict:
    total_debit = 0.0
    total_credit = 0.0
    by_category = {category: 0.0 for category in CATEGORY_META}
    anomalies = []

    for transaction in transactions:
        amount = float(transaction["amount"])
        if transaction["type"] == "debit":
            total_debit += amount
            by_category[transaction["category"]] += amount
        else:
            total_credit += amount

        if transaction.get("is_anomaly"):
            anomalies.append({
                "transaction_id": transaction["id"],
                "merchant": transaction["merchant"],
                "amount": amount,
                "reason": transaction.get("anomaly_reason"),
            })

    return {
        "total_debit": total_debit,
        "total_credit": total_credit,
        "by_category": by_category,
        "anomalies": anomalies,
    }


async def _get_or_create_categories(session) -> dict[str, Category]:
    result = await session.execute(select(Category))
    categories = {category.name: category for category in result.scalars()}

    for name, meta in CATEGORY_META.items():
        if name not in categories:
            categories[name] = Category(name=name, **meta)
            session.add(categories[name])

    await session.flush()
    return categories


def _parse_iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return date.today()


async def _save_to_db(
    filename: str,
    file_type: str,
    bank_detected: str,
    transactions: list[dict],
) -> str:
    get_engine()
    async with AsyncSessionLocal() as session:
        try:
            statement_id = uuid4()
            categories = await _get_or_create_categories(session)
            statement = Statement(
                statement_id=statement_id,
                filename=filename,
                bank_name=bank_detected if bank_detected in BANK_COLUMN_MAPS else None,
                file_type=file_type,
                status="completed",
                total_rows=len(transactions),
            )
            session.add(statement)
            await session.flush()

            for transaction in transactions:
                db_transaction = Transaction(
                    transaction_id=UUID(transaction["id"]),
                    statement_id=statement_id,
                    transaction_date=_parse_iso_date(transaction["date"]),
                    merchant=transaction["merchant"],
                    raw_description=transaction["raw_description"],
                    amount=float(transaction["amount"]),
                    transaction_type=transaction["type"],
                    category_id=categories[transaction["category"]].category_id,
                    ml_confidence=float(transaction["confidence"]),
                    is_anomaly=transaction["is_anomaly"],
                    anomaly_reason=transaction.get("anomaly_reason"),
                    manually_updated=False,
                )
                session.add(db_transaction)

            await session.commit()
            return str(statement_id)
        except Exception:
            await session.rollback()
            raise


@router.post("/upload")
async def upload_statement(
    file: UploadFile = File(...),
    session_id: str | None = Form(default=None),
):
    try:
        filename = file.filename or ""
        suffix = Path(filename).suffix.lower()
        if suffix not in {".csv", ".pdf"}:
            return _error(
                400,
                "UNSUPPORTED_FORMAT",
                f"Only CSV and PDF files are supported. Received: {suffix or 'unknown'}",
            )

        file_bytes = await file.read()
        if not file_bytes:
            return _error(
                422,
                "PARSE_FAILED",
                "Uploaded file is empty.",
                rows_extracted=0,
            )

        if len(file_bytes) > MAX_FILE_SIZE:
            size_mb = len(file_bytes) / (1024 * 1024)
            return _error(
                413,
                "FILE_TOO_LARGE",
                f"File size {size_mb:.1f}MB exceeds the 10MB limit.",
            )

        try:
            if suffix == ".csv":
                bank_detected = _detect_csv_bank(file_bytes)
                parsed_transactions = parse_csv(file_bytes)
                file_type = "csv"
            else:
                bank_detected = "GENERIC"
                parsed_transactions = parse_pdf(file_bytes)
                file_type = "pdf"
        except Exception as exc:
            hint = (
                "Could not read this CSV. Export your statement from the bank app "
                "with columns for Date, Description/Narration, and Debit/Credit (or Amount)."
                if suffix == ".csv"
                else
                "Could not read this PDF. Export the statement as CSV from your bank app "
                "(HDFC, SBI, ICICI, etc.) for best results."
            )
            return _error(
                422,
                "PARSE_FAILED",
                f"{hint} Details: {str(exc)}",
                rows_extracted=0,
            )

        if not parsed_transactions:
            hint = (
                "No transactions found in this CSV. Check that it has Date, Description, "
                "and Withdrawal/Deposit (or Amount) columns with data rows."
                if suffix == ".csv"
                else
                "No transactions found in this PDF. Scanned PDFs or complex layouts may not parse. "
                "Please export as CSV from your bank website or app."
            )
            return _error(
                422,
                "PARSE_FAILED",
                hint,
                rows_extracted=0,
            )

        transactions = [_normalize_transaction(t) for t in parsed_transactions]
        transactions = detect_anomalies(transactions)
        summary = _build_summary(transactions)
        statement_id = await _save_to_db(filename, file_type, bank_detected, transactions)

        return {
            "statement_id": statement_id,
            "filename": filename,
            "bank_detected": bank_detected,
            "total_transactions": len(transactions),
            "transactions": [
                {
                    "id": transaction["id"],
                    "date": transaction["date"],
                    "merchant": transaction["merchant"],
                    "raw_description": transaction["raw_description"],
                    "amount": float(transaction["amount"]),
                    "type": transaction["type"],
                    "category": transaction["category"],
                    "confidence": float(transaction["confidence"]),
                    "is_anomaly": bool(transaction["is_anomaly"]),
                }
                for transaction in transactions
            ],
            "summary": summary,
        }
    except Exception as exc:
        return _error(
            500,
            "UPLOAD_FAILED",
            f"Could not process upload: {str(exc)}",
        )
