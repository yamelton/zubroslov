from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from ..config import settings

bearer_transport = BearerTransport(tokenUrl="api/auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.SECRET_KEY, 
        lifetime_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
