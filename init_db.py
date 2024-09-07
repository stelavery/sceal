import os
import asyncio
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.models import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Create the asynchronous engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create a sessionmaker factory for async sessions
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    # Create tables asynchronously
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Database tables created successfully.")

    # Dispose of the engine after tables are created
    await engine.dispose()

# Main entry point for running the init_db function
if __name__ == "__main__":
    asyncio.run(init_db())