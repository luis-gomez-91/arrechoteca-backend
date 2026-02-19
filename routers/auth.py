from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from database import get_db
from auth.dependencies import get_current_user, require_auth
from schemas.user import UserResponse, TokenPayload, ProtectedResponse, AuthTestResponse
from config import settings
import models

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])

db_dependency = Annotated[Session, Depends(get_db)]

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Usuario actual",
    description="Devuelve la información del usuario autenticado (JWT). Crea el usuario en BD si no existe.",
)
async def get_current_user_info(
    current_user: TokenPayload = Depends(get_current_user),
    db: db_dependency = None
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = current_user.sub
    email = current_user.email
    
    # Buscar o crear usuario en la base de datos
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        # Crear usuario si no existe (datos básicos desde JWT)
        db_user = models.User(
            id=user_id,
            email=email,
            full_name=None,  # Se puede actualizar después
            avatar_url=None
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    
    return db_user

@router.get(
    "/protected",
    response_model=ProtectedResponse,
    summary="Ruta protegida",
    description="Ejemplo de ruta que requiere autenticación. Devuelve saludo y datos del usuario.",
)
async def protected_route(current_user: TokenPayload = Depends(require_auth)):
    return {
        "message": f"¡Hola {current_user.email}!",
        "user_id": current_user.sub,
        "authenticated": True
    }

@router.get(
    "/test",
    response_model=AuthTestResponse,
    summary="Probar auth",
    description="Comprueba que el router de autenticación y la configuración de Supabase responden.",
)
async def test_auth():
    return {
        "message": "Auth router funcionando",
        "supabase_configured": bool(settings.supabase_url)
    }