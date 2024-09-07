from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from typing import List, Optional

# Schema for reading user information (without articles to avoid circular references)
class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    is_active: bool
    is_superuser: bool
    is_verified: bool

    model_config = ConfigDict(from_attributes=True)  # Replaces orm_mode = True

# Schema for creating a user
class UserCreate(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(from_attributes=True)

# Schema for updating a user
class UserUpdate(BaseModel):
    email: Optional[EmailStr]
    password: Optional[str]
    is_active: Optional[bool]
    is_superuser: Optional[bool]

    model_config = ConfigDict(from_attributes=True)

# Schema for reading article information
class ArticleRead(BaseModel):
    id: UUID
    title: str
    content: str
    audio_file_url: Optional[str]
    author_id: UUID

    model_config = ConfigDict(from_attributes=True)

# Schema for creating an article
class ArticleCreate(BaseModel):
    title: str
    content: str
    audio_file_url: Optional[str]

    model_config = ConfigDict(from_attributes=True)

# Schema for updating an article
class ArticleUpdate(BaseModel):
    title: Optional[str]
    content: Optional[str]
    audio_file_url: Optional[str]

    model_config = ConfigDict(from_attributes=True)

# Schema for reading user information with their articles
class UserReadWithArticles(UserRead):
    articles: List[ArticleRead] = []

    model_config = ConfigDict(from_attributes=True)