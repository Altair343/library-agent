from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.book.repository import BookRepository
from app.book.schemas import BookCreate, BookRead, BookUpdate
from app.core.exceptions import BookError

BOOK_NOT_FOUND = "Book not found"


class BookService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = BookRepository(session)

    async def get_book(self, isbn: str) -> BookRead:
        book = await self.repository.get_active_by_isbn(isbn)

        if book is None:
            raise BookError(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=BOOK_NOT_FOUND,
            )

        return BookRead.model_validate(book)

    async def create_book(self, payload: BookCreate) -> BookRead:
        async with self.session.begin():
            product = await self.repository.create(payload)

            if product is None:
                raise BookError(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="The book's ISBN already exists.",
                )

            response = BookRead.model_validate(product)

        return response

    async def update_product(self, isbn: str, payload: BookUpdate) -> BookRead:
        async with self.session.begin():
            book = await self.repository.update(isbn, payload)

            if book is None:
                raise BookError(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=BOOK_NOT_FOUND,
                )

            response = BookRead.model_validate(book)
        return response

    async def delete(self, isbn: str) -> None:
        async with self.session.begin():
            deleted = await self.repository.delete(isbn)

            if not deleted:
                raise BookError(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=BOOK_NOT_FOUND,
                )
