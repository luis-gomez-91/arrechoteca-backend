from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from schemas.words import Word, WordExampleBase, WordCreate
from models import Word as WordModel, WordExample as WordExampleModel
import models

router = APIRouter(
    prefix="/words",
    tags=["Palabras"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[Word])
def get_words(db: Session = Depends(get_db)):
    words = db.query(models.Word).all()
    return words

@router.get("/{word_id}/examples", response_model=List[WordExampleBase])
def get_examples(word_id: int, db: Session = Depends(get_db)):
    examples = db.query(models.WordExample).filter(models.WordExample.word_id == word_id).all()
    return examples

@router.post("/", response_model=Word)
def create_word(word_data: WordCreate, db: Session = Depends(get_db)):
    # Crear la palabra
    new_word = models.Word(word=word_data.word, meaning=word_data.meaning)

    # Buscar las categorías por ID
    categories = db.query(models.Category).filter(models.Category.id.in_(word_data.category_ids)).all()

    if not categories:
        raise HTTPException(status_code=400, detail="No se encontraron categorías con esos IDs")

    # Asociar las categorías a la palabra
    new_word.categories = categories

    # Guardar en la BD
    db.add(new_word)
    db.commit()
    db.refresh(new_word)

    return new_word

@router.post("/bulk", response_model=List[Word])
def create_words_bulk(words_data: List[WordCreate], db: Session = Depends(get_db)):
    created_words = []

    for word_data in words_data:
        new_word = models.Word(word=word_data.word, meaning=word_data.meaning)

        # Buscar las categorías por ID
        categories = db.query(models.Category).filter(models.Category.id.in_(word_data.category_ids)).all()
        if not categories:
            raise HTTPException(status_code=400, detail=f"No se encontraron categorías para {word_data.word}")

        new_word.categories = categories
        db.add(new_word)
        created_words.append(new_word)

    db.commit()

    for word in created_words:
        db.refresh(word)

    return created_words