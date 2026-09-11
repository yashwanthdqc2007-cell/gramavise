@echo off
echo ====================================================
echo Setting up GramaVise Project Environment (Windows)
echo ====================================================

if not exist .env (
    echo Copying .env.example to .env...
    copy .env.example .env
)

echo Setting up Backend...
cd backend
if not exist .venv (
    echo Creating Python virtual environment...
    python -m venv .venv
)
call .venv\Scripts\activate.bat
pip install -r requirements.txt
cd ..

echo Setting up Frontend...
cd frontend
call npm install
cd ..

echo ====================================================
echo Setup complete! Run backend with:
echo   cd backend ^&^& .venv\Scripts\activate ^&^& uvicorn app.main:app --reload
echo Run frontend with:
echo   cd frontend ^&^& npm run dev
echo ====================================================
