from sqlalchemy import delete as sql_delete
from sqlalchemy import select
from sqlalchemy import update as sql_update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession

from app.book.models import Book
from app.book.schemas import BookCreate, BookUpdate


class BookRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_active(
        self,
        *,
        limit: int,
        offset: int,
    ) -> tuple[list[Book], bool]:
        """Retrieve a page of active books ordered by ID in ascending order.

        Args:
            limit: Maximum number of books to return in the page.
            offset: Number of active books to skip from the beginning of the results.

        Returns:
            tuple[list[Book], bool]: The books on the page and a flag indicating
                whether more active books follow. The query requests one extra row
                to determine the flag's value.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: If the database query fails.
        """
        statement = (
            select(Book)
            .where(Book.is_active.is_(True))
            .order_by(Book.id)
            .offset(offset)
            .limit(limit + 1)
        )

        result = await self.session.scalars(statement)
        products = list(result.all())
        has_more = len(products) > limit

        return products[:limit], has_more

    async def get_active_by_isbn(
        self,
        isbn: str,
    ) -> Book | None:
        """Find an active book by its isbn.

        Args:
            isbn: The isbn of the book to look up.

        Returns:
            Book | None: The book if it exists and is active, or `None` if no book
                has that isbn or the book is inactive.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: If the database query fails.
        """
        statement = select(Book).where(
            Book.isbn == isbn,
            Book.is_active.is_(True),
        )

        result = await self.session.scalars(statement)
        return result.one_or_none()

    async def create(self, payload: BookCreate) -> Book | None:
        """Insert a book if its ISBN is unique.

        The method uses the current transaction. The caller is responsible for
        committing it.

        Args:
            payload: Data for the book to insert.

        Returns:
            Book | None: The inserted book, or `None` if PostgreSQL skips the
                insert because of an ISBN conflict.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: If the operation fails, for example,
                because the connection is lost or the insert violates another
                database constraint.
        """
        statement = (
            insert(Book)
            .values(**payload.model_dump())
            .on_conflict_do_nothing(index_elements=[Book.isbn])
            .returning(Book)
        )

        result: ScalarResult[Book] = await self.session.scalars(statement)
        return result.one_or_none()

    async def update(self, isbn: str, payload: BookUpdate) -> Book | None:
        """Update an active book by ISBN.

        Only fields explicitly supplied in the payload are updated.
        An empty payload returns the current book without modifying it.

        Args:
            isbn: ISBN of the book to update.
            payload: Fields to update and their new values.

        Returns:
            Book | None: The book with its current values, or `None` if
                no active book has the given ISBN.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: If the database operation fails.
        """
        changes = payload.model_dump(exclude_unset=True)

        if not changes:
            return await self.get_active_by_isbn(isbn)

        statement = (
            sql_update(Book).where(Book.isbn == isbn).values(changes).returning(Book)
        )

        result: ScalarResult[Book] = await self.session.scalars(statement)
        return result.one_or_none()

    async def delete(self, isbn: str) -> bool:
        """Permanently delete a book by ISBN.

        Args:
            isbn: ISBN of the book to delete.

        Returns:
            bool: True if a book was deleted, False otherwise.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: If the delete operation fails.
        """
        statement = sql_delete(Book).where(Book.isbn == isbn).returning(Book.id)

        result: ScalarResult[int] = await self.session.scalars(statement)
        return result.one_or_none() is not None
