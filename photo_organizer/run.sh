#!/usr/bin/env bash
# ─────────────────────────────────────────────
#  Photo Organizer – one-click launcher
#  Usage:  bash run.sh   (or double-click via Finder → open with Terminal)
# ─────────────────────────────────────────────

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📷  Photo Organizer – Starting up …"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. Make sure Python 3 is available
if ! command -v python3 &>/dev/null; then
    echo "❌  Python 3 is not installed. Please install it from https://python.org"
    exit 1
fi

# 2. Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "🔧  Creating virtual environment …"
    python3 -m venv "$VENV_DIR"
fi

# 3. Activate venv
source "$VENV_DIR/bin/activate"

# 4. Install / upgrade dependencies silently
echo "📦  Installing dependencies (first run may take a minute) …"
pip install --quiet --upgrade pip
pip install --quiet -r "$SCRIPT_DIR/requirements.txt"

echo "✅  Dependencies ready."
echo ""

# 5. Launch the app
python3 "$SCRIPT_DIR/main.py"
