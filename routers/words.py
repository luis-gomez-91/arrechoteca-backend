from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List

from database import get_db
from auth.dependencies import require_auth
from schemas.user import TokenPayload
from schemas.words import Word, WordExampleBase, WordCreate, WordExample, WordPaginated, WordDeleteResponse
import models

router = APIRouter(
    prefix="/words",
    tags=["Palabras"],
    responses={404: {"description": "Not found"}},
)

@router.get(
    "/",
    response_model=WordPaginated,
    summary="Listar palabras (paginado)",
    description="Devuelve palabras paginadas. Usa `skip` y `limit` para infinite scroll (ej: skip=0 limit=20, luego skip=20 limit=20).",
)
def get_words(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    if limit < 1 or limit > 100:
        limit = 20
    if skip < 0:
        skip = 0
    total = db.query(func.count(models.Word.id)).scalar() or 0
    words = (
        db.query(models.Word)
        .order_by(models.Word.word.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return WordPaginated(items=words, total=total, skip=skip, limit=limit)

@router.get(
    "/{word_id}/examples",
    response_model=List[WordExample],
    summary="Ejemplos de una palabra",
    description="Devuelve la lista de ejemplos de uso asociados a una palabra por su ID.",
)
def get_examples(word_id: int, db: Session = Depends(get_db)):
    examples = db.query(models.WordExample).filter(models.WordExample.word_id == word_id).all()
    return examples

@router.post(
    "/",
    response_model=Word,
    summary="Crear palabra",
    description="Crea una nueva palabra con su significado y la asocia a las categorías indicadas por ID. Requiere autenticación.",
)
def create_word(
    word_data: WordCreate,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_auth),
):
    # Crear la palabra
    new_word = models.Word(
        word=word_data.word,
        meaning=word_data.meaning,
        is_active=word_data.is_active,
    )

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

@router.post(
    "/bulk",
    response_model=List[Word],
    summary="Crear varias palabras",
    description="Crea múltiples palabras en una sola petición. Cada una debe incluir word, meaning y category_ids. Requiere autenticación.",
)
def create_words_bulk(
    words_data: List[WordCreate],
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_auth),
):
    created_words = []

    for word_data in words_data:
        new_word = models.Word(
            word=word_data.word,
            meaning=word_data.meaning,
            is_active=word_data.is_active,
        )

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


@router.delete(
    "/{word_id}",
    response_model=WordDeleteResponse,
    summary="Eliminar palabra",
    description="Elimina una palabra por ID. Devuelve confirmación y el ID eliminado.",
)
def delete_word(word_id: int, db: Session = Depends(get_db)):
    # Buscar la palabra por ID
    word = db.query(models.Word).filter(models.Word.id == word_id).first()
    
    if not word:
        raise HTTPException(
            status_code=404, 
            detail=f"Palabra con ID {word_id} no encontrada"
        )
    
    try:
        # Guardar el nombre de la palabra para el mensaje de respuesta
        word_name = word.word
        
        # Eliminar la palabra de la base de datos
        db.delete(word)
        db.commit()
        
        return {
            "success": True,
            "message": f"Palabra '{word_name}' eliminada exitosamente",
            "deleted_word_id": word_id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar la palabra: {str(e)}"
        )
    

    
@router.put(
    "/{word_id}",
    response_model=Word,
    summary="Actualizar palabra",
    description="Actualiza una palabra existente por ID (texto, significado y categorías).",
)
def update_word(word_id: int, word_data: WordCreate, db: Session = Depends(get_db)):
    # Buscar la palabra por ID
    word = db.query(models.Word).filter(models.Word.id == word_id).first()
    if not word:
        raise HTTPException(status_code=404, detail=f"Palabra con ID {word_id} no encontrada")

    # Actualizar campos
    word.word = word_data.word
    word.meaning = word_data.meaning
    word.is_active = word_data.is_active

    # Buscar las categorías por ID
    categories = db.query(models.Category).filter(models.Category.id.in_(word_data.category_ids)).all()
    if not categories:
        raise HTTPException(status_code=400, detail="No se encontraron categorías con esos IDs")

    # Asociar las categorías
    word.categories = categories

    # Guardar cambios
    db.commit()
    db.refresh(word)

    return word

@router.post(
    "/{word_id}/examples",
    response_model=Word,
    summary="Añadir ejemplo a una palabra",
    description="Añade un ejemplo de uso (texto) a una palabra existente por ID. Requiere autenticación.",
)
def add_examples_to_word(
    word_id: int,
    example_data: WordExampleBase,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(require_auth),
):
    word = db.query(models.Word).options(joinedload(models.Word.examples)).filter(models.Word.id == word_id).first()
    if not word:
        raise HTTPException(status_code=404, detail=f"Palabra con ID {word_id} no encontrada")

    new_example = models.WordExample(
        text=example_data.text,
        word_id=word_id,
        is_active=example_data.is_active,
    )
    db.add(new_example)
    db.commit()
    db.refresh(word)
    return word

