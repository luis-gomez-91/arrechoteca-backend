from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models
from schemas.categories import Category
from schemas.words import WordBase

router = APIRouter(
    prefix="/categories",
    tags=["Categorías"],
    responses={404: {"description": "Not found"}},
)

@router.get(
    "/",
    response_model=List[Category],
    summary="Listar categorías",
    description="Devuelve todas las categorías disponibles para clasificar palabras de la jerga.",
)
async def get_all_categories(db: Session = Depends(get_db)):
    categories = db.query(models.Category).all()
    return categories

@router.get(
    "/{category_id}/words",
    response_model=List[WordBase],
    summary="Palabras por categoría",
    description="Devuelve todas las palabras asociadas a una categoría por su ID.",
)
def get_words_by_category(category_id: int, db: Session = Depends(get_db)):
    # Verificar si la categoría existe
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no existe")
    
    # Traer todas las palabras asociadas a esa categoría
    words = category.words  # gracias al relationship many-to-many
    return words