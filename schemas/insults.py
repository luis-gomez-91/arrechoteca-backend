from pydantic import BaseModel

class InsultExampleBase(BaseModel):
    text: str

class InsultBase(BaseModel):
    insult: str
    meaning: str

class Insult(InsultBase):
    id: int
    examples: list[InsultExampleBase] = []

    class Config:
        from_attributes = True