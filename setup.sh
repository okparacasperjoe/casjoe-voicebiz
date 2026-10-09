#!/usr/bin/env bash
# setup.sh — VoiceBiz one-time development environment setup
# Run this once after cloning the repository.
set -e

echo "=== Casjoe VoiceBiz Setup ==="

# ─── 1. Pull N-ATLAS GGUF via Ollama ──────────────────────────────────────────
echo ""
echo "[1/4] Pulling N-ATLAS GGUF model via Ollama..."
echo "      This downloads ~4GB. It will take several minutes."
ollama pull hf.co/QuantFactory/N-ATLaS-GGUF:Q4_K_M
echo "      N-ATLAS model ready."

# ─── 2. Backend Python environment ────────────────────────────────────────────
echo ""
echo "[2/4] Setting up Python backend..."
cd backend
python -m venv .venv
source .venv/bin/activate 2>/dev/null || .venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt
echo "      Python dependencies installed."

# Copy .env template
if [ ! -f .env ]; then
  cp .env.example .env
  echo "      Created backend/.env — fill in your values."
fi
cd ..

# ─── 3. Frontend Node dependencies ────────────────────────────────────────────
echo ""
echo "[3/4] Installing frontend dependencies..."
cd frontend
npm install
echo "      Frontend dependencies installed."
cd ..

# ─── 4. Create upload directory ───────────────────────────────────────────────
echo ""
echo "[4/4] Creating directories..."
mkdir -p backend/uploads/audio
echo "      Done."

echo ""
echo "=== Setup complete ==="
echo ""
echo "Next steps:"
echo "  1. Edit backend/.env with your database URL and Casjoe Biz JWT secret"
echo "  2. Start Ollama:   ollama serve"
echo "  3. Start backend:  cd backend && uvicorn main:app --reload"
echo "  4. Start frontend: cd frontend && npm run dev"
echo "  5. Health check:   http://localhost:8000/api/v1/health"
