from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Integer,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Book(Base):
    __tablename__ = "book"

    __table_args__ = (
        CheckConstraint(
            "stock >= 0",
            name="stock_non_negative",
        ),
        CheckConstraint(
            "length(trim(title)) > 0",
            name="title_not_blank",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    isbn: Mapped[str | None] = mapped_column(
        String(24),
        unique=True,
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    stock: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )

    date_publication: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
