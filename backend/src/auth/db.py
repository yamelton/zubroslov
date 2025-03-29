from fastapi import Depends
from fastapi_users.db import SQLModelUserDatabase
from sqlmodel import Session
from ..database import get_session
from ..models.models import User

async def get_user_db(session: Session = Depends(get_session)):
    yield SQLModelUserDatabase(session, User)
