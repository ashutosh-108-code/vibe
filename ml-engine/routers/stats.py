from collections import defaultdict
from datetime import date, timedelta
from uuid import UUID

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from sqlalchemy import select

from db.database import AsyncSessionLocal, get_engine
from db.models import Category, Transaction


router = APIRouter(prefix="/api", tags=["stats"])

CATEGORIES = [
    "Food", "Transport", "Groceries", "Rent",
    "EMI", "Shopping", "Investments", "Other",
]


def _error(status_code: int, error: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": error, "message": message})


def _period_start(period: str) -> date | None:
    today = date.today()
    if period == "weekly":
        return today - timedelta(days=7)
    if period == "monthly":
        return today.replace(day=1)
    return None


def _resolve_period_start(period: str, transaction_dates: list[date]) -> date | None:
    """Anchor period filters to the statement's dates, not the server clock."""
    if not transaction_dates:
        return _period_start(period)

    latest = max(transaction_dates)
    if period == "weekly":
        return latest - timedelta(days=7)
    if period == "monthly":
        return latest.replace(day=1)
    return None


async def build_stats_summary(statement_id: str, period: str = "monthly") -> dict:
    statement_uuid = UUID(statement_id)

    get_engine()
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Transaction, Category)
            .join(Category, Transaction.category_id == Category.category_id, isouter=True)
            .where(Transaction.statement_id == statement_uuid)
        )
        all_rows = result.all()

    transaction_dates = [transaction.transaction_date for transaction, _ in all_rows]
    start_date = _resolve_period_start(period, transaction_dates)

    rows = [
        row
        for row in all_rows
        if start_date is None or row[0].transaction_date >= start_date
    ]

    total_debit = 0.0
    total_credit = 0.0
    category_amounts = {category: 0.0 for category in CATEGORIES}
    category_counts = {category: 0 for category in CATEGORIES}
    daily_spending = defaultdict(float)
    merchant_totals = defaultdict(lambda: {"amount": 0.0, "count": 0})

    for transaction, category in rows:
        amount = float(transaction.amount)
        category_name = category.name if category else "Other"
        merchant = transaction.merchant or "Unknown"

        if transaction.transaction_type == "credit":
            total_credit += amount
            continue

        total_debit += amount
        category_amounts[category_name] = category_amounts.get(category_name, 0.0) + amount
        category_counts[category_name] = category_counts.get(category_name, 0) + 1
        daily_spending[transaction.transaction_date.isoformat()] += amount
        merchant_totals[merchant]["amount"] += amount
        merchant_totals[merchant]["count"] += 1

    by_category = {
        category: {
            "amount": amount,
            "percentage": round((amount / total_debit) * 100, 1) if total_debit else 0.0,
            "transaction_count": category_counts.get(category, 0),
        }
        for category, amount in category_amounts.items()
    }
    top_merchants = [
        {"merchant": merchant, "amount": data["amount"], "count": data["count"]}
        for merchant, data in sorted(
            merchant_totals.items(),
            key=lambda item: item[1]["amount"],
            reverse=True,
        )[:5]
    ]

    return {
        "period": period,
        "total_debit": total_debit,
        "total_credit": total_credit,
        "net_savings": total_credit - total_debit,
        "savings_rate": round(((total_credit - total_debit) / total_credit) * 100, 1) if total_credit else 0.0,
        "by_category": by_category,
        "daily_spending": [
            {"date": day, "amount": amount}
            for day, amount in sorted(daily_spending.items())
        ],
        "top_merchants": top_merchants,
    }


@router.get("/stats")
async def get_stats(
    statement_id: str,
    period: str = Query(default="monthly", pattern="^(weekly|monthly|all)$"),
):
    try:
        return await build_stats_summary(statement_id, period)
    except ValueError:
        return _error(400, "INVALID_STATEMENT_ID", "statement_id must be a valid UUID.")
    except Exception as exc:
        return _error(500, "STATS_FAILED", f"Could not load stats: {str(exc)}")
