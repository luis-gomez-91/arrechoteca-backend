from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from database import get_db
from auth.dependencies import get_current_user, require_auth
from schemas.user import UserResponse, TokenPayload
import models

router = APIRouter(prefix="/api/auth", tags=["authentication"])

db_dependency = Annotated[Session, Depends(get_db)]

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: TokenPayload = Depends(get_current_user),
    db: db_dependency = None
):
    """Obtener información del usuario autenticado"""
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

@router.get("/protected")
async def protected_route(current_user: TokenPayload = Depends(require_auth)):
    """Ruta protegida"""
    return {
        "message": f"¡Hola {current_user.email}!",
        "user_id": current_user.sub,
        "authenticated": True
    }

@router.get("/test")
async def test_auth():
    """Test endpoint"""
    return {
        "message": "Auth router funcionando",
        "supabase_configured": bool(settings.supabase_url)
    }