from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ----- Tags -----
class InsultTagBase(BaseModel):
    name: str


class InsultTagCreate(InsultTagBase):
    pass


class InsultTag(InsultTagBase):
    id: int

    class Config:
        from_attributes = True


# ----- Examples -----
class InsultExampleBase(BaseModel):
    text: str
    is_active: bool = False


class InsultExample(InsultExampleBase):
    id: int
    insult_id: int | None = None
    is_active: bool = False

    class Config:
        from_attributes = True


# ----- Insult -----
class InsultBase(BaseModel):
    insult: str
    meaning: str
    is_active: bool = False
    tag_id: Optional[int] = None


class InsultCreate(InsultBase):
    pass


class Insult(InsultBase):
    id: int
    tag_id: Optional[int] = None
    tag: Optional[InsultTag] = None
    examples: list[InsultExample] = []
    is_active: bool = False
    comments_count: int = 0
    star_count: int = 0
    starred_by_me: bool = False

    class Config:
        from_attributes = True


class InsultDeleteResponse(BaseModel):
    success: bool
    message: str
    deleted_id: int


# ----- Comentarios -----
class InsultCommentBase(BaseModel):
    comment: str
    parent_id: Optional[int] = None


class InsultCommentCreate(InsultCommentBase):
    pass


class InsultCommentUpdate(BaseModel):
    comment: str


class UserCommentAuthor(BaseModel):
    id: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True


class InsultComment(InsultCommentBase):
    id: int
    insult_id: int
    user_id: str
    created_at: datetime
    parent_id: Optional[int] = None
    user: Optional[UserCommentAuthor] = None
    star_count: int = 0
    starred_by_me: bool = False
    likes_count: int = 0
    liked_by_me: bool = False
    replies: list["InsultComment"] = []

    class Config:
        from_attributes = True


# Para respuesta de like/estrellita
class LikeResponse(BaseModel):
    liked: bool
    likes_count: int


class StarResponse(BaseModel):
    starred: bool
    star_count: int


class DeleteResponse(BaseModel):
    success: bool
    message: str


InsultComment.model_rebuild()
