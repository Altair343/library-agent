from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.book.service import BookService
from app.db.session import get_session

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_product_service(session: SessionDep) -> BookService:
    return BookService(session)


BookServiceDep = Annotated[
    BookService,
    Depends(get_product_service),
]
