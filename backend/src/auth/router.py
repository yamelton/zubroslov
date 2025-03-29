import uuid
from fastapi import Depends, FastAPI
from fastapi_users import FastAPIUsers
from .auth import auth_backend
from .manager import get_user_manager
from ..models.models import User

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

# Create auth router with all FastAPI Users routes
auth_router = fastapi_users.get_auth_router(auth_backend)
register_router = fastapi_users.get_register_router()
reset_password_router = fastapi_users.get_reset_password_router()
verify_router = fastapi_users.get_verify_router()
users_router = fastapi_users.get_users_router()

# Export current_user dependency for protected routes
current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
