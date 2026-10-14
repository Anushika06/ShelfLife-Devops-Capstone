"""Pantry item REST API: list, read, create, replace, consume, delete, summary."""

from datetime import timedelta
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..domain import LOCATIONS, Category, Location, expiry_status, is_low_stock, today
from ..metrics import ITEMS_CONSUMED, ITEMS_CREATED, ITEMS_DELETED, PANTRY_ITEMS
from ..models import PantryItem
from ..schemas import ConsumeRequest, ItemCreate, ItemOut, ItemUpdate, SummaryOut

router = APIRouter(prefix="/api", tags=["items"])

StatusFilter = Literal["expired", "expiring", "fresh", "no-date", "low-stock"]
SortOrder = Literal["expiry", "name", "updated"]


def _get_or_404(db: Session, item_id: int) -> PantryItem:
    item = db.get(PantryItem, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


@router.get("/items", response_model=list[ItemOut])
def list_items(
    location: Location | None = None,
    category: Category | None = None,
    status_filter: StatusFilter | None = Query(default=None, alias="status"),
    q: str | None = Query(default=None, max_length=120, description="Search name and notes"),
    sort: SortOrder = "expiry",
    db: Session = Depends(get_db),
):
    stmt = select(PantryItem)
    if location:
        stmt = stmt.where(PantryItem.location == location)
    if category:
        stmt = stmt.where(PantryItem.category == category)
    if q:
        pattern = f"%{q.strip().lower()}%"
        stmt = stmt.where(
            or_(func.lower(PantryItem.name).like(pattern), func.lower(PantryItem.notes).like(pattern))
        )

    # Expiry status depends on "today" and the warning window, so these filters are
    # translated into date ranges here rather than stored in the table.
    now = today()
    warn_until = now + timedelta(days=get_settings().expiry_warning_days)
    if status_filter == "expired":
        stmt = stmt.where(PantryItem.expiry_date < now)
    elif status_filter == "expiring":
        stmt = stmt.where(PantryItem.expiry_date >= now, PantryItem.expiry_date <= warn_until)
    elif status_filter == "fresh":
        stmt = stmt.where(PantryItem.expiry_date > warn_until)
    elif status_filter == "no-date":
        stmt = stmt.where(PantryItem.expiry_date.is_(None))
    elif status_filter == "low-stock":
        stmt = stmt.where(PantryItem.min_quantity > 0, PantryItem.quantity <= PantryItem.min_quantity)

    if sort == "name":
        stmt = stmt.order_by(func.lower(PantryItem.name), PantryItem.id)
    elif sort == "updated":
        stmt = stmt.order_by(PantryItem.updated_at.desc(), PantryItem.id.desc())
    else:
        # Soonest expiry first; items without a date go last.
        stmt = stmt.order_by(PantryItem.expiry_date.is_(None), PantryItem.expiry_date, PantryItem.id)
    return db.scalars(stmt).all()


@router.get("/items/{item_id}", response_model=ItemOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, item_id)


@router.post("/items", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)):
    item = PantryItem(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    ITEMS_CREATED.labels(location=item.location).inc()
    return item


@router.put("/items/{item_id}", response_model=ItemOut)
def replace_item(item_id: int, payload: ItemUpdate, db: Session = Depends(get_db)):
    item = _get_or_404(db, item_id)
    for field, value in payload.model_dump().items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.post("/items/{item_id}/consume", response_model=ItemOut)
def consume_item(item_id: int, payload: ConsumeRequest, db: Session = Depends(get_db)):
    """Use up some of an item. Quantity never goes below zero."""
    item = _get_or_404(db, item_id)
    item.quantity = max(0.0, round(item.quantity - payload.amount, 3))
    db.commit()
    db.refresh(item)
    ITEMS_CONSUMED.inc()
    return item


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = _get_or_404(db, item_id)
    db.delete(item)
    db.commit()
    ITEMS_DELETED.inc()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/summary", response_model=SummaryOut)
def summary(db: Session = Depends(get_db)):
    rows = db.execute(
        select(PantryItem.location, PantryItem.expiry_date, PantryItem.quantity, PantryItem.min_quantity)
    ).all()
    now = today()
    by_location = dict.fromkeys(LOCATIONS, 0)
    counts = {"expired": 0, "expiring": 0, "fresh": 0, "no-date": 0}
    low_stock = 0
    for location, expiry, quantity, min_quantity in rows:
        by_location[location] = by_location.get(location, 0) + 1
        counts[expiry_status(expiry, now)] += 1
        low_stock += is_low_stock(quantity, min_quantity)

    for name, value in counts.items():
        PANTRY_ITEMS.labels(status=name).set(value)
    PANTRY_ITEMS.labels(status="low-stock").set(low_stock)

    return SummaryOut(
        total=len(rows),
        expired=counts["expired"],
        expiring_soon=counts["expiring"],
        low_stock=low_stock,
        by_location=by_location,
        expiry_warning_days=get_settings().expiry_warning_days,
    )
