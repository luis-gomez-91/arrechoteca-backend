
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from database import get_db
from auth.dependencies import require_auth
from schemas.user import TokenPayload
from schemas.insults import Insult, InsultBase, InsultExampleBase
import models

router = APIRouter(
    prefix="/bad_words",
    tags=["Bad Words"],
    responses={404: {"description": "Not found"}},
)

@router.get(
    "/",
    response_model=List[Insult],
    summary="Listar insultos / puteadas",
    description="Devuelve todas las palabras fuertes o insultos de la jerga con sus ejemplos.",
)
def get_bad_words(db: Session = Depends(get_db)):
    bad_words = db.query(models.Insult).options(joinedload(models.Insult.examples)).all()
    return bad_words

@router.post(
    "/",
    response_model=Insult,
    summary="Crear insulto / puteada",
    description="Añade un nuevo insulto o expresión fuerte con su significado. Requiere autenticación.",
)
def create_bad_word(
    bad_word_data: InsultBase,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_auth),
):
    new_bad_word = models.Insult(
        insult=bad_word_data.insult,
        meaning=bad_word_data.meaning,
        is_active=bad_word_data.is_active,
    )
    db.add(new_bad_word)
    db.commit()
    db.refresh(new_bad_word)
    return new_bad_word

@router.put(
    "/{id}",
    response_model=Insult,
    summary="Actualizar insulto / puteada",
    description="Actualiza un insulto existente por ID (texto y significado).",
)
def update_word(id: int, insult_data: InsultBase, db: Session = Depends(get_db)):
    # Buscar la palabra por ID
    bad_word = db.query(models.Insult).filter(models.Insult.id == id).first()

    if not bad_word:
        raise HTTPException(status_code=404, detail=f"Puteada con ID {id} no encontrada")

    # Actualizar campos
    bad_word.insult = insult_data.insult
    bad_word.meaning = insult_data.meaning
    bad_word.is_active = insult_data.is_active

    # Guardar cambios
    db.commit()
    db.refresh(bad_word)

    return bad_word


@router.post(
    "/{insult_id}/examples",
    response_model=Insult,
    summary="Añadir ejemplo a un insulto",
    description="Añade un ejemplo de uso a un insulto existente por ID. Requiere autenticación.",
)
def add_example_to_insult(
    insult_id: int,
    example_data: InsultExampleBase,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_auth),
):
    insult = db.query(models.Insult).options(joinedload(models.Insult.examples)).filter(models.Insult.id == insult_id).first()
    if not insult:
        raise HTTPException(status_code=404, detail=f"Insulto con ID {insult_id} no encontrado")
    new_example = models.InsultExample(
        text=example_data.text,
        insult_id=insult_id,
        is_active=example_data.is_active,
    )
    db.add(new_example)
    db.commit()
    db.refresh(insult)
    return insult


# @router.get("/{word_id}", response_model=List[Word])
# def get_word_examples(word_id:int, db: Session = Depends(get_db)):
#     word = db.query(models.Word).filter(models.Word.id == word_id).first()

#     examples = db.query(models.WordExample).filter()

#     return words