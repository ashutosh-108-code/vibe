import json
from datetime import date
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import APIRouter, Body, Query
from fastapi.responses import JSONResponse
from sqlalchemy import func, or_, select

from db.database import AsyncSessionLocal, get_engine
from db.models import Category, Statement, Transaction
from routers.upload import CATEGORY_META


router = APIRouter(prefix="/api", tags=["transactions"])
DEMO_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "demo-data.json"


def _error(status_code: int, error: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": error, "message": message})


def _transaction_response(transaction: Transaction, category: Category | None) -> dict:
    return {
        "id": str(transaction.transaction_id),
        "date": transaction.transaction_date.isoformat(),
        "merchant": transaction.merchant,
        "raw_description": transaction.raw_description,
        "amount": float(transaction.amount),
        "type": transaction.transaction_type,
        "category": category.name if category else "Other",
        "confidence": float(transaction.ml_confidence or 0),
        "is_anomaly": bool(transaction.is_anomaly),
        "anomaly_reason": transaction.anomaly_reason,
        "manually_updated": bool(transaction.manually_updated),
    }


async def _get_or_create_categories(session) -> dict[str, Category]:
    result = await session.execute(select(Category))
    categories = {category.name: category for category in result.scalars()}
    for name, meta in CATEGORY_META.items():
        if name not in categories:
            categories[name] = Category(name=name, color_hex=meta["color_hex"], icon_key=meta["icon_key"])
            session.add(categories[name])
    await session.flush()
    return categories


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


@router.get("/transactions")
async def get_transactions(
    statement_id: str,
    category: str | None = None,
    search: str | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
):
    try:
        statement_uuid = UUID(statement_id)
        get_engine()
        async with AsyncSessionLocal() as session:
            base_query = (
                select(Transaction, Category)
                .join(Category, Transaction.category_id == Category.category_id, isouter=True)
                .where(Transaction.statement_id == statement_uuid)
            )
            count_query = (
                select(func.count())
                .select_from(Transaction)
                .join(Category, Transaction.category_id == Category.category_id, isouter=True)
                .where(Transaction.statement_id == statement_uuid)
            )

            if category:
                base_query = base_query.where(Category.name == category)
                count_query = count_query.where(Category.name == category)
            if search:
                pattern = f"%{search}%"
                search_filter = or_(
                    Transaction.merchant.ilike(pattern),
                    Transaction.raw_description.ilike(pattern),
                )
                base_query = base_query.where(search_filter)
                count_query = count_query.where(search_filter)

            total = await session.scalar(count_query)
            result = await session.execute(
                base_query
                .order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())
                .offset((page - 1) * limit)
                .limit(limit)
            )

        return {
            "total": total or 0,
            "page": page,
            "limit": limit,
            "transactions": [
                _transaction_response(transaction, cat)
                for transaction, cat in result.all()
            ],
        }
    except ValueError:
        return _error(400, "INVALID_STATEMENT_ID", "statement_id must be a valid UUID.")
    except Exception as exc:
        return _error(500, "TRANSACTIONS_FAILED", f"Could not load transactions: {str(exc)}")


@router.patch("/transactions/{transaction_id}/category")
async def update_transaction_category(
    transaction_id: str,
    payload: dict = Body(...),
):
    try:
        transaction_uuid = UUID(transaction_id)
        new_category_name = payload.get("category")
        if new_category_name not in CATEGORY_META:
            return _error(400, "INVALID_CATEGORY", "Category must be one of the fixed 8 categories.")

        get_engine()
        async with AsyncSessionLocal() as session:
            categories = await _get_or_create_categories(session)
            transaction = await session.get(Transaction, transaction_uuid)
            if transaction is None:
                return _error(404, "TRANSACTION_NOT_FOUND", "Transaction not found.")

            old_category = await session.get(Category, transaction.category_id) if transaction.category_id else None
            transaction.category_id = categories[new_category_name].category_id
            transaction.manually_updated = True
            await session.commit()

        return {
            "transaction_id": str(transaction_uuid),
            "old_category": old_category.name if old_category else "Other",
            "new_category": new_category_name,
            "updated": True,
        }
    except ValueError:
        return _error(400, "INVALID_TRANSACTION_ID", "transaction_id must be a valid UUID.")
    except Exception as exc:
        return _error(500, "RECATEGORIZE_FAILED", f"Could not update category: {str(exc)}")


@router.post("/demo")
async def load_demo_data():
    try:
        demo = json.loads(DEMO_DATA_PATH.read_text(encoding="utf-8"))
        transactions = demo["transactions"]
        statement_id = uuid4()

        get_engine()
        async with AsyncSessionLocal() as session:
            categories = await _get_or_create_categories(session)
            statement = Statement(
                statement_id=statement_id,
                filename=demo["filename"],
                bank_name=demo.get("bankDetected"),
                file_type="csv",
                status="completed",
                total_rows=len(transactions),
            )
            session.add(statement)
            await session.flush()

            for item in transactions:
                session.add(Transaction(
                    transaction_id=uuid4(),
                    statement_id=statement_id,
                    transaction_date=_parse_date(item["date"]),
                    merchant=item["merchant"],
                    raw_description=item["raw_description"],
                    amount=float(item["amount"]),
                    transaction_type=item["type"],
                    category_id=categories[item["category"]].category_id,
                    ml_confidence=float(item.get("confidence", 1.0)),
                    is_anomaly=bool(item.get("is_anomaly", False)),
                    anomaly_reason=item.get("anomaly_reason"),
                    manually_updated=False,
                ))

            await session.commit()

        return {
            "statement_id": str(statement_id),
            "message": f"{len(transactions)} demo transactions loaded",
            "redirect_to": f"/dashboard?statement_id={statement_id}",
        }
    except Exception as exc:
        return _error(500, "DEMO_LOAD_FAILED", f"Could not load demo data: {str(exc)}")
