"""
Аутентификация и управление JWT токенами
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверить пароль (простое сравнение без хеширования)
    
    В production используйте passlib с bcrypt:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"])
    """
    return plain_password == hashed_password

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Создать JWT токен
    
    Args:
        data: Данные для включения в токен
        expires_delta: Время истечения токена (опционально)
    
    Returns:
        JWT токен
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Проверить JWT токен
    
    Args:
        token: JWT токен
    
    Returns:
        Payload токена или None если токен невалиден
    """
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        print("❌ Токен истёк")
        return None
    except jwt.InvalidTokenError:
        print("❌ Невалиден токен")
        return None
