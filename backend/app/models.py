"""Database tables. Schema changes are applied with Alembic (see alembic/versions)."""

from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class PantryItem(Base):
    __tablename__ = "pantry_items"
    __table_args__ = (CheckConstraint("quantity >= 0", name="ck_pantry_items_quantity_non_negative"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str] = mapped_column(String(40), nullable=False, default="Other")
    location: Mapped[str] = mapped_column(String(20), nullable=False, default="Pantry", index=True)
    quantity: Mapped[float] = mapped_column(Float, nullable=False, default=1)
    unit: Mapped[str] = mapped_column(String(20), nullable=False, default="pcs")
    # Added by migration 0002: when quantity drops to/below this, the item is "low stock".
    min_quantity: Mapped[float] = mapped_column(Float, nullable=False, default=0, server_default="0")
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
