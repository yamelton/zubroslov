from __future__ import annotations
from sqlmodel import SQLModel, Field
from typing import Optional, List
import uuid

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    is_superuser: bool = Field(default=False)

class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str

class ProgressBase(SQLModel):
    user_id: uuid.UUID = Field(foreign_key="user.id")
    completed: bool = Field(default=False)
    score: int = Field(default=0)

class Progress(ProgressBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class UserResponse(UserBase):
    id: uuid.UUID

class ProgressResponse(ProgressBase):
    id: int
