from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    description: str | None = Field(default=None, max_length=500)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=80)
    description: str | None = Field(default=None, max_length=500)


class CategorySummary(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class CategoryResponse(CategoryBase):
    id: int
    games_count: int

    model_config = ConfigDict(from_attributes=True)
