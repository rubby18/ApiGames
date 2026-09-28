from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.schemas.common import PaginatedResponse
from app.services.category_service import (
    create_category,
    delete_category,
    get_category,
    list_categories,
    update_category,
)

router = APIRouter(prefix="/api/categories", tags=["Categories"])


def _to_response(category) -> CategoryResponse:
    return CategoryResponse(
        id=category.id,
        name=category.name,
        description=category.description,
        games_count=len(category.games),
    )


@router.get("", response_model=PaginatedResponse[CategoryResponse])
def read_categories(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    categories, total = list_categories(db, page, page_size)
    return PaginatedResponse(
        items=[_to_response(category) for category in categories],
        page=page,
        page_size=page_size,
        total=total,
        pages=ceil(total / page_size) if total else 0,
    )


@router.get("/{category_id}", response_model=CategoryResponse)
def read_category(category_id: int, db: Session = Depends(get_db)):
    category = get_category(db, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada.")
    return _to_response(category)


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_new_category(data: CategoryCreate, db: Session = Depends(get_db)):
    try:
        return _to_response(create_category(db, data))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/{category_id}", response_model=CategoryResponse)
def update_existing_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
):
    category = get_category(db, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada.")

    try:
        return _to_response(update_category(db, category, data))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error de integridad de datos.") from exc


@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
def delete_existing_category(category_id: int, db: Session = Depends(get_db)):
    category = get_category(db, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada.")

    try:
        delete_category(db, category)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"message": "Categoría eliminada correctamente."}
