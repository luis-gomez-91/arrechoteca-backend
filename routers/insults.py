
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from database import get_db
from schemas.insults import Insult, InsultBase, InsultBase
import models

router = APIRouter(
    prefix="/bad_words",
    tags=["Bad Words"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[Insult])
def get_bad_words(db: Session = Depends(get_db)):
    bad_words = db.query(models.Insult).options(joinedload(models.Insult.examples)).all()
    return bad_words

@router.post("/", response_model=Insult)
def create_bad_word(bad_word_data: InsultBase, db: Session = Depends(get_db)):
    new_bad_word = models.Insult(insult=bad_word_data.insult, meaning=bad_word_data.meaning)
    db.add(new_bad_word)
    db.commit()
    db.refresh(new_bad_word)
    return new_bad_word

@router.put("/{id}", response_model=Insult)
def update_word(id: int, insult_data: InsultBase, db: Session = Depends(get_db)):
    # Buscar la palabra por ID
    bad_word = db.query(models.Insult).filter(models.Insult.id == id).first()

    if not bad_word:
        raise HTTPException(status_code=404, detail=f"Puteada con ID {id} no encontrada")

    # Actualizar campos
    bad_word.insult = insult_data.insult
    bad_word.meaning = insult_data.meaning

    # Guardar cambios
    db.commit()
    db.refresh(bad_word)

    return bad_word


# @router.get("/{word_id}", response_model=List[Word])
# def get_word_examples(word_id:int, db: Session = Depends(get_db)):
#     word = db.query(models.Word).filter(models.Word.id == word_id).first()

#     examples = db.query(models.WordExample).filter()

#     return words