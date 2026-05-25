"""create initial tables

Revision ID: 20260524_0001
Revises:
Create Date: 2026-05-24
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260524_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    op.create_table(
        "statements",
        sa.Column(
            "statement_id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("bank_name", sa.String(length=100), nullable=True),
        sa.Column("file_type", sa.String(length=10), nullable=False),
        sa.Column("upload_date", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("total_rows", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.CheckConstraint("file_type IN ('csv', 'pdf')"),
        sa.CheckConstraint("status IN ('pending', 'processing', 'completed', 'error')"),
        sa.PrimaryKeyConstraint("statement_id"),
    )

    op.create_table(
        "categories",
        sa.Column("category_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("color_hex", sa.String(length=7), nullable=False),
        sa.Column("icon_key", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("category_id"),
        sa.UniqueConstraint("name"),
    )

    op.bulk_insert(
        sa.table(
            "categories",
            sa.column("name", sa.String),
            sa.column("color_hex", sa.String),
            sa.column("icon_key", sa.String),
        ),
        [
            {"name": "Food", "color_hex": "#F59E0B", "icon_key": "UtensilsCrossed"},
            {"name": "Transport", "color_hex": "#3B82F6", "icon_key": "Car"},
            {"name": "Groceries", "color_hex": "#10B981", "icon_key": "ShoppingCart"},
            {"name": "Rent", "color_hex": "#8B5CF6", "icon_key": "Home"},
            {"name": "EMI", "color_hex": "#EF4444", "icon_key": "CreditCard"},
            {"name": "Shopping", "color_hex": "#EC4899", "icon_key": "ShoppingBag"},
            {"name": "Investments", "color_hex": "#06B6D4", "icon_key": "TrendingUp"},
            {"name": "Other", "color_hex": "#64748B", "icon_key": "MoreHorizontal"},
        ],
    )

    op.create_table(
        "transactions",
        sa.Column(
            "transaction_id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("statement_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("transaction_date", sa.Date(), nullable=False),
        sa.Column("merchant", sa.String(length=255), nullable=True),
        sa.Column("raw_description", sa.Text(), nullable=False),
        sa.Column("amount", sa.DECIMAL(precision=12, scale=2), nullable=False),
        sa.Column("transaction_type", sa.String(length=10), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("ml_confidence", sa.Float(), nullable=True),
        sa.Column("is_anomaly", sa.Boolean(), nullable=True),
        sa.Column("anomaly_reason", sa.Text(), nullable=True),
        sa.Column("manually_updated", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.CheckConstraint("transaction_type IN ('debit', 'credit')"),
        sa.ForeignKeyConstraint(["category_id"], ["categories.category_id"]),
        sa.ForeignKeyConstraint(["statement_id"], ["statements.statement_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("transaction_id"),
    )
    op.create_index("idx_transactions_statement", "transactions", ["statement_id"], unique=False)
    op.create_index("idx_transactions_date", "transactions", ["transaction_date"], unique=False)
    op.create_index("idx_transactions_category", "transactions", ["category_id"], unique=False)

    op.create_table(
        "insights",
        sa.Column(
            "insight_id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("statement_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("insight_type", sa.String(length=30), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=True),
        sa.Column("title_en", sa.Text(), nullable=False),
        sa.Column("body_en", sa.Text(), nullable=False),
        sa.Column("title_hi", sa.Text(), nullable=True),
        sa.Column("body_hi", sa.Text(), nullable=True),
        sa.Column("severity", sa.String(length=10), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.CheckConstraint("severity IN ('success', 'warning', 'error', 'info')"),
        sa.ForeignKeyConstraint(["statement_id"], ["statements.statement_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("insight_id"),
    )


def downgrade() -> None:
    op.drop_table("insights")
    op.drop_index("idx_transactions_category", table_name="transactions")
    op.drop_index("idx_transactions_date", table_name="transactions")
    op.drop_index("idx_transactions_statement", table_name="transactions")
    op.drop_table("transactions")
    op.drop_table("categories")
    op.drop_table("statements")
