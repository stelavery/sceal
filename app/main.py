from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal, init_db
from app import schemas, crud, auth
from app.auth import fastapi_users, jwt_backend

# Define the lifespan function
async def lifespan(app: FastAPI):
    await init_db()
    yield

# Create an instance of FastAPI with the lifespan function
app = FastAPI(lifespan=lifespan)

# Dependency to get the async session
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

@app.get("/")
async def read_root():
    return {"message": "Sceal API is running"}

@app.post("/users/", response_model=schemas.UserRead)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await crud.create_user(db, user)
    return db_user

@app.post("/articles/", response_model=schemas.ArticleRead)
async def create_article(
    article: schemas.ArticleCreate,
    db: AsyncSession = Depends(get_db),
    user: schemas.UserRead = Depends(fastapi_users.current_user())  # Ensure user is authenticated
):
    db_article = await crud.create_article(db, article, user.id)  # Use authenticated user's ID
    return db_article

# Add FastAPI Users' router with the JWT backend
app.include_router(
    fastapi_users.get_auth_router(jwt_backend),
    prefix="/auth/jwt",
    tags=["auth"]
)

app.include_router(
    fastapi_users.get_register_router(schemas.UserCreate, user_create_schema=schemas.UserCreate),
    prefix="/auth",
    tags=["auth"]
)

app.include_router(
    fastapi_users.get_users_router(
        user_schema=schemas.UserRead,
        user_update_schema=schemas.UserUpdate
    ),
    prefix="/users",
    tags=["users"]
)