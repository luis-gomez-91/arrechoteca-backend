from pydantic import BaseModel
from typing import List


class TestGuayacoAnswerBase(BaseModel):
    text: str
    order: int  # 1, 2, 3, 4
    is_correct: bool = False


class TestGuayacoAnswerCreate(TestGuayacoAnswerBase):
    pass


class TestGuayacoAnswerUpdate(BaseModel):
    text: str | None = None
    order: int | None = None
    is_correct: bool | None = None


class TestGuayacoAnswer(TestGuayacoAnswerBase):
    id: int
    test_guayaco_id: int

    class Config:
        from_attributes = True


# ----- Question -----
class TestGuayacoBase(BaseModel):
    question: str
    is_active: bool = True


class TestGuayacoCreate(TestGuayacoBase):
    answers: List[TestGuayacoAnswerCreate]  # exactly 4, one with is_correct=True


class TestGuayacoUpdate(BaseModel):
    question: str | None = None
    is_active: bool | None = None
    answers: List[TestGuayacoAnswerCreate] | None = None  # if provided, replaces all answers


class TestGuayaco(TestGuayacoBase):
    id: int
    answers: List[TestGuayacoAnswer] = []

    class Config:
        from_attributes = True


class TestGuayacoPaginated(BaseModel):
    items: List[TestGuayaco]
    total: int
    skip: int
    limit: int

    class Config:
        from_attributes = True


class TestGuayacoDeleteResponse(BaseModel):
    success: bool
    message: str
    deleted_id: int
