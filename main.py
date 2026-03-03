# main.py
import os
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Annotated
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

import models
from database import engine, get_db

# ------------------------------
# Cargar variables de entorno
# ------------------------------
load_dotenv()

# ------------------------------
# Inicializar la app
# ------------------------------
app = FastAPI(
    title="Arrechoteca",
    version="1.0",
    description="Diccionario de jerga guayaca: palabras y expresiones coloquiales de la costa ecuatoriana. Consulta significados, ejemplos y (con cuenta) comenta palabras o accede a insultos de la jerga.",
)

# ------------------------------
# Configuración CORS
# ------------------------------
# Origen exacto: sin barra final (el navegador envía "https://arrechoteca-web.vercel.app")
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://192.168.100.38:3000",
    "http://192.168.2.250:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://arrechoteca-web.vercel.app",
    "https://www.arrechoteca-web.vercel.app",
]

# CORS se añade primero para que envuelva todo (incluidas respuestas de error)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ------------------------------
# Middleware de seguridad
# ------------------------------
# Solo HTTPS en producción
if os.getenv("RAILWAY_ENVIRONMENT") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# TrustedHost
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],  # En producción, especifica tus dominios
)

# ------------------------------
# Crear tablas
# ------------------------------
models.Base.metadata.create_all(bind=engine)

# ------------------------------
# Dependencia DB
# ------------------------------
db_dependency = Annotated[Session, Depends(get_db)]

# ------------------------------
# Root endpoint
# ------------------------------
class RootResponse(BaseModel):
    status: str
    message: str


@app.get(
    "/",
    response_model=RootResponse,
    summary="Raíz",
    description="Mensaje de bienvenida a la API de Arrechoteca (diccionario de jerga guayaca).",
)
def root():
    return RootResponse(
        status="success",
        message="Diccionario de jerga guayaca: palabras y expresiones coloquiales de la costa ecuatoriana. Consulta significados, ejemplos y (con cuenta) comenta palabras o accede a insultos de la jerga.",
    )

# ------------------------------
# Routers
# ------------------------------
from routers import categories, words, auth, insults
app.include_router(categories.router)
app.include_router(words.router)
app.include_router(auth.router)
app.include_router(insults.router)