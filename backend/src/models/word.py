from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from datetime import datetime
import uuid
import json

from ..models.models import Base, wordset_word

class Word(Base):
    __tablename__ = "word"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    english: Mapped[str] = mapped_column(String, index=True)  # Английское слово
    russian: Mapped[str] = mapped_column(String)  # Русский перевод
    audio_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # Аудио файл
    
    # Relationships
    progress = relationship("WordProgress", back_populates="word")
    user_events = relationship("UserWordEvent", back_populates="word")
    sets = relationship("WordSet", secondary=wordset_word, back_populates="words")

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

class UserWordEvent(Base):
    """
    Модель для хранения сырых событий взаимодействия пользователя со словами.
    Сохраняет каждое событие показа слова и каждый ответ пользователя.
    """
    __tablename__ = "user_word_events"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))
    word_id: Mapped[int] = mapped_column(ForeignKey("word.id"))
    event_type: Mapped[str] = mapped_column(String)  # "shown" или "answered"
    is_correct: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)  # Null для event_type="shown"
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Дополнительные данные в JSON формате (опционально)
    event_data: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # JSON строка с дополнительными данными
    
    # Relationships
    user = relationship("User", back_populates="word_events")
    word = relationship("Word", back_populates="user_events")
