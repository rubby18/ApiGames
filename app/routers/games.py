from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.game import GameCreate, GameResponse, GameUpdate
from app.services.game_service import (
    create_game,
    delete_game,
    get_game,
    list_games,
    update_game,
)

router = APIRouter(prefix="/api/games", tags=["Games"])


@router.get("", response_model=PaginatedResponse[GameResponse])
def read_games(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = Query(None, max_length=100),
    category_id: int | None = Query(None, gt=0),
    db: Session = Depends(get_db),
):
    games, total = list_games(db, page, page_size, search, category_id)
    return PaginatedResponse(
        items=games,
        page=page,
        page_size=page_size,
        total=total,
        pages=ceil(total / page_size) if total else 0,
    )


@router.get("/{game_id}", response_model=GameResponse)
def read_game(game_id: int, db: Session = Depends(get_db)):
    game = get_game(db, game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Videojuego no encontrado.")
    return game


@router.post("", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
def create_new_game(data: GameCreate, db: Session = Depends(get_db)):
    try:
        return create_game(db, data)
    except LookupError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/{game_id}", response_model=GameResponse)
def update_existing_game(
    game_id: int,
    data: GameUpdate,
    db: Session = Depends(get_db),
):
    game = get_game(db, game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Videojuego no encontrado.")

    try:
        return update_game(db, game, data)
    except LookupError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/{game_id}", status_code=status.HTTP_200_OK)
def delete_existing_game(game_id: int, db: Session = Depends(get_db)):
    game = get_game(db, game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="Videojuego no encontrado.")

    delete_game(db, game)
    return {"message": "Videojuego eliminado correctamente."}
