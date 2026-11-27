from typing import Annotated

from fastapi import APIRouter, Path, Query, status
from fastapi.responses import JSONResponse

from app.api.dependencies import BookServiceDep, SessionDep
from app.book.repository import BookRepository
from app.book.schemas import BookCreate, BookPage, BookRead, BookUpdate
from app.core.exceptions import BookError

router = APIRouter()


@router.get("", response_model=BookPage, status_code=status.HTTP_200_OK)
async def list_books(
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0, le=10_000)] = 0,
) -> BookPage:
    repository = BookRepository(session)

    books, has_more = await repository.list_active(
        limit=limit,
        offset=offset,
    )

    return BookPage(
        items=[BookRead.model_validate(book) for book in books],
        limit=limit,
        offset=offset,
        has_more=has_more,
    )


@router.get("/{isbn}", response_model=BookRead, status_code=status.HTTP_200_OK)
async def get_book(
    isbn: Annotated[str, Path(gt="")],
    service: BookServiceDep,
) -> BookRead | JSONResponse:
    try:
        return await service.get_book(isbn)
    except BookError as exc:
        return JSONResponse(
            status_code=exc.status_code, content={"message": str(exc.detail)}
        )
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "An error occurred while searching for the product"},
        )


@router.post(
    "",
    response_model=BookRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_book(
    payload: BookCreate,
    service: BookServiceDep,
) -> BookRead | JSONResponse:
    try:
        return await service.create_book(payload)
    except BookError as exc:
        return JSONResponse(
            status_code=exc.status_code, content={"message": str(exc.detail)}
        )
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "The book could not be created"},
        )


@router.patch("/{isbn}", response_model=BookRead)
async def update_book(
    isbn: Annotated[str, Path(min_length=1)],
    payload: BookUpdate,
    service: BookServiceDep,
) -> JSONResponse:
    try:
        await service.update_product(isbn, payload)
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"message": "Updated book"}
        )
    except BookError as exc:
        return JSONResponse(
            status_code=exc.status_code, content={"message": str(exc.detail)}
        )
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "An error occurred while updating product"},
        )


@router.delete("/{isbn}")
async def delete_book(
    isbn: Annotated[str, Path(min_length=1)],
    service: BookServiceDep,
) -> JSONResponse:
    try:
        await service.delete(isbn)
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"message": "Delete book"}
        )
    except BookError as exc:
        return JSONResponse(
            status_code=exc.status_code, content={"message": str(exc.detail)}
        )
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "An error occurred while deleting the product A"},
        )
