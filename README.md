# Arrechoteca

**Arrechoteca** es un diccionario de jerga guayaca: palabras y expresiones que se usan de forma coloquial en Ecuador, sobre todo en la costa (Guayaquil y alrededores). Aquí puedes consultar significados, ejemplos y, si creas una cuenta, comentar palabras o ver y comentar insultos típicos de esta jerga.

## ¿Qué es la jerga guayaca?

Es el conjunto de modismos, palabras y frases del habla informal de la costa ecuatoriana. Arrechoteca reúne ese vocabulario para que cualquiera pueda entenderlo, consultarlo y aportar con comentarios (con cuenta) o solo navegar y leer.

## Características

- **Palabras y significados**: Consulta términos de la jerga con su definición.
- **Categorías**: Las palabras están organizadas por categorías para facilitar la búsqueda.
- **Ejemplos**: Cada palabra puede tener ejemplos de uso.
- **Cuenta de usuario**: Crea una cuenta si quieres comentar palabras o acceder a la sección de insultos.
- **Insultos de la jerga**: Sección dedicada a insultos usados en esta jerga (acceso/comentarios con cuenta).

## API (backend)

Este repositorio es el **backend** de Arrechoteca: una API REST hecha con FastAPI que sirve palabras, categorías y ejemplos.

### Requisitos

- Python 3.x
- PostgreSQL (o variable de entorno `DATABASE_URL` configurada)

### Instalación y ejecución en local

1. Clona el repositorio y entra en la carpeta del proyecto.
2. Crea un entorno virtual y actívalo:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # source .venv/bin/activate   # Linux/macOS
   ```

3. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

4. Crea un archivo `.env` en la raíz con tu URL de base de datos:

   ```env
   DATABASE_URL=postgresql://usuario:password@host:puerto/nombre_db
   ```

5. Levanta el servidor:

   ```bash
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

6. Abre en el navegador: **http://localhost:8000**  
   Documentación interactiva: **http://localhost:8000/docs**

### Estructura del proyecto

- `main.py` — Punto de entrada y configuración de la API.
- `routers/` — Rutas de categorías, palabras e insultos.
- `models.py` — Modelos de base de datos (palabras, categorías, ejemplos, insultos, comentarios).
- `schemas/` — Esquemas Pydantic para request/response.
- `alembic/` — Migraciones de base de datos.

### Admin de puteadas (insultos)

Para integrar el panel de administración de insultos/puteadas con la API, usa la guía **[ADMIN_PUTEADAS.md](ADMIN_PUTEADAS.md)**: endpoints, métodos, cuerpos de petición y autenticación. La documentación interactiva está en **http://localhost:8000/docs** (tag «Bad Words»).

## Autor

Luis Gómez
