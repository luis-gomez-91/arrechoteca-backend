
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from typing import List

from database import get_db
from schemas import CategoryWithWords, Word
from models import Category as CategoryModel, Word as WordModel

router = APIRouter(
    prefix="/insults",
    tags=["Insults"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[CategoryWithWords])
def get_categories_with_words(db: Session = Depends(get_db)):
    categories = db.query(CategoryModel).options(joinedload(CategoryModel.words)).all()
    return categories

@router.get("/all", response_model=List[Word])
def get_all_words(db: Session = Depends(get_db)):
    words = db.query(WordModel).all()
    return words