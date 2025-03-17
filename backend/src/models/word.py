from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class WordBase(SQLModel):
    english: str = Field(index=True)  # Английское слово
    russian: str  # Русский перевод
    audio_path: str | None = Field(default=None, nullable=True)  # Важное изменение


class Word(WordBase, table=True):
    id: int = Field(default=None, primary_key=True)

class WordCreate(WordBase):
    pass

class WordProgress(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    word_id: int = Field(foreign_key="word.id")
    user_id: int = Field(foreign_key="user.id")
    last_shown: datetime = Field(default_factory=datetime.utcnow)
    shown_count: int = 0
    correct_count: int = 0
    error_count: int = 0
