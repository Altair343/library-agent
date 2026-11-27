from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints


class BookRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    isbn: str | None
    description: str | None
    stock: int
    date_publication: str | None
    created_at: datetime


class BookPage(BaseModel):
    items: list[BookRead]
    limit: int
    offset: int
    has_more: bool


class BookCreate(BaseModel):
    title: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=200),
    ]
    isbn: str | None
    description: str | None
    stock: int
    date_publication: str | None


class BookUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    isbn: str | None = None
    description: str | None = None
    stock: int | None = None
    date_publication: str | None = None
