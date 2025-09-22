#!/usr/bin/env bash

set -euo pipefail

# Non-interactive installer for STORM (backend + storm-ui frontend)
# - Creates a Python 3.11+ virtualenv in .venv
# - Installs knowledge_storm (editable) and backend requirements
# - Installs storm-ui npm dependencies and writes default env
# - Writes example secrets file at repo root
#
# Usage:
#   chmod +x install-storm-ui.sh
#   ./install-storm-ui.sh

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
PYTHON_BIN="python3"

echo "STORM Installer (backend + storm-ui)"
echo "Project root: ${ROOT_DIR}"
echo ""

# --- Checks ---
command -v ${PYTHON_BIN} >/dev/null 2>&1 || { echo "Error: python3 not found"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "Error: node not found"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "Error: npm not found"; exit 1; }

PY_VERSION="$(${PYTHON_BIN} -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
NODE_VERSION="$(node -v | sed 's/^v//')"

min_ver_ge() { # args: have need
  # returns 0 if have >= need
  [ "$(printf '%s\n' "$2" "$1" | sort -V | head -n1)" = "$2" ]
}

if ! min_ver_ge "${PY_VERSION}" "3.11"; then
  echo "Error: Python 3.11+ required (found ${PY_VERSION})"; exit 1;
fi
if ! min_ver_ge "${NODE_VERSION}" "18.0.0"; then
  echo "Error: Node.js 18+ required (found ${NODE_VERSION})"; exit 1;
fi

echo "✓ Python ${PY_VERSION} and Node ${NODE_VERSION} detected"

# --- Python venv ---
if [ ! -d "${VENV_DIR}" ]; then
  echo "Creating virtual environment at ${VENV_DIR}"
  ${PYTHON_BIN} -m venv "${VENV_DIR}"
else
  echo "Using existing virtual environment at ${VENV_DIR}"
fi

PIP_BIN="${VENV_DIR}/bin/pip"
PY_BIN="${VENV_DIR}/bin/python"

echo "Upgrading pip/setuptools/wheel"
"${PIP_BIN}" install --upgrade pip setuptools wheel

echo "Installing knowledge_storm (editable)"
"${PIP_BIN}" install -e "${ROOT_DIR}"

# Backend requirements (prefer pinned file if present)
BACKEND_REQ_TXT="${ROOT_DIR}/backend/requirements-backend.txt"
if [ ! -f "${BACKEND_REQ_TXT}" ]; then
  BACKEND_REQ_TXT="${ROOT_DIR}/backend/requirements.txt"
fi
echo "Installing backend requirements from ${BACKEND_REQ_TXT}"
"${PIP_BIN}" install -r "${BACKEND_REQ_TXT}"

# --- Frontend deps ---
FRONTEND_DIR="${ROOT_DIR}/frontend/storm-ui"
if [ ! -d "${FRONTEND_DIR}" ]; then
  echo "Error: frontend/storm-ui not found"; exit 1;
fi

echo "Installing storm-ui dependencies"
pushd "${FRONTEND_DIR}" >/dev/null
if [ -f "package-lock.json" ]; then
  npm ci
else
  npm install
fi

# Write default .env.local if not exists
if [ ! -f ".env.local" ]; then
  cat > .env.local << 'ENVEOF'
NEXT_PUBLIC_API_URL=http://localhost:8000/api
ENVEOF
  echo "Created frontend .env.local (NEXT_PUBLIC_API_URL=http://localhost:8000/api)"
fi
popd >/dev/null

# --- Example secrets ---
SECRETS_EXAMPLE_PATH="${ROOT_DIR}/secrets.example.toml"
if [ ! -f "${SECRETS_EXAMPLE_PATH}" ]; then
  cat > "${SECRETS_EXAMPLE_PATH}" << 'SEOFE'
# Copy to secrets.toml and fill at least ONE LLM key and ONE search key

# ===== LLM Providers =====
# OPENAI_API_KEY = "sk-..."
# ANTHROPIC_API_KEY = "sk-ant-..."
# # Azure OpenAI (optional)
# AZURE_API_KEY = "..."
# AZURE_API_BASE = "https://your-resource.openai.azure.com/"
# AZURE_API_VERSION = "2024-02-15-preview"

# ===== Search Providers =====
# BING_SEARCH_API_KEY = "..."
# YDC_API_KEY = "..."        # You.com
# TAVILY_API_KEY = "..."
# BRAVE_API_KEY = "..."
SEOFE
  echo "Wrote ${SECRETS_EXAMPLE_PATH}. Copy to secrets.toml and fill keys."
fi

echo ""
echo "✓ Installation complete"
echo ""
echo "Next steps:"
echo "1) Copy ${SECRETS_EXAMPLE_PATH} to ${ROOT_DIR}/secrets.toml and add your API keys"
echo "2) Start backend: ${PY_BIN} ${ROOT_DIR}/backend/main.py"
echo "3) Start frontend: (cd ${FRONTEND_DIR} && npm run dev)"
echo "   Then open http://localhost:3000"



