"""
Конфигурация приложения
"""

import os
from dotenv import load_dotenv

# Загрузить переменные окружения из .env файла
load_dotenv()

# JWT конфигурация
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Администратор
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# База данных (если нужна в будущем)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///outposts.db")

# Переменные приложения
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

if __name__ == "__main__":
    print("Текущая конфигурация:")
    print(f"🔐 SECRET_KEY: {'***' if len(SECRET_KEY) > 10 else SECRET_KEY}")
    print(f"🎯 ALGORITHM: {ALGORITHM}")
    print(f"⏱️ TOKEN_EXPIRE: {ACCESS_TOKEN_EXPIRE_MINUTES} минут")
    print(f"🔑 ADMIN_PASSWORD: {'***' if len(ADMIN_PASSWORD) > 3 else ADMIN_PASSWORD}")
    print(f"🌍 ENVIRONMENT: {ENVIRONMENT}")
    print(f"🐛 DEBUG: {DEBUG}")
