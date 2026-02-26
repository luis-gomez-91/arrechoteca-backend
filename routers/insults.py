from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func
from typing import List, Optional

from database import get_db
from auth.dependencies import require_auth, get_current_user, ensure_user_in_db
from schemas.user import TokenPayload
from schemas.insults import (
    Insult,
    InsultBase,
    InsultCreate,
    InsultExampleBase,
    InsultExample,
    InsultTag,
    InsultTagCreate,
    InsultComment,
    InsultCommentCreate,
    InsultCommentUpdate,
    LikeResponse,
    StarResponse,
    InsultDeleteResponse,
    DeleteResponse,
)
import models

router = APIRouter(
    prefix="/bad_words",
    tags=["Bad Words"],
    responses={404: {"description": "Not found"}},
)


def _insult_with_counts(insult: models.Insult, user_id: Optional[str] = None) -> Insult:
    """Construye respuesta de insulto con comments_count, star_count y starred_by_me."""
    stars = insult.stars or []
    return Insult(
        id=insult.id,
        insult=insult.insult,
        meaning=insult.meaning,
        is_active=insult.is_active,
        tag_id=insult.tag_id,
        tag=insult.tag,
        examples=insult.examples,
        comments_count=len(insult.comments) if insult.comments else 0,
        star_count=len(stars),
        starred_by_me=any(s.user_id == user_id for s in stars) if user_id else False,
    )


# ----- Tags -----
@router.get(
    "/tags",
    response_model=List[InsultTag],
    summary="Listar tags de insultos",
    description="Devuelve todos los tags (ej. regionales, fuertes).",
)
def list_insult_tags(db: Session = Depends(get_db)):
    return db.query(models.InsultTag).order_by(models.InsultTag.name).all()


