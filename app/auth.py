import os
import uuid
from fastapi import Depends
from fastapi_users import FastAPIUsers, schemas
from fastapi_users.authentication import JWTStrategy, AuthenticationBackend, BearerTransport
from fastapi_users.manager import BaseUserManager
from fastapi_users.exceptions import UserAlreadyExists
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User
from app.database import get_async_session
from dotenv import load_dotenv

load_dotenv()

SECRET = os.getenv("SECRET_KEY", "default_secret")

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)

class UserManager(BaseUserManager[User, uuid.UUID]):
    user_db_model = User

    async def on_after_register(self, user: User, request=None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(self, user: User, token: str, request=None):
        print(f"User {user.id} has forgotten their password. Reset token: {token}")

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

jwt_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy
)

fastapi_users = FastAPIUsers(
    get_user_manager,
    [jwt_backend],
)

current_user = fastapi_users.current_user()