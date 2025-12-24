from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json
import asyncio
from typing import List, Dict
from datetime import datetime
from pathlib import Path

from models import Outpost
from schemas import OutpostUpdate, LoginRequest, TokenResponse
from auth import verify_password, create_access_token, verify_token
from config import ADMIN_PASSWORD, SECRET_KEY

outposts_db: Dict[int, Outpost] = {
    1: Outpost(id=1, name='Лингвистический аванпост', team='cyberpunk'),
    2: Outpost(id=2, name='Математический аванпост', team='classic'),
    3: Outpost(id=3, name='Информационный аванпост', team='cyberpunk'),
    4: Outpost(id=4, name='Физический аванпост', team='classic'),
    5: Outpost(id=5, name='Аванпост русского языка', team='cyberpunk'),
    6: Outpost(id=6, name='Творческий аванпост', team='classic'),
    7: Outpost(id=7, name='-{Клуб ярчайшей Н.}-', team='cyberpunk', is_primary=True),
    8: Outpost(id=8, name='-{Поместье господина М.}-', team='classic', is_primary=True),
}


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Ошибка отправки: {e}")
                disconnected.append(connection)

        # Удалить неработающие соединения
        for conn in disconnected:
            self.disconnect(conn)


manager = ConnectionManager()

# Инициализация приложения


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    print("🚀 Сервер запущен")
    yield
    print("🛑 Сервер остановлен")

app = FastAPI(
    title="Outpost Control System API",
    description="API для управления аванпостами с WebSocket синхронизацией",
    version="1.0.0",
    lifespan=lifespan
)

# CORS конфигурация
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все источники
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)

# Монтировать папку со статичными файлами
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", tags=["Static"])
async def root():
    """Главная страница (дисплей)"""
    display_path = STATIC_DIR / "index.html"
    if display_path.exists():
        return FileResponse(display_path)
    return {
        "message": "Outpost Control System API",
        "version": "1.0.0",
        "docs": "/docs",
        "display": "/",
        "admin": "/admin",
        "health": "/health"
    }


@app.get("/admin", tags=["Static"])
async def admin_page():
    """Страница администратора"""
    admin_path = STATIC_DIR / "admin.html"
    if admin_path.exists():
        return FileResponse(admin_path)
    raise HTTPException(
        status_code=404,
        detail="Admin page not found. Place admin.html in static/ folder"
    )
# ============================================================================
# АУТЕНТИФИКАЦИЯ
# ============================================================================


@app.post("/auth/login", response_model=TokenResponse, tags=["Authentication"])
async def login(request: LoginRequest):
    """
    Вход администратора

    **Пароль по умолчанию: admin123**
    """
    if not verify_password(request.password, ADMIN_PASSWORD):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": "admin"})
    return TokenResponse(access_token=access_token, token_type="bearer")

# Зависимость для проверки токена


async def get_current_user(token: str = None) -> str:
    """Проверить JWT токен"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Отсутствует токен",
        )

    # Удалить "Bearer " префикс если есть
    if token.startswith("Bearer "):
        token = token[7:]

    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен",
        )
    return payload.get("sub")

# ============================================================================
# API ENDPOINTS
# ============================================================================


@app.get("/", tags=["General"])
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Outpost Control System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", tags=["General"])
async def health_check():
    """Проверка здоровья сервера"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "outposts_count": len(outposts_db),
        "active_connections": len(manager.active_connections)
    }

# ============================================================================
# АВАНПОСТЫ
# ============================================================================


@app.get("/api/outposts", response_model=List[dict], tags=["Outposts"])
async def get_outposts():
    """Получить все аванпосты"""
    return [
        {
            "id": outpost.id,
            "name": outpost.name,
            "team": outpost.team,
            "is_primary": outpost.is_primary
        }
        for outpost in outposts_db.values()
    ]


@app.get("/api/outposts/{outpost_id}", tags=["Outposts"])
async def get_outpost(outpost_id: int):
    """Получить конкретный аванпост"""
    if outpost_id not in outposts_db:
        raise HTTPException(status_code=404, detail="Аванпост не найден")

    outpost = outposts_db[outpost_id]
    return {
        "id": outpost.id,
        "name": outpost.name,
        "team": outpost.team,
        "is_primary": outpost.is_primary
    }


