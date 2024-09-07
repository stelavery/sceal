import pytest
import asyncio
import os
import logging
from uuid import uuid4
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.models import Base, User, Article
from app.schemas import UserCreate, UserUpdate, ArticleCreate, ArticleUpdate
from app.crud import (
    create_user, get_user, get_user_by_email, update_user, delete_user,
    create_article, get_article, get_articles_by_author, update_article, delete_article
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Test database URL and engine
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

async def force_drop_tables():
    logger.info("Forcing table drop")
    async with engine.begin() as conn:
        # Close all database connections
        await conn.execute(text("""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = current_database()
            AND pid <> pg_backend_pid();
        """))
        # Now drop the tables
        await conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS articles CASCADE"))
    logger.info("Forced table drop completed")

@pytest.fixture(scope="session", autouse=True)
async def cleanup_database():
    yield
    await force_drop_tables()

# Setup and teardown for tests
@pytest.fixture(scope="function")
async def db_session():
    logger.info("Setting up database")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            logger.info("Tearing down database")
            await session.close()
            await asyncio.sleep(1)  # Give a moment for connections to close
            
            try:
                async with engine.begin() as conn:
                    await conn.run_sync(Base.metadata.drop_all)
                logger.info("Tables dropped successfully")
            except Exception as e:
                logger.error(f"Error dropping tables: {e}")
            
            await engine.dispose()
            logger.info("Engine disposed")

@pytest.mark.asyncio
async def test_create_user(db_session):
    logger.info("Starting test_create_user")
    try:
        async with asyncio.timeout(10):  # 10 seconds timeout
            user_create = UserCreate(email="test@example.com", password="securepassword")
            user = await create_user(db_session, user_create)
            assert user.email == "test@example.com"
            assert user.hashed_password  # assuming the password is hashed
        logger.info("test_create_user completed successfully")
    except asyncio.TimeoutError:
        logger.error("test_create_user timed out")
        raise
    except Exception as e:
        logger.error(f"Error in test_create_user: {e}")
        raise

@pytest.mark.asyncio
async def test_get_user(db_session):
    logger.info("Starting test_get_user")
    try:
        async with asyncio.timeout(10):  # 10 seconds timeout
            user_create = UserCreate(email="test@example.com", password="securepassword")
            user = await create_user(db_session, user_create)
            fetched_user = await get_user(db_session, user.id)
            assert fetched_user is not None
            assert fetched_user.email == "test@example.com"
        logger.info("test_get_user completed successfully")
    except asyncio.TimeoutError:
        logger.error("test_get_user timed out")
        raise
    except Exception as e:
        logger.error(f"Error in test_get_user: {e}")
        raise

@pytest.mark.asyncio
async def test_update_user(db_session):
    logger.info("Starting test_update_user")
    try:
        async with asyncio.timeout(10):  # 10 seconds timeout
            user_create = UserCreate(email="test@example.com", password="securepassword")
            user = await create_user(db_session, user_create)
            
            # Update the UserUpdate instantiation to include all required fields
            user_update = UserUpdate(
                email="newemail@example.com",
                password="newpassword",  # Include password if it's required
                is_active=True,  # Or False, depending on your needs
                is_superuser=False  # Or True, depending on your needs
            )
            
            updated_user = await update_user(db_session, user.id, user_update)
            assert updated_user.email == "newemail@example.com"
            # Add more assertions if needed, e.g.:
            assert updated_user.is_active == True
            assert updated_user.is_superuser == False
        logger.info("test_update_user completed successfully")
    except asyncio.TimeoutError:
        logger.error("test_update_user timed out")
        raise
    except Exception as e:
        logger.error(f"Error in test_update_user: {e}")
        raise

@pytest.mark.asyncio
async def test_delete_user(db_session):
    logger.info("Starting test_delete_user")
    try:
        async with asyncio.timeout(10):  # 10 seconds timeout
            user_create = UserCreate(email="test@example.com", password="securepassword")
            user = await create_user(db_session, user_create)
            deleted_user = await delete_user(db_session, user.id)
            assert deleted_user is not None
            fetched_user = await get_user(db_session, user.id)
            assert fetched_user is None
        logger.info("test_delete_user completed successfully")
    except asyncio.TimeoutError:
        logger.error("test_delete_user timed out")
        raise
    except Exception as e:
        logger.error(f"Error in test_delete_user: {e}")
        raise