from pydantic import BaseModel, ConfigDict, Field


class GameBase(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=1000)
    release_year: int | None = Field(default=None, ge=1950, le=2100)
    developer: str | None = Field(default=None, max_length=120)
    platform: str | None = Field(default=None, max_length=80)


class GameCreate(GameBase):
    category_id: int = Field(gt=0)


class GameUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=1000)
    release_year: int | None = Field(default=None, ge=1950, le=2100)
    developer: str | None = Field(default=None, max_length=120)
    platform: str | None = Field(default=None, max_length=80)
    category_id: int | None = Field(default=None, gt=0)


class CategoryEmbedded(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class GameResponse(GameBase):
    id: int
    category: CategoryEmbedded

    model_config = ConfigDict(from_attributes=True)
