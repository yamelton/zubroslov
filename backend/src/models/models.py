from __future__ import annotations
from typing import Optional, List
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, Float, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from fastapi_users.db import SQLAlchemyBaseUserTableUUID

class Base(DeclarativeBase):
    pass

class User(SQLAlchemyBaseUserTableUUID, Base):
    username = Column(String, unique=True, index=True)
    
    # Relationships
    word_progress = relationship("WordProgress", back_populates="user")

# Progress models using SQLAlchemy
class Progress(Base):
    __tablename__ = "progress"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    score: Mapped[int] = mapped_column(Integer, default=0)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    words_learned: Mapped[int] = mapped_column(Integer, default=0)
    accuracy: Mapped[float] = mapped_column(Float, default=0.0)
    session_start: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="progress")

# Add relationship to User model
User.progress = relationship("Progress", back_populates="user")

# Response models
class ProgressResponse:
    id: int
    user_id: uuid.UUID
    completed: bool
    score: int
    duration_seconds: int
    words_learned: int
    accuracy: float
    session_start: datetime
