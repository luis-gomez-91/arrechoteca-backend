import os
from fastapi import FastAPI, Depends
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
app = FastAPI(title="ANT Simulator", version="1.0")

# ------------------------------
# Configuración CORS
# ------------------------------
origins = [
    "https://luis-gomez-91.github.io",
    "https://www.luis-gomez-91.github.io",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Lista de URLs permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------
# Middleware de seguridad
# ------------------------------
# Redirigir a HTTPS solo en producción
if os.getenv("RAILWAY_ENVIRONMENT") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# Configurar TrustedHost (recomendado especificar hosts en producción)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],  # Cambiar "*" por tus dominios en producción
)

# ------------------------------
# Crear tablas de la base de datos
# ------------------------------
models.Base.metadata.create_all(bind=engine)

# ------------------------------
# Dependencia de base de datos
# ------------------------------
db_dependency = Annotated[Session, Depends(get_db)]

# ------------------------------
# Endpoints
# ------------------------------
@app.get("/")
def root():
    return {'status': 'success', 'message': 'Bienvenido a ANT Simulator - by Luis Gómez'}

# ------------------------------
# Routers (si tienes otros módulos)
# ------------------------------
from routers import categories, words
app.include_router(categories.router)
app.include_router(words.router)
