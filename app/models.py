from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
import uuid

class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = 'users'

    articles = relationship("Article", back_populates="author", cascade="all, delete-orphan")

class Article(Base):
    __tablename__ = 'articles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(100), nullable=False)  # Ensure this field is not nullable
    content = Column(Text, nullable=False)  # Ensure this field is not nullable
    audio_file_url = Column(String(255), nullable=True)  # Make this field optional if needed
    author_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)  # Ensure this field is not nullable

    # Define a relationship with User
    author = relationship("User", back_populates="articles")