{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "outpost-backend-env";
  
  buildInputs = with pkgs; [
    # Python и основные зависимости
    python311
    python311Packages.pip
    python311Packages.virtualenv
    
    # FastAPI и Uvicorn
    python311Packages.fastapi
    python311Packages.uvicorn
    python311Packages.pydantic
    python311Packages.pydantic-settings
    
    # JWT и криптография
    python311Packages.pyjwt
    python311Packages.cryptography
    python311Packages.python-jose
    
    # Дополнительные утилиты
    python311Packages.python-dotenv
    
    # Для разработки
    python311Packages.pytest
    python311Packages.black
    python311Packages.flake8
    
    # Утилиты
    curl
    git
  ];

  shellHook = ''
    # Создать виртуальное окружение если его нет
    if [ ! -d ".venv" ]; then
      echo "🔨 Creating virtual environment..."
      python -m venv .venv
    fi
    
    # Активировать виртуальное окружение
    source .venv/bin/activate
    
    # Установить зависимости если requirements.txt существует
    if [ -f "requirements.txt" ] && [ ! -f ".venv/.installed" ]; then
      echo "📦 Installing Python dependencies..."
      pip install -r requirements.txt
      touch .venv/.installed
    fi
    
    echo ""
    echo "✅ Outpost Backend Environment Loaded"
    echo ""
    echo "Available commands:"
    echo "  python main.py          - Run the backend server"
    echo "  pytest                  - Run tests"
    echo "  black .                 - Format code"
    echo "  flake8 .                - Check code style"
    echo ""
    echo "Server will be available at: http://localhost:8000"
    echo "API Documentation: http://localhost:8000/docs"
    echo ""
  '';

  # Установить переменные окружения для тестирования
  PYTHONPATH = ".";
  ENVIRONMENT = "development";
  DEBUG = "True";
}
