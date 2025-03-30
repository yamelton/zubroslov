from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from datetime import datetime
import uuid

from ..models.models import Base

class Word(Base):
    __tablename__ = "word"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    english: Mapped[str] = mapped_column(String, index=True)  # Английское слово
    russian: Mapped[str] = mapped_column(String)  # Русский перевод
    audio_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Аудио файл
    
    # Relationship with WordProgress
    progress = relationship("WordProgress", back_populates="word")

class WordProgress(Base):
    __tablename__ = "wordprogress"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    word_id: Mapped[int] = mapped_column(ForeignKey("word.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))
    last_shown: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    shown_count: Mapped[int] = mapped_column(Integer, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    word = relationship("Word", back_populates="progress")
    user = relationship("User", back_populates="word_progress")
