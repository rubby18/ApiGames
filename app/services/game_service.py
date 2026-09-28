from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.category import Category
from app.models.game import Game
from app.schemas.game import GameCreate, GameUpdate


def list_games(
    db: Session,
    page: int,
    page_size: int,
    search: str | None,
    category_id: int | None,
) -> tuple[list[Game], int]:
    conditions = []

    if search:
        term = f"%{search.strip()}%"
        conditions.append(
            or_(
                Game.title.ilike(term),
                Game.developer.ilike(term),
                Game.platform.ilike(term),
            )
        )

    if category_id is not None:
        conditions.append(Game.category_id == category_id)

    base = select(Game)
    count_query = select(func.count()).select_from(Game)

    if conditions:
        base = base.where(*conditions)
        count_query = count_query.where(*conditions)

    total = db.scalar(count_query) or 0

    statement = (
        base.options(joinedload(Game.category))
        .order_by(Game.title.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    return list(db.scalars(statement).unique().all()), total


def get_game(db: Session, game_id: int) -> Game | None:
    statement = (
        select(Game)
        .options(joinedload(Game.category))
        .where(Game.id == game_id)
    )
    return db.scalar(statement)


def _ensure_category(db: Session, category_id: int) -> None:
    if db.get(Category, category_id) is None:
        raise LookupError("La categoría indicada no existe.")


def create_game(db: Session, data: GameCreate) -> Game:
    _ensure_category(db, data.category_id)

    game = Game(**data.model_dump())
    db.add(game)
    db.commit()
    db.refresh(game)
    return get_game(db, game.id)


def update_game(db: Session, game: Game, data: GameUpdate) -> Game:
    values = data.model_dump(exclude_unset=True)

    if "category_id" in values:
        _ensure_category(db, values["category_id"])

    for field, value in values.items():
        setattr(game, field, value)

    db.commit()
    db.refresh(game)
    return get_game(db, game.id)


def delete_game(db: Session, game: Game) -> None:
    db.delete(game)
    db.commit()
