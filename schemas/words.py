from pydantic import BaseModel
from typing import List
from .categories import Category

class WordBase(BaseModel):
    word: str
    meaning: str


class WordCreate(WordBase):
    category_ids: List[int]

class Word(WordBase):
    id: int
    categories: List[Category] = []

    class Config:
        orm_mode = True

class WordExampleBase(BaseModel):
    text: str

    class Config:
        orm_mode = True