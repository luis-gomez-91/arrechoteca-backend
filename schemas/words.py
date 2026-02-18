from pydantic import BaseModel
from typing import List
from .categories import Category


class WordExampleBase(BaseModel):
    text: str

class WordExample(WordExampleBase):
    id: int

    class Config:
        orm_mode = True

class WordBase(BaseModel):
    word: str
    meaning: str

class WordCreate(WordBase):
    category_ids: List[int]

class Word(WordBase):
    id: int
    categories: List[Category] = []
    examples: List[WordExample] = []

    class Config:
        orm_mode = True