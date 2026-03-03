from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
from typing import Optional
import os
import jwt
from jwt import PyJWKClient
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from schemas.user import TokenPayload
import models

# En macOS, Python a veces no encuentra los certificados SSL; certifi los proporciona.
try:
    import certifi
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
except ImportError:
    pass

security = HTTPBearer(auto_error=False)

# JWKS de Supabase para verificar tokens ES256 (clave asimétrica)
def _get_jwks_client() -> PyJWKClient:
    jwks_url = f"{settings.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
    return PyJWKClient(jwks_url)


def _decode_supabase_token(token_str: str):
    """Decodifica y verifica un JWT de Supabase (HS256 legacy o ES256 con JWKS)."""
    header = jwt.get_unverified_header(token_str)
    alg = header.get("alg")

    if alg == "ES256":
        jwks_client = _get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token_str)
        return jwt.decode(
            token_str,
            signing_key.key,
            algorithms=["ES256"],
            audience="authenticated",
            options={"verify_aud": True},
        )
    if alg == "HS256":
        return jwt.decode(
            token_str,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
        )
    raise jwt.InvalidTokenError(f"Algoritmo no permitido: {alg}")


async def get_current_user(token: Optional[str] = Depends(security)) -> Optional[TokenPayload]:
    """
    Verificar token JWT de Supabase (opcional)
    """
    if not token:
        return None

    try:
        payload = _decode_supabase_token(token.credentials)
        return TokenPayload(**payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"JWT Error: {e}")
        raise HTTPException(status_code=401, detail="Token verification failed")


async def require_auth(token: str = Depends(security)) -> TokenPayload:
    """
    Require authentication - lanza error si no hay token válido
    """
    token_value = token.credentials if token else None
    print("[require_auth] Token recibido:", token_value if token_value else "(ninguno)")

    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        payload = _decode_supabase_token(token.credentials)
        return TokenPayload(**payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        print(f"[require_auth] Invalid token - error: {e}, token (primeros 50 chars): {token.credentials[:50] if token.credentials else ''}...")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"JWT Error: {e}")
        raise HTTPException(status_code=401, detail="Token verification failed")


def ensure_user_in_db(
    current_user: TokenPayload = Depends(require_auth),
    db: Session = Depends(get_db),
) -> TokenPayload:
    """
    Requiere autenticación y asegura que el usuario exista en la tabla users
    (upsert por id). Usar en rutas que escriben user_id en tablas con FK a users.
    """
    user = db.query(models.User).filter(models.User.id == current_user.sub).first()
    if not user:
        user = models.User(
            id=current_user.sub,
            email=current_user.email,
            full_name=None,
            avatar_url=None,
        )
        db.add(user)
        db.commit()
    return current_user