@app.put("/api/outposts/{outpost_id}", tags=["Outposts"])
async def update_outpost(
    outpost_id: int,
    update: OutpostUpdate,
    authorization: str = Header(None)
):
    """
    Изменить владельца аванпоста

    **Требует JWT токена в заголовке Authorization**

    Пример: `Authorization: Bearer eyJ...`
    """
    # Проверка токена
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется токен",
        )

    await get_current_user(authorization)

    if outpost_id not in outposts_db:
        raise HTTPException(status_code=404, detail="Аванпост не найден")

    if update.team not in ["classic", "cyberpunk"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Команда должна быть 'classic' или 'cyberpunk'"
        )

    # Обновить владельца
    old_team = outposts_db[outpost_id].team
    outposts_db[outpost_id].team = update.team

    outpost = outposts_db[outpost_id]

    # Broadcast обновление всем клиентам
    await manager.broadcast({
        "type": "outpost_updated",
        "outpost": {
            "id": outpost.id,
            "name": outpost.name,
            "team": outpost.team
        },
        "timestamp": datetime.now().isoformat(),
        "changed_from": old_team
    })

    return {
        "id": outpost.id,
        "name": outpost.name,
        "team": outpost.team,
        "is_primary": outpost.is_primary,
        "message": f"Аванпост передан команде {update.team}"
    }


@app.post("/api/outposts/batch/update", tags=["Outposts"])
async def batch_update_outposts(
    updates: List[OutpostUpdate],
    authorization: str = None
):
    """
    Массовое обновление аванпостов

    **Требует JWT токена в заголовке Authorization**
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется токен",
        )

    await get_current_user(authorization)

    for outpost_id, update in enumerate(updates, start=1):
        if outpost_id not in outposts_db:
            continue

        outposts_db[outpost_id].team = update.team
        outpost = outposts_db[outpost_id]

        await manager.broadcast({
            "type": "outpost_updated",
            "outpost": {
                "id": outpost.id,
                "name": outpost.name,
                "team": outpost.team
            },
            "timestamp": datetime.now().isoformat()
        })

    return {"message": f"Обновлено {len(updates)} аванпостов"}

# ============================================================================
# WEBSOCKET
# ============================================================================


@app.websocket("/ws/display")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket эндпоинт для реал-тайм обновлений

    Клиент получает уведомления при изменении состояния аванпостов:
    ```json
    {
      "type": "outpost_updated",
      "outpost": {
        "id": 1,
        "name": "Alpha Station",
        "team": "cyberpunk"
      },
      "timestamp": "2024-12-05T20:35:00.123456"
    }
    ```
    """
    await manager.connect(websocket)

    try:
        # Отправить начальное состояние
        initial_state = {
            "type": "initial_state",
            "outposts": [
                {
                    "id": outpost.id,
                    "name": outpost.name,
                    "team": outpost.team
                }
                for outpost in outposts_db.values()
            ],
            "timestamp": datetime.now().isoformat()
        }
        await websocket.send_json(initial_state)

        # Слушать входящие сообщения (для keep-alive)
        while True:
            data = await websocket.receive_text()
            # Просто пинг для поддержания соединения
            if data == "ping":
                await websocket.send_text("pong")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"Активных соединений: {len(manager.active_connections)}")
    except Exception as e:
        print(f"❌ Ошибка WebSocket: {e}")
        manager.disconnect(websocket)

# ============================================================================
# СТАТИСТИКА
# ============================================================================


@app.get("/api/stats", tags=["Statistics"])
async def get_stats():
    """Получить статистику"""
    classic_count = sum(1 for o in outposts_db.values() if o.team == "classic")
    cyberpunk_count = sum(1 for o in outposts_db.values()
                          if o.team == "cyberpunk")
    classic_primary = next((o for o in outposts_db.values()
                            if o.team == "classic" and o.is_primary), None)
    cyberpunk_primary = next((o for o in outposts_db.values()
                              if o.team == "cyberpunk" and o.is_primary), None)
    return {
        "total_outposts": len(outposts_db),
        "classic_holdings": classic_count,
        "cyberpunk_holdings": cyberpunk_count,
        "classic_primary": {
            "id": classic_primary.id if classic_primary else None,
            "name": classic_primary.name if classic_primary else None,
        },
        "cyberpunk_primary": {
            "id": cyberpunk_primary.id if cyberpunk_primary else None,
            "name": cyberpunk_primary.name if cyberpunk_primary else None,
        },
        "active_connections": len(manager.active_connections),
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# Запуск сервера
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    print("🎮 Outpost Control System Backend")
    print("📍 http://localhost:8000")
    print("📚 Документация: http://localhost:8000/docs")
    print()

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
