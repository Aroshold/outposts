"""
Pydantic схемы для валидации данных
"""

from pydantic import BaseModel, Field
from typing import Literal

class LoginRequest(BaseModel):
    """Запрос на вход"""
    password: str = Field(..., description="Пароль администратора")
    
    class Config:
        json_schema_extra = {
            "example": {
                "password": "admin123"
            }
        }

class TokenResponse(BaseModel):
    """Ответ с токеном"""
    access_token: str
    token_type: str = "bearer"
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }

class OutpostUpdate(BaseModel):
    """Обновление владельца аванпоста"""
    team: Literal["classic", "cyberpunk"] = Field(
        ..., 
        description="Новая команда-владелец"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "team": "cyberpunk"
            }
        }

class OutpostResponse(BaseModel):
    """Ответ с данными аванпоста"""
    id: int
    name: str
    team: Literal["classic", "cyberpunk"]
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Alpha Station",
                "team": "classic"
            }
        }
