from sqlmodel import create_engine, SQLModel, Session, select
from .config import settings
# from .models.user import User
# from .models.progress import Progress
from .models.models import User, Progress
from passlib.context import CryptContext

engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

def get_session():
    with Session(engine) as session:
        yield session


def create_test_user(session: Session):
    test_user = session.exec(
        select(User).where(User.username == "testuser")
    ).first()

    if not test_user:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        new_user = User(
            username="testuser",
            hashed_password=pwd_context.hash("testpass")
        )
        session.add(new_user)
        session.commit()
        print("Test user created")
    else:
        print("Test user already exists")


def create_db_and_tables():
    from backend.src.models.word import Word
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        create_test_user(session)
