# Ideas para ampliar la sección de insultos

Resumen de lo ya implementado y recomendaciones para seguir creciendo.

---

## Ya implementado

- **Varios ejemplos por insulto** (relación `InsultExample`).
- **Un tag por insulto** (ej. regionales, fuertes): tabla `insult_tags`, endpoints `GET/POST /bad_words/tags`.
- **Comentarios** en insultos (con respuestas en hilo).
- **Estrellita por comentario**: un usuario puede dar una estrellita por comentario (`POST /bad_words/comments/{id}/star`).
- **Like por insulto**: un usuario puede dar like una vez por insulto (`POST /bad_words/{id}/like`).

---

## Recomendaciones de ideas

1. **Filtrar por tag**  
   - `GET /bad_words?tag_id=1` para listar solo insultos de un tag (regionales, fuertes, etc.).

2. **Ordenar por popularidad**  
   - `GET /bad_words?sort=likes` o `sort=comments` para ordenar por más likes o más comentarios.

3. **Reportar insulto o comentario**  
   - Tabla `reports` (insult_id o comment_id, user_id, reason) y endpoint para crear reporte (requiere auth). Útil para moderación.

4. **Favoritos / “Guardados”**  
   - Tabla `user_favorite_insults` (user_id, insult_id). Endpoint para marcar/desmarcar favorito y listar “Mis insultos guardados”.

5. **Historial de “vistos”**  
   - Guardar últimos insultos vistos por usuario (por ejemplo en una tabla o en el front con localStorage) para “Continuar viendo” o “Vistos recientemente”.

6. **Búsqueda**  
   - `GET /bad_words?q=malparido` para filtrar por texto en insulto o significado.

7. **Traducción o variantes**  
   - Campo opcional en el insulto: “variante” o “traducción al estándar” para mostrar alternativas o explicar la forma “suave”.

8. **Nivel de intensidad**  
   - Campo numérico (1–5) o segundo tag “intensidad” (leve / medio / fuerte) para filtrar o advertir en el front.

9. **Compartir**  
   - Endpoint o helper que devuelva una URL o metadatos para compartir un insulto (ej. `/bad_words/123` con OG tags en el front).

10. **Estadísticas**  
    - Endpoint tipo `GET /bad_words/stats`: insulto más likeado, más comentado, tag más usado, etc., para rankings o dashboard.

11. **Moderación de comentarios**  
    - Campo `is_hidden` o `moderated` en comentarios y endpoint (protegido por rol admin) para ocultar o eliminar.

12. **Notificaciones**  
    - Cuando alguien responde a tu comentario o da estrellita a tu comentario, guardar evento en una tabla `notifications` y luego exponer `GET /notifications` para el usuario.

Si quieres, se puede bajar cualquiera de estas ideas a esquema de BD y endpoints concretos en el backend.