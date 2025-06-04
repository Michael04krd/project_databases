from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator
from enum import Enum as PyEnum

from ..models.user import UserRole

class UserBase(BaseModel):
    surname: str = Field(..., max_length=200)
    name: str = Field(..., max_length=200)
    namedad: Optional[str] = Field(None, max_length=200)
    email:EmailStr
    role: UserRole = Field(
        default=UserRole.DONOR,
        description="Роль пользователя: donor, medical или admin"
    )


    model_config = ConfigDict(extra='forbid')

class UserCreate(UserBase):
    password:str = Field(..., min_length=8)
    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Пароль должен содержать минимум 8 символов")
        if not any(c.isupper() for c in v):
            raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")
        return v


class UserUpdate(BaseModel):
    surname: Optional[str] = Field(None, max_length=200, example="Иванов")
    name: Optional[str] = Field(None, max_length=200, example="Иван")
    namedad: Optional[str] = Field(None, max_length=200, example="Иванович")
    is_active: Optional[bool] = Field(None, example=True)

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)