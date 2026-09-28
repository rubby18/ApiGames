from math import ceil

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.game import Game
from app.schemas.category import CategoryCreate, CategoryUpdate


def list_categories(db: Session, page: int, page_size: int) -> tuple[list[Category], int]:
    total = db.scalar(select(func.count()).select_from(Category)) or 0

    statement = (
        select(Category)
        .order_by(Category.name.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    categories = list(db.scalars(statement).all())
    return categories, total


def get_category(db: Session, category_id: int) -> Category | None:
    return db.get(Category, category_id)


def create_category(db: Session, data: CategoryCreate) -> Category:
    existing = db.scalar(select(Category).where(func.lower(Category.name) == data.name.lower()))
    if existing:
        raise ValueError("Ya existe una categoría con ese nombre.")

    category = Category(**data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category: Category, data: CategoryUpdate) -> Category:
    values = data.model_dump(exclude_unset=True)

    if "name" in values:
        existing = db.scalar(
            select(Category).where(
                func.lower(Category.name) == values["name"].lower(),
                Category.id != category.id,
            )
        )
        if existing:
            raise ValueError("Ya existe una categoría con ese nombre.")

    for field, value in values.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category: Category) -> None:
    games_count = db.scalar(
        select(func.count()).select_from(Game).where(Game.category_id == category.id)
    ) or 0

    if games_count:
        raise ValueError(
            "No se puede eliminar la categoría porque tiene videojuegos asociados."
        )

    db.delete(category)
    db.commit()