@router.post(
    "/tags",
    response_model=InsultTag,
    summary="Crear tag de insultos",
    description="Crea un nuevo tag. Requiere autenticación.",
)
def create_insult_tag(
    data: InsultTagCreate,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(ensure_user_in_db),
):
    existing = db.query(models.InsultTag).filter(models.InsultTag.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Ya existe el tag '{data.name}'")
    tag = models.InsultTag(name=data.name)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@router.put(
    "/tags/{tag_id}",
    response_model=InsultTag,
    summary="Actualizar tag de insultos",
    description="Actualiza el nombre de un tag. Requiere autenticación.",
)
def update_insult_tag(
    tag_id: int,
    data: InsultTagCreate,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(ensure_user_in_db),
):
    tag = db.query(models.InsultTag).filter(models.InsultTag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag no encontrado")
    existing = db.query(models.InsultTag).filter(models.InsultTag.name == data.name, models.InsultTag.id != tag_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Ya existe otro tag con el nombre '{data.name}'")
    tag.name = data.name
    db.commit()
    db.refresh(tag)
    return tag


@router.delete(
    "/tags/{tag_id}",
    response_model=DeleteResponse,
    summary="Eliminar tag de insultos",
    description="Elimina un tag. Los insultos que lo usen quedarán con tag_id null. Requiere autenticación.",
)
def delete_insult_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(ensure_user_in_db),
):
    tag = db.query(models.InsultTag).filter(models.InsultTag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag no encontrado")
    db.query(models.Insult).filter(models.Insult.tag_id == tag_id).update({models.Insult.tag_id: None})
    db.delete(tag)
    db.commit()
    return DeleteResponse(success=True, message=f"Tag '{tag.name}' eliminado")


# ----- Insultos -----
@router.get(
    "/",
    response_model=List[Insult],
    summary="Listar insultos / puteadas",
    description="Devuelve todos los insultos con ejemplos, tag y conteo de likes y comentarios.",
)
def get_bad_words(
    db: Session = Depends(get_db),
    current_user: Optional[TokenPayload] = Depends(get_current_user),
):
    rows = (
        db.query(models.Insult)
        .options(
            joinedload(models.Insult.examples),
            joinedload(models.Insult.tag),
            selectinload(models.Insult.stars),
            selectinload(models.Insult.comments),
        )
        .order_by(models.Insult.insult.asc())
        .all()
    )
    user_id = current_user.sub if current_user else None
    return [_insult_with_counts(r, user_id) for r in rows]


@router.post(
    "/",
    response_model=Insult,
    summary="Crear insulto / puteada",
    description="Añade un nuevo insulto. Opcionalmente asigna tag_id. Requiere autenticación.",
)
def create_bad_word(
    data: InsultCreate,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(ensure_user_in_db),
):
    new_insult = models.Insult(
        insult=data.insult,
        meaning=data.meaning,
        is_active=data.is_active,
        tag_id=data.tag_id,
    )
    db.add(new_insult)
    db.commit()
    db.refresh(new_insult)
    row = (
        db.query(models.Insult)
        .options(
            joinedload(models.Insult.examples),
            joinedload(models.Insult.tag),
            selectinload(models.Insult.stars),
            selectinload(models.Insult.comments),
        )
        .filter(models.Insult.id == new_insult.id)
        .first()
    )
    return _insult_with_counts(row, current_user.sub)


@router.put(
    "/{id}",
    response_model=Insult,
    summary="Actualizar insulto / puteada",
    description="Actualiza un insulto por ID (texto, significado, tag). Requiere autenticación.",
)
def update_bad_word(
    id: int,
    data: InsultBase,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(ensure_user_in_db),
):
    insult = (
        db.query(models.Insult)
        .options(
            joinedload(models.Insult.examples),
            joinedload(models.Insult.tag),
            selectinload(models.Insult.stars),
            selectinload(models.Insult.comments),
        )
        .filter(models.Insult.id == id)
        .first()
    )
    if not insult:
        raise HTTPException(status_code=404, detail=f"Insulto con ID {id} no encontrado")
    insult.insult = data.insult
    insult.meaning = data.meaning
    insult.is_active = data.is_active
    insult.tag_id = data.tag_id
    db.commit()
    db.refresh(insult)
    return _insult_with_counts(insult, current_user.sub)


@router.get(
    "/{id}",
    response_model=Insult,
    summary="Obtener un insulto por ID",
    description="Devuelve un insulto con ejemplos, tag, conteos y liked_by_me si estás autenticado.",
)
def get_bad_word_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: Optional[TokenPayload] = Depends(get_current_user),
):
    insult = (
        db.query(models.Insult)
        .options(
            joinedload(models.Insult.examples),
            joinedload(models.Insult.tag),
            selectinload(models.Insult.stars),
            selectinload(models.Insult.comments),
        )
        .filter(models.Insult.id == id)
        .first()
    )
    if not insult:
        raise HTTPException(status_code=404, detail=f"Insulto con ID {id} no encontrado")
    return _insult_with_counts(insult, current_user.sub if current_user else None)


@router.delete(
    "/{id}",
    response_model=InsultDeleteResponse,
    summary="Eliminar insulto",
    description="Elimina un insulto por ID. Requiere autenticación.",
)
def delete_bad_word(
    id: int,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(ensure_user_in_db),
):
    insult = db.query(models.Insult).filter(models.Insult.id == id).first()
    if not insult:
        raise HTTPException(status_code=404, detail=f"Insulto con ID {id} no encontrado")
    name = insult.insult
    db.delete(insult)
    db.commit()
    return InsultDeleteResponse(success=True, message=f"Insulto '{name}' eliminado", deleted_id=id)


@router.post(
    "/{insult_id}/examples",
    response_model=Insult,
    summary="Añadir ejemplo a un insulto",
    description="Añade un ejemplo de uso a un insulto. Requiere autenticación.",
)
def add_example_to_insult(
    insult_id: int,
    data: InsultExampleBase,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(ensure_user_in_db),
):
    insult = (
        db.query(models.Insult)
        .options(
            joinedload(models.Insult.examples),
            joinedload(models.Insult.tag),
            selectinload(models.Insult.stars),
            selectinload(models.Insult.comments),
        )
        .filter(models.Insult.id == insult_id)
        .first()
    )
    if not insult:
        raise HTTPException(status_code=404, detail=f"Insulto con ID {insult_id} no encontrado")
    ex = models.InsultExample(text=data.text, insult_id=insult_id, is_active=data.is_active)
    db.add(ex)
    db.commit()
    db.refresh(insult)
    return _insult_with_counts(insult, current_user.sub)


@router.get(
    "/{insult_id}/examples",
    response_model=List[InsultExample],
    summary="Listar ejemplos de un insulto",
    description="Devuelve los ejemplos de uso de un insulto.",
)
def list_insult_examples(insult_id: int, db: Session = Depends(get_db)):
    insult = db.query(models.Insult).filter(models.Insult.id == insult_id).first()
    if not insult:
        raise HTTPException(status_code=404, detail=f"Insulto con ID {insult_id} no encontrado")
    examples = db.query(models.InsultExample).filter(models.InsultExample.insult_id == insult_id).all()
    return examples


@router.put(
    "/examples/{example_id}",
    response_model=InsultExample,
    summary="Editar ejemplo de un insulto",
    description="Actualiza un ejemplo por ID. Requiere autenticación.",
)
def update_insult_example(
    example_id: int,
    data: InsultExampleBase,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(ensure_user_in_db),
):
    ex = db.query(models.InsultExample).filter(models.InsultExample.id == example_id).first()
    if not ex:
        raise HTTPException(status_code=404, detail="Ejemplo no encontrado")
    ex.text = data.text
    ex.is_active = data.is_active
    db.commit()
    db.refresh(ex)
    return ex


@router.delete(
    "/examples/{example_id}",
    response_model=DeleteResponse,
    summary="Eliminar ejemplo de un insulto",
    description="Elimina un ejemplo por ID. Requiere autenticación.",
)
def delete_insult_example(
    example_id: int,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(ensure_user_in_db),
):
    ex = db.query(models.InsultExample).filter(models.InsultExample.id == example_id).first()
    if not ex:
        raise HTTPException(status_code=404, detail="Ejemplo no encontrado")
    db.delete(ex)
    db.commit()
    return DeleteResponse(success=True, message="Ejemplo eliminado")


# ----- Estrellita en insulto (una por usuario por insulto) -----
@router.post(
    "/{insult_id}/star",
    response_model=StarResponse,
    summary="Dar o quitar estrellita a un insulto",
    description="Toggle: una estrellita por usuario por insulto. Requiere autenticación.",
)
def toggle_insult_star(
    insult_id: int,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(ensure_user_in_db),
):
    insult = db.query(models.Insult).filter(models.Insult.id == insult_id).first()
    if not insult:
        raise HTTPException(status_code=404, detail=f"Insulto con ID {insult_id} no encontrado")
    existing = (
        db.query(models.InsultStar)
        .filter(
            models.InsultStar.insult_id == insult_id,
            models.InsultStar.user_id == current_user.sub,
        )
        .first()
    )
    if existing:
        db.delete(existing)
        starred = False
    else:
        db.add(models.InsultStar(insult_id=insult_id, user_id=current_user.sub))
        starred = True
    db.commit()
    count = (
        db.query(func.count(models.InsultStar.insult_id))
        .filter(models.InsultStar.insult_id == insult_id)
        .scalar()
        or 0
    )
    return StarResponse(starred=starred, star_count=count)


# ----- Comentarios -----
@router.get(
    "/{insult_id}/comments",
    response_model=List[InsultComment],
    summary="Listar comentarios de un insulto",
    description="Devuelve comentarios con respuestas, autor, conteo de estrellas y si el usuario actual dio estrellita.",
)
def get_insult_comments(
    insult_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[TokenPayload] = Depends(get_current_user),
):
    insult = db.query(models.Insult).filter(models.Insult.id == insult_id).first()
    if not insult:
        raise HTTPException(status_code=404, detail=f"Insulto con ID {insult_id} no encontrado")
    comments = (
        db.query(models.InsultComment)
        .options(
            joinedload(models.InsultComment.user),
            selectinload(models.InsultComment.stars),
            selectinload(models.InsultComment.likes),
            joinedload(models.InsultComment.replies).joinedload(models.InsultComment.user),
            joinedload(models.InsultComment.replies).selectinload(models.InsultComment.stars),
            joinedload(models.InsultComment.replies).selectinload(models.InsultComment.likes),
        )
        .filter(
            models.InsultComment.insult_id == insult_id,
            models.InsultComment.parent_id.is_(None),
        )
        .order_by(models.InsultComment.created_at.asc())
        .all()
    )
    user_id = current_user.sub if current_user else None
    out = []
    for c in comments:
        star_count = len(c.stars) if c.stars else 0
        starred_by_me = any(s.user_id == user_id for s in (c.stars or []))
        likes_count = len(c.likes) if c.likes else 0
        liked_by_me = any(l.user_id == user_id for l in (c.likes or []))
        replies_data = []
        for r in (c.replies or []):
            r_stars = len(r.stars) if r.stars else 0
            r_starred = any(s.user_id == user_id for s in (r.stars or []))
            r_likes = len(r.likes) if r.likes else 0
            r_liked = any(l.user_id == user_id for l in (r.likes or []))
            replies_data.append(
                InsultComment(
                    id=r.id,
                    insult_id=r.insult_id,
                    user_id=r.user_id,
                    comment=r.comment,
                    created_at=r.created_at,
                    parent_id=r.parent_id,
                    user=r.user,
                    star_count=r_stars,
                    starred_by_me=r_starred,
                    likes_count=r_likes,
                    liked_by_me=r_liked,
                    replies=[],
                )
            )
        out.append(
            InsultComment(
                id=c.id,
                insult_id=c.insult_id,
                user_id=c.user_id,
                comment=c.comment,
                created_at=c.created_at,
                parent_id=c.parent_id,
                user=c.user,
                star_count=star_count,
                starred_by_me=starred_by_me,
                likes_count=likes_count,
                liked_by_me=liked_by_me,
                replies=replies_data,
            )
        )
    return out


@router.post(
    "/{insult_id}/comments",
    response_model=InsultComment,
    summary="Comentar un insulto",
    description="Añade un comentario (o respuesta si envías parent_id). Requiere autenticación.",
)
def create_insult_comment(
    insult_id: int,
    data: InsultCommentCreate,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(ensure_user_in_db),
):
    insult = db.query(models.Insult).filter(models.Insult.id == insult_id).first()
    if not insult:
        raise HTTPException(status_code=404, detail=f"Insulto con ID {insult_id} no encontrado")
    if data.parent_id:
        parent = (
            db.query(models.InsultComment)
            .filter(
                models.InsultComment.id == data.parent_id,
                models.InsultComment.insult_id == insult_id,
            )
            .first()
        )
        if not parent:
            raise HTTPException(status_code=404, detail="Comentario padre no encontrado")
    comment = models.InsultComment(
        insult_id=insult_id,
        user_id=current_user.sub,
        comment=data.comment,
        parent_id=data.parent_id,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    db.refresh(comment.user)
    return InsultComment(
        id=comment.id,
        insult_id=comment.insult_id,
        user_id=comment.user_id,
        comment=comment.comment,
        created_at=comment.created_at,
        parent_id=comment.parent_id,
        user=comment.user,
        star_count=0,
        starred_by_me=False,
        likes_count=0,
        liked_by_me=False,
        replies=[],
    )


# ----- Like en comentario (un like por usuario por comentario) -----
@router.post(
    "/comments/{comment_id}/like",
    response_model=LikeResponse,
    summary="Dar o quitar like a un comentario de insulto",
    description="Toggle: un like por usuario por comentario. Requiere autenticación.",
)
def toggle_comment_like(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(ensure_user_in_db),
):
    comment = db.query(models.InsultComment).filter(models.InsultComment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")
    existing = (
        db.query(models.CommentLike)
        .filter(
            models.CommentLike.comment_id == comment_id,
            models.CommentLike.user_id == current_user.sub,
        )
        .first()
    )
    if existing:
        db.delete(existing)
        liked = False
    else:
        db.add(models.CommentLike(comment_id=comment_id, user_id=current_user.sub))
        liked = True
    db.commit()
    count = (
        db.query(func.count(models.CommentLike.comment_id))
        .filter(models.CommentLike.comment_id == comment_id)
        .scalar()
        or 0
    )
    return LikeResponse(liked=liked, likes_count=count)


# ----- Estrellita en comentario (una por usuario por comentario) -----
@router.post(
    "/comments/{comment_id}/star",
    response_model=StarResponse,
    summary="Dar o quitar estrellita a un comentario",
    description="Toggle: una estrellita por usuario por comentario. Requiere autenticación.",
)
def toggle_comment_star(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(ensure_user_in_db),
):
    comment = db.query(models.InsultComment).filter(models.InsultComment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")
    existing = (
        db.query(models.CommentStar)
        .filter(
            models.CommentStar.comment_id == comment_id,
            models.CommentStar.user_id == current_user.sub,
        )
        .first()
    )
    if existing:
        db.delete(existing)
        starred = False
    else:
        db.add(models.CommentStar(comment_id=comment_id, user_id=current_user.sub))
        starred = True
    db.commit()
    count = (
        db.query(func.count(models.CommentStar.comment_id))
        .filter(models.CommentStar.comment_id == comment_id)
        .scalar()
        or 0
    )
    return StarResponse(starred=starred, star_count=count)


@router.put(
    "/comments/{comment_id}",
    response_model=InsultComment,
    summary="Editar comentario",
    description="Actualiza tu comentario. Solo el autor puede editarlo. Requiere autenticación.",
)
def update_insult_comment(
    comment_id: int,
    data: InsultCommentUpdate,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(ensure_user_in_db),
):
    comment = (
        db.query(models.InsultComment)
        .options(
            joinedload(models.InsultComment.user),
            selectinload(models.InsultComment.stars),
            selectinload(models.InsultComment.likes),
        )
        .filter(models.InsultComment.id == comment_id)
        .first()
    )
    if not comment:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")
    if comment.user_id != current_user.sub:
        raise HTTPException(status_code=403, detail="Solo el autor puede editar este comentario")
    comment.comment = data.comment
    db.commit()
    db.refresh(comment)
    star_count = len(comment.stars) if comment.stars else 0
    starred_by_me = any(s.user_id == current_user.sub for s in (comment.stars or []))
    likes_count = len(comment.likes) if comment.likes else 0
    liked_by_me = any(l.user_id == current_user.sub for l in (comment.likes or []))
    return InsultComment(
        id=comment.id,
        insult_id=comment.insult_id,
        user_id=comment.user_id,
        comment=comment.comment,
        created_at=comment.created_at,
        parent_id=comment.parent_id,
        user=comment.user,
        star_count=star_count,
        starred_by_me=starred_by_me,
        likes_count=likes_count,
        liked_by_me=liked_by_me,
        replies=[],
    )


@router.delete(
    "/comments/{comment_id}",
    response_model=DeleteResponse,
    summary="Eliminar comentario",
    description="Elimina tu comentario. Solo el autor puede eliminarlo. Requiere autenticación.",
)
def delete_insult_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(ensure_user_in_db),
):
    comment = db.query(models.InsultComment).filter(models.InsultComment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")
    if comment.user_id != current_user.sub:
        raise HTTPException(status_code=403, detail="Solo el autor puede eliminar este comentario")
    db.delete(comment)
    db.commit()
    return DeleteResponse(success=True, message="Comentario eliminado")
