#!/usr/bin/env bash
set -e

echo "===================================================="
echo "Setting up GramaVise Project Environment (Linux/macOS)"
echo "===================================================="

if [ ! -f .env ]; then
    echo "Copying .env.example to .env..."
    cp .env.example .env
fi

echo "Setting up Backend..."
cd backend
if [ ! -d .venv ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt
cd ..

echo "Setting up Frontend..."
cd frontend
npm install
cd ..

echo "===================================================="
echo "Setup complete! Run backend with:"
echo "  cd backend && source .venv/bin/activate && uvicorn app.main:app --reload"
echo "Run frontend with:"
echo "  cd frontend && npm run dev"
echo "===================================================="
