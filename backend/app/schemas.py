"""Request/response models (Pydantic). Validation errors become HTTP 422 automatically."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

from .domain import (
    Category,
    ExpiryStatus,
    Location,
    Unit,
    days_until,
    expiry_status,
    is_low_stock,
)


class ItemBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    category: Category = "Other"
    location: Location = "Pantry"
    quantity: float = Field(default=1, ge=0, le=100_000)
    unit: Unit = "pcs"
    min_quantity: float = Field(default=0, ge=0, le=100_000)
    expiry_date: date | None = None
    notes: str | None = Field(default=None, max_length=500)

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("name must not be blank")
        return value


class ItemCreate(ItemBase):
    """Body for POST /api/items."""


class ItemUpdate(ItemBase):
    """Body for PUT /api/items/{id}: a full replacement of the editable fields."""


class ConsumeRequest(BaseModel):
    amount: float = Field(default=1, gt=0, le=100_000)


class ItemOut(ItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def days_until_expiry(self) -> int | None:
        return days_until(self.expiry_date)

    @computed_field
    @property
    def expiry_status(self) -> ExpiryStatus:
        return expiry_status(self.expiry_date)

    @computed_field
    @property
    def low_stock(self) -> bool:
        return is_low_stock(self.quantity, self.min_quantity)


class SummaryOut(BaseModel):
    total: int
    expired: int
    expiring_soon: int
    low_stock: int
    by_location: dict[str, int]
    expiry_warning_days: int


class MetaOut(BaseModel):
    service: str
    version: str
    environment: str
    categories: list[str]
    locations: list[str]
    units: list[str]
    expiry_warning_days: int
