from sqlalchemy import Column, Integer, String, ForeignKey, Text, Table, DateTime, func
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

# ==============================
# MANY-TO-MANY RELATIONSHIP
# ==============================
word_category = Table(
    "word_category",
    Base.metadata,
    Column("word_id", Integer, ForeignKey("words.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True)
)

# ==============================
# CATEGORY MODEL
# ==============================
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    words = relationship("Word", secondary=word_category, back_populates="categories")

# ==============================
# WORD MODEL
# ==============================
class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String(100), unique=True, nullable=False)
    meaning = Column(Text, nullable=False)

    categories = relationship("Category", secondary=word_category, back_populates="words")
    examples = relationship("WordExample", back_populates="word", cascade="all, delete-orphan")

class WordExample(Base):
    __tablename__ = "word_examples"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    word_id = Column(Integer, ForeignKey("words.id"))

    word = relationship("Word", back_populates="examples")

# ==============================
# INSULT MODEL
# ==============================
class Insult(Base):
    __tablename__ = "insults"

    id = Column(Integer, primary_key=True, index=True)
    insult = Column(String(100), unique=True, nullable=False)
    meaning = Column(Text, nullable=False)

    examples = relationship("InsultExample", back_populates="insult", cascade="all, delete-orphan")
    comments = relationship("InsultComment", back_populates="insult", cascade="all, delete-orphan")

class InsultExample(Base):
    __tablename__ = "insult_examples"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    insult_id = Column(Integer, ForeignKey("insults.id"))

    insult = relationship("Insult", back_populates="examples")

# ==============================
# USER MODEL (CORREGIDO)
# ==============================
class User(Base):
    __tablename__ = "users"

    id = Column(String(255), primary_key=True, index=True)  # UUID de Supabase
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# ==============================
# USER COMMENTS (FORUM STYLE)
# ==============================
class InsultComment(Base):
    __tablename__ = "insult_comments"

    id = Column(Integer, primary_key=True, index=True)
    insult_id = Column(Integer, ForeignKey("insults.id"), nullable=False)

    # Usuario (UUID de Supabase)
    user_id = Column(String(255), ForeignKey("users.id"), nullable=False)

    comment = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # ==============================
    # SELF-REFERENTIAL RELATIONSHIP
    # ==============================
    parent_id = Column(Integer, ForeignKey("insult_comments.id"), nullable=True)

    # Un comentario puede tener "respuestas"
    replies = relationship(
        "InsultComment",
        back_populates="parent",
        cascade="all, delete-orphan"
    )

    # El comentario padre
    parent = relationship(
        "InsultComment",
        remote_side=[id],
        back_populates="replies"
    )

    # Relación con el insulto principal
    insult = relationship("Insult", back_populates="comments")
    
    # Relación con el usuario
    user = relationship("User")