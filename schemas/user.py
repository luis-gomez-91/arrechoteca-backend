from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    id: str  # UUID de Supabase

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TokenPayload(BaseModel):
    sub: str  # user id
    email: str
    exp: int
    iat: int


class ProtectedResponse(BaseModel):
    """Respuesta de ruta protegida."""
    message: str
    user_id: str
    authenticated: bool


class AuthTestResponse(BaseModel):
    """Respuesta del endpoint de prueba de auth."""
    message: str
    supabase_configured: bool