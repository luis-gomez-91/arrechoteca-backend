from pydantic import BaseModel

class InsultExampleBase(BaseModel):
    text: str
    is_active: bool = False

class InsultExample(InsultExampleBase):
    id: int
    insult_id: int | None = None
    is_active: bool = False

    class Config:
        from_attributes = True

class InsultBase(BaseModel):
    insult: str
    meaning: str
    is_active: bool = False

class Insult(InsultBase):
    id: int
    examples: list[InsultExample] = []
    is_active: bool = False

    class Config:
        from_attributes = True