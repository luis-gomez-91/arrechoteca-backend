from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from database import get_db
from auth.dependencies import ensure_user_in_db
from schemas.user import TokenPayload
from schemas.test_guayaco import (
    TestGuayaco,
    TestGuayacoCreate,
    TestGuayacoUpdate,
    TestGuayacoPaginated,
    TestGuayacoDeleteResponse,
    TestGuayacoAnswer,
    TestGuayacoAnswerCreate,
)
import models

router = APIRouter(
    prefix="/test-guayaco",
    tags=["Test Guayaco"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/",
    response_model=TestGuayacoPaginated,
    summary="Listar preguntas (paginado)",
    description="Devuelve preguntas del test Guayaco paginadas, con sus respuestas.",
)
def list_questions(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    if limit < 1 or limit > 100:
        limit = 20
    if skip < 0:
        skip = 0
    total = db.query(func.count(models.TestGuayaco.id)).scalar() or 0
    questions = (
        db.query(models.TestGuayaco)
        .options(joinedload(models.TestGuayaco.answers))
        .order_by(models.TestGuayaco.id.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return TestGuayacoPaginated(items=questions, total=total, skip=skip, limit=limit)


@router.get(
    "/{question_id}",
    response_model=TestGuayaco,
    summary="Obtener una pregunta",
    description="Devuelve una pregunta por ID con sus 4 respuestas.",
)
def get_question(
    question_id: int,
    db: Session = Depends(get_db),
):
    question = (
        db.query(models.TestGuayaco)
        .options(joinedload(models.TestGuayaco.answers))
        .filter(models.TestGuayaco.id == question_id)
        .first()
    )
    if not question:
        raise HTTPException(status_code=404, detail=f"Pregunta con ID {question_id} no encontrada")
    return question


@router.post(
    "/",
    response_model=TestGuayaco,
    summary="Crear pregunta",
    description="Crea una nueva pregunta con exactamente 4 respuestas (una correcta). Requiere autenticación.",
)
def create_question(
    data: TestGuayacoCreate,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(ensure_user_in_db),
):
    if len(data.answers) != 4:
        raise HTTPException(
            status_code=400,
            detail="Debe haber exactamente 4 respuestas por pregunta",
        )
    correct_count = sum(1 for a in data.answers if a.is_correct)
    if correct_count != 1:
        raise HTTPException(
            status_code=400,
            detail="Debe haber exactamente una respuesta correcta",
        )
    orders = [a.order for a in data.answers]
    if set(orders) != {1, 2, 3, 4}:
        raise HTTPException(
            status_code=400,
            detail="Las respuestas deben tener order 1, 2, 3 y 4",
        )

    question = models.TestGuayaco(
        question=data.question,
        is_active=data.is_active,
    )
    db.add(question)
    db.flush()

    for a in data.answers:
        answer = models.TestGuayacoAnswer(
            test_guayaco_id=question.id,
            text=a.text,
            order=a.order,
            is_correct=a.is_correct,
        )
        db.add(answer)

    db.commit()
    question = (
        db.query(models.TestGuayaco)
        .options(joinedload(models.TestGuayaco.answers))
        .filter(models.TestGuayaco.id == question.id)
        .first()
    )
    return question


@router.put(
    "/{question_id}",
    response_model=TestGuayaco,
    summary="Actualizar pregunta",
    description="Actualiza una pregunta y/o sus respuestas. Si envías `answers`, se reemplazan todas. Requiere autenticación.",
)
def update_question(
    question_id: int,
    data: TestGuayacoUpdate,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(ensure_user_in_db),
):
    question = (
        db.query(models.TestGuayaco)
        .options(joinedload(models.TestGuayaco.answers))
        .filter(models.TestGuayaco.id == question_id)
        .first()
    )
    if not question:
        raise HTTPException(status_code=404, detail=f"Pregunta con ID {question_id} no encontrada")

    if data.question is not None:
        question.question = data.question
    if data.is_active is not None:
        question.is_active = data.is_active

    if data.answers is not None:
        if len(data.answers) != 4:
            raise HTTPException(
                status_code=400,
                detail="Debe haber exactamente 4 respuestas",
            )
        correct_count = sum(1 for a in data.answers if a.is_correct)
        if correct_count != 1:
            raise HTTPException(
                status_code=400,
                detail="Debe haber exactamente una respuesta correcta",
            )
        orders = [a.order for a in data.answers]
        if set(orders) != {1, 2, 3, 4}:
            raise HTTPException(
                status_code=400,
                detail="Las respuestas deben tener order 1, 2, 3 y 4",
            )
        # Delete existing and create new
        for a in question.answers:
            db.delete(a)
        db.flush()
        for a in data.answers:
            answer = models.TestGuayacoAnswer(
                test_guayaco_id=question.id,
                text=a.text,
                order=a.order,
                is_correct=a.is_correct,
            )
            db.add(answer)

    db.commit()
    db.refresh(question)
    question = (
        db.query(models.TestGuayaco)
        .options(joinedload(models.TestGuayaco.answers))
        .filter(models.TestGuayaco.id == question_id)
        .first()
    )
    return question


@router.delete(
    "/{question_id}",
    response_model=TestGuayacoDeleteResponse,
    summary="Eliminar pregunta",
    description="Elimina una pregunta y todas sus respuestas. Requiere autenticación.",
)
def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: TokenPayload = Depends(ensure_user_in_db),
):
    question = db.query(models.TestGuayaco).filter(models.TestGuayaco.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail=f"Pregunta con ID {question_id} no encontrada")
    try:
        db.delete(question)
        db.commit()
        return TestGuayacoDeleteResponse(
            success=True,
            message=f"Pregunta {question_id} eliminada correctamente",
            deleted_id=question_id,
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ----- Respuestas (opcional: endpoints por respuesta) -----
@router.get(
    "/{question_id}/answers",
    response_model=list[TestGuayacoAnswer],
    summary="Listar respuestas de una pregunta",
    description="Devuelve las 4 respuestas de una pregunta (ordenadas por order).",
)
def list_answers(
    question_id: int,
    db: Session = Depends(get_db),
):
    question = db.query(models.TestGuayaco).filter(models.TestGuayaco.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail=f"Pregunta con ID {question_id} no encontrada")
    answers = (
        db.query(models.TestGuayacoAnswer)
        .filter(models.TestGuayacoAnswer.test_guayaco_id == question_id)
        .order_by(models.TestGuayacoAnswer.order)
        .all()
    )
    return answers
