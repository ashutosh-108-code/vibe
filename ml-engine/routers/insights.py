from uuid import UUID

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from sqlalchemy import select

from db.database import AsyncSessionLocal, get_engine
from db.models import Category, Transaction
from routers.stats import build_stats_summary
from services.insight_generator import generate_insights


router = APIRouter(prefix="/api", tags=["insights"])

CATEGORY_ICONS = {
    "Food": "UtensilsCrossed",
    "Transport": "Car",
    "Groceries": "ShoppingCart",
    "Rent": "Home",
    "EMI": "CreditCard",
    "Shopping": "ShoppingBag",
    "Investments": "TrendingUp",
    "Other": "MoreHorizontal",
}


def _error(status_code: int, error: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": error, "message": message})


async def _load_anomalies(statement_id: str) -> list[dict]:
    statement_uuid = UUID(statement_id)

    get_engine()
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Transaction, Category)
            .join(Category, Transaction.category_id == Category.category_id, isouter=True)
            .where(Transaction.statement_id == statement_uuid)
            .where(Transaction.is_anomaly.is_(True))
        )
        rows = result.all()

    return [
        {
            "transaction_id": str(transaction.transaction_id),
            "merchant": transaction.merchant or "Unknown",
            "amount": float(transaction.amount),
            "reason": transaction.anomaly_reason or "Amount is unusually high.",
            "category": category.name if category else "Other",
        }
        for transaction, category in rows
    ]


@router.get("/insights")
async def get_insights(
    statement_id: str,
    language: str = Query(default="en", pattern="^(en|hi)$"),
):
    try:
        summary = await build_stats_summary(statement_id, "monthly")
        summary["anomalies"] = await _load_anomalies(statement_id)
        insights = generate_insights(summary, language)

        return {
            "language": language,
            "insights": [
                {
                    "type": insight["type"],
                    "category": insight["category"],
                    "icon": CATEGORY_ICONS.get(insight["category"], "MoreHorizontal"),
                    "title": insight["title"],
                    "body": insight["body"],
                    "severity": insight["severity"],
                }
                for insight in insights
            ],
        }
    except ValueError:
        return _error(400, "INVALID_STATEMENT_ID", "statement_id must be a valid UUID.")
    except Exception as exc:
        return _error(500, "INSIGHTS_FAILED", f"Could not load insights: {str(exc)}")
