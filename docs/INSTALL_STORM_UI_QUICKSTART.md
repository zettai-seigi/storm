## STORM + storm-ui Quickstart (Concise)

Follow these steps to install and run the full application (backend + Next.js UI).

### 1) Prerequisites
- Python 3.11+
- Node.js 18+ and npm 9+
- Git

macOS tip:
```bash
xcode-select --install
brew install python@3.11 node
```

### 2) Clone
```bash
git clone https://github.com/stanford-oval/storm.git
cd storm
```

### 3) Install (Non-interactive)
```bash
chmod +x ./install-storm-ui.sh
./install-storm-ui.sh
```
What it does:
- Creates .venv and installs Python deps (editable knowledge_storm + backend)
- Installs frontend deps under frontend/storm-ui
- Writes frontend .env.local with NEXT_PUBLIC_API_URL
- Writes secrets.example.toml

Manual alternative:
```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e .
pip install -r backend/requirements-backend.txt
cd frontend/storm-ui && npm install && cd -
```

### 4) Configure API Keys
```bash
cp secrets.example.toml secrets.toml
# Edit secrets.toml and set at least one LLM key and one search key:
# OPENAI_API_KEY = "sk-..."   OR   ANTHROPIC_API_KEY = "sk-ant-..."
# BING_SEARCH_API_KEY = "..." OR   YDC_API_KEY = "..."  OR TAVILY_API_KEY = "..."
```

### 5) Run
Terminal A (backend):
```bash
./.venv/bin/python backend/main.py
```

Terminal B (frontend):
```bash
cd frontend/storm-ui
npm run dev
```

Open http://localhost:3000

Health check:
```bash
curl http://localhost:8000/api/health
```

### 6) Production (optional)
```bash
# Backend
./.venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4

# Frontend
cd frontend/storm-ui
npm run build
npm start
```


