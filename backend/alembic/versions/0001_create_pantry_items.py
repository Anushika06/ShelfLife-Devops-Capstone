"""Create the pantry_items table.

Revision ID: 0001_create_pantry_items
Revises:
Create Date: 2026-10-14
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_create_pantry_items"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "pantry_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("category", sa.String(length=40), nullable=False, server_default="Other"),
        sa.Column("location", sa.String(length=20), nullable=False, server_default="Pantry"),
        sa.Column("quantity", sa.Float(), nullable=False, server_default="1"),
        sa.Column("unit", sa.String(length=20), nullable=False, server_default="pcs"),
        sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("quantity >= 0", name="ck_pantry_items_quantity_non_negative"),
    )
    op.create_index("ix_pantry_items_location", "pantry_items", ["location"])
    op.create_index("ix_pantry_items_expiry_date", "pantry_items", ["expiry_date"])


def downgrade() -> None:
    op.drop_index("ix_pantry_items_expiry_date", table_name="pantry_items")
    op.drop_index("ix_pantry_items_location", table_name="pantry_items")
    op.drop_table("pantry_items")
