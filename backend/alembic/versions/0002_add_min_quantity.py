"""Add min_quantity so items can be flagged as low stock.

Revision ID: 0002_add_min_quantity
Revises: 0001_create_pantry_items
Create Date: 2026-10-14
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_add_min_quantity"
down_revision: str | None = "0001_create_pantry_items"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("pantry_items") as batch:
        batch.add_column(sa.Column("min_quantity", sa.Float(), nullable=False, server_default="0"))


def downgrade() -> None:
    with op.batch_alter_table("pantry_items") as batch:
        batch.drop_column("min_quantity")
