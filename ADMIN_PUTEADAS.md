# Admin de Puteadas (Insultos) — Guía de API

Base URL de la API (ej. local): `http://localhost:8000`  
Prefijo de puteadas: **`/bad_words`**

Todas las rutas que requieren autenticación deben enviar el header:

```http
Authorization: Bearer <access_token>
```

(el token de Supabase tras login).

---

## 1. Tags

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/bad_words/tags` | No | Listar todos los tags |
| POST | `/bad_words/tags` | Sí | Crear tag |
| PUT | `/bad_words/tags/{tag_id}` | Sí | Actualizar tag |
| DELETE | `/bad_words/tags/{tag_id}` | Sí | Eliminar tag |

**POST /bad_words/tags** — Body:
```json
{ "name": "Insultos regionales" }
```

**PUT /bad_words/tags/{tag_id}** — Body:
```json
{ "name": "Nuevo nombre" }
```

**Respuesta tag:** `{ "id": 1, "name": "..." }`

---

## 2. Insultos (CRUD)

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/bad_words/` | No | Listar todos los insultos |
| GET | `/bad_words/{id}` | No | Obtener un insulto por ID |
| POST | `/bad_words/` | Sí | Crear insulto |
| PUT | `/bad_words/{id}` | Sí | Actualizar insulto |
| DELETE | `/bad_words/{id}` | Sí | Eliminar insulto |

**POST /bad_words/** — Body:
```json
{
  "insult": "malparido",
  "meaning": "Insulto muy usado en la costa.",
  "is_active": true,
  "tag_id": 1
}
```
`tag_id` es opcional (puede ser `null`).

**PUT /bad_words/{id}** — Body: mismo que arriba.

**Respuesta insulto (GET lista o por id):**
```json
{
  "id": 1,
  "insult": "malparido",
  "meaning": "...",
  "is_active": true,
  "tag_id": 1,
  "tag": { "id": 1, "name": "Insultos regionales" },
  "examples": [
    { "id": 1, "text": "...", "insult_id": 1, "is_active": true }
  ],
  "likes_count": 5,
  "comments_count": 3,
  "liked_by_me": false
}
```

**DELETE /bad_words/{id}** — Respuesta:
```json
{ "success": true, "message": "Insulto '...' eliminado", "deleted_id": 1 }
```

---

## 3. Ejemplos de un insulto

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/bad_words/{insult_id}/examples` | No | Listar ejemplos |
| POST | `/bad_words/{insult_id}/examples` | Sí | Añadir ejemplo |
| PUT | `/bad_words/examples/{example_id}` | Sí | Editar ejemplo |
| DELETE | `/bad_words/examples/{example_id}` | Sí | Eliminar ejemplo |

**POST /bad_words/{insult_id}/examples** — Body:
```json
{ "text": "Ese malparido se fue sin pagar.", "is_active": true }
```

**PUT /bad_words/examples/{example_id}** — Body: mismo.

**Respuesta ejemplo:** `{ "id": 1, "text": "...", "insult_id": 1, "is_active": true }`

---

## 4. Likes (insulto)

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| POST | `/bad_words/{insult_id}/like` | Sí | Toggle like (dar o quitar) |

**Respuesta:** `{ "liked": true, "likes_count": 6 }`

---

## 5. Comentarios

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/bad_words/{insult_id}/comments` | No | Listar comentarios (con respuestas) |
| POST | `/bad_words/{insult_id}/comments` | Sí | Crear comentario o respuesta |
| PUT | `/bad_words/comments/{comment_id}` | Sí | Editar (solo autor) |
| DELETE | `/bad_words/comments/{comment_id}` | Sí | Eliminar (solo autor) |

**POST /bad_words/{insult_id}/comments** — Body comentario nuevo:
```json
{ "comment": "Muy usado en Guayaquil.", "parent_id": null }
```

**Respuesta (respuesta a otro comentario):**
```json
{ "comment": "Total.", "parent_id": 5 }
```

**POST /bad_words/comments/{comment_id}/star** — Toggle estrellita (auth).  
**Respuesta:** `{ "starred": true, "star_count": 2 }`

**Respuesta comentario (GET comments):**
```json
{
  "id": 1,
  "insult_id": 1,
  "user_id": "uuid-supabase",
  "comment": "...",
  "created_at": "2026-02-19T...",
  "parent_id": null,
  "user": { "id": "...", "full_name": "...", "avatar_url": "..." },
  "star_count": 1,
  "starred_by_me": false,
  "replies": [ ... ]
}
```

---

## Resumen para el admin

- **Listar puteadas:** `GET /bad_words/`
- **Crear puteada:** `POST /bad_words/` (body: insult, meaning, is_active, tag_id opcional).
- **Editar puteada:** `PUT /bad_words/{id}` (mismo body).
- **Eliminar puteada:** `DELETE /bad_words/{id}`.
- **Tags:** `GET /bad_words/tags` para selector; `POST /bad_words/tags` para crear; PUT/DELETE con `{tag_id}`.
- **Ejemplos:** GET/POST en `/bad_words/{insult_id}/examples`; PUT/DELETE en `/bad_words/examples/{example_id}`.

Todas las escrituras (POST, PUT, DELETE) requieren `Authorization: Bearer <token>`.

Documentación interactiva: **http://localhost:8000/docs** (tag "Bad Words").
