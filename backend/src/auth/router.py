import uuid
from fastapi import Depends
from fastapi_users import FastAPIUsers
from .auth import auth_backend
from .manager import get_user_manager
from ..models.models import User
from ..schemas import UserRead, UserCreate, UserUpdate

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

# Export current_user dependency for protected routes
current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
