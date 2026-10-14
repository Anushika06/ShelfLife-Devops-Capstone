"""Pantry business rules: allowed values and expiry / stock status calculations."""

from datetime import date, datetime
from typing import Literal
from zoneinfo import ZoneInfo

from .config import get_settings

CATEGORIES = (
    "Produce",
    "Dairy",
    "Meat & Fish",
    "Bakery",
    "Grains & Pasta",
    "Canned & Jarred",
    "Frozen",
    "Snacks",
    "Beverages",
    "Spices & Condiments",
    "Household",
    "Other",
)
LOCATIONS = ("Fridge", "Freezer", "Pantry")
UNITS = ("pcs", "g", "kg", "ml", "L", "pack")

Category = Literal[
    "Produce",
    "Dairy",
    "Meat & Fish",
    "Bakery",
    "Grains & Pasta",
    "Canned & Jarred",
    "Frozen",
    "Snacks",
    "Beverages",
    "Spices & Condiments",
    "Household",
    "Other",
]
Location = Literal["Fridge", "Freezer", "Pantry"]
Unit = Literal["pcs", "g", "kg", "ml", "L", "pack"]
ExpiryStatus = Literal["expired", "expiring", "fresh", "no-date"]


def today() -> date:
    return datetime.now(ZoneInfo(get_settings().app_timezone)).date()


def days_until(expiry: date | None, reference: date | None = None) -> int | None:
    if expiry is None:
        return None
    return (expiry - (reference or today())).days


def expiry_status(expiry: date | None, reference: date | None = None) -> ExpiryStatus:
    remaining = days_until(expiry, reference)
    if remaining is None:
        return "no-date"
    if remaining < 0:
        return "expired"
    if remaining <= get_settings().expiry_warning_days:
        return "expiring"
    return "fresh"


def is_low_stock(quantity: float, min_quantity: float) -> bool:
    return min_quantity > 0 and quantity <= min_quantity
