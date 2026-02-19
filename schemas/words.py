from pydantic import BaseModel
from typing import List
from .categories import Category


class WordPaginated(BaseModel):
    """Respuesta paginada de palabras (para infinite scroll)."""
    items: List["Word"]
    total: int
    skip: int
    limit: int

    class Config:
        from_attributes = True


class WordDeleteResponse(BaseModel):
    """Respuesta al eliminar una palabra."""
    success: bool
    message: str
    deleted_word_id: int


class WordExampleBase(BaseModel):
    text: str
    is_active: bool = False

class WordExample(WordExampleBase):
    id: int
    word_id: int | None = None
    is_active: bool = False

    class Config:
        from_attributes = True

class WordBase(BaseModel):
    word: str
    meaning: str
    is_active: bool = False

class WordCreate(WordBase):
    category_ids: List[int]

class Word(WordBase):
    id: int
    categories: List[Category] = []
    examples: List[WordExample] = []
    is_active: bool = False

    class Config:
        from_attributes = True