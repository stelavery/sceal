from typing import List, Optional
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from uuid import UUID
from app.models import User, Article
from app.schemas import UserCreate, UserUpdate, ArticleCreate, ArticleUpdate
from passlib.context import CryptContext

# User CRUD operations

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user(db: AsyncSession, user_create: UserCreate) -> User:
    hashed_password = pwd_context.hash(user_create.password)
    db_user = User(email=user_create.email, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_user(db: AsyncSession, user_id: UUID) -> Optional[User]:
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalar_one_or_none()

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalar_one_or_none()

async def update_user(db: AsyncSession, user_id: UUID, user_update: UserUpdate) -> Optional[User]:
    result = await db.execute(select(User).filter(User.id == user_id))
    db_user = result.scalar_one_or_none()
    if not db_user:
        return None
    
    for field, value in user_update.model_dump(exclude_unset=True).items():
        setattr(db_user, field, value)
    
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def delete_user(db: AsyncSession, user_id: UUID) -> Optional[User]:
    result = await db.execute(select(User).filter(User.id == user_id))
    db_user = result.scalar_one_or_none()
    if db_user:
        await db.delete(db_user)
        await db.commit()
    return db_user

# Article CRUD operations

async def create_article(db: AsyncSession, article_create: ArticleCreate, author_id: UUID) -> Article:
    db_article = Article(
        title=article_create.title,
        content=article_create.content,
        audio_file_url=article_create.audio_file_url,
        author_id=author_id
    )
    db.add(db_article)
    await db.commit()
    await db.refresh(db_article)
    return db_article

async def get_article(db: AsyncSession, article_id: UUID) -> Optional[Article]:
    result = await db.execute(select(Article).filter(Article.id == article_id))
    return result.scalar_one_or_none()

async def get_articles_by_author(db: AsyncSession, author_id: UUID) -> List[Article]:
    result = await db.execute(select(Article).filter(Article.author_id == author_id))
    return result.scalars().all()

async def update_article(db: AsyncSession, article_id: UUID, article_update: ArticleUpdate) -> Optional[Article]:
    result = await db.execute(select(Article).filter(Article.id == article_id))
    db_article = result.scalar_one_or_none()
    if not db_article:
        return None
    
    for field, value in article_update.model_dump(exclude_unset=True).items():
        setattr(db_article, field, value)
    
    await db.commit()
    await db.refresh(db_article)
    return db_article

async def delete_article(db: AsyncSession, article_id: UUID) -> Optional[Article]:
    result = await db.execute(select(Article).filter(Article.id == article_id))
    db_article = result.scalar_one_or_none()
    if db_article:
        await db.delete(db_article)
        await db.commit()
    return db_article