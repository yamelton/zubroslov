from __future__ import annotations
from sqlmodel import SQLModel, Field
from typing import Optional

class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)
    hashed_password: str

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class ProgressBase(SQLModel):
    user_id: int = Field(foreign_key="user.id")
    completed: bool = Field(default=False)
    score: int = Field(default=0)

class Progress(ProgressBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class UserResponse(UserBase):
    id: int

class ProgressResponse(ProgressBase):
    id: int
