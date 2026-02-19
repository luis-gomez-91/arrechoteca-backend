from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
from typing import Optional
import jwt
from config import settings
from schemas.user import TokenPayload

security = HTTPBearer(auto_error=False)

async def get_current_user(token: Optional[str] = Depends(security)) -> Optional[TokenPayload]:
    """
    Verificar token JWT de Supabase (opcional)
    """
    if not token:
        return None
    
    try:
        payload = jwt.decode(
            token.credentials,
            settings.supabase_jwt_secret,
            algorithms=["HS256"]
        )
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
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        payload = jwt.decode(
            token.credentials,
            settings.supabase_jwt_secret,
            algorithms=["HS256"]
        )
        return TokenPayload(**payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"JWT Error: {e}")
        raise HTTPException(status_code=401, detail="Token verification failed")