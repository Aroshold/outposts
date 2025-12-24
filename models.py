"""
Модели данных с поддержкой главных аванпостов
"""

from pydantic import BaseModel
from typing import Literal

class Outpost(BaseModel):
    """Модель аванпоста"""
    id: int
    name: str
    team: Literal["classic", "cyberpunk"]
    is_primary: bool = False  # Новое поле для главного аванпоста
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Alpha Station",
                "team": "classic",
                "is_primary": False
            }
        }
