#!/bin/bash
# start.sh
# Sets up the Python environment on the Raspberry Pi (if needed) and starts
# the home monitor. Re-run at any time — setup steps are skipped if already done.

set -e

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$REPO_DIR/.venv"
MAIN_SCRIPT="$REPO_DIR/src/run.py"

echo "==> Home Monitor"
echo "    Repo : $REPO_DIR"

# ── 1. Enable SPI (required for e-ink display) ────────────────────────────────
if command -v raspi-config &>/dev/null; then
    echo "==> Enabling SPI interface"
    sudo raspi-config nonint do_spi 0
else
    echo "    (raspi-config not found — skipping SPI setup)"
fi

# ── 2. System packages ────────────────────────────────────────────────────────
echo "==> Installing system packages"
sudo apt-get update -qq
sudo apt-get install -y -qq python3 python3-venv python3-pip libopenjp2-7 libtiff5

# ── 3. Python virtual environment ────────────────────────────────────────────
if [ ! -d "$VENV_DIR" ]; then
    echo "==> Creating virtual environment at $VENV_DIR"
    python3 -m venv "$VENV_DIR"
fi

# ── 4. Install Python dependencies ───────────────────────────────────────────
echo "==> Installing Python dependencies"
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet -e "$REPO_DIR"

# ── 5. Run ────────────────────────────────────────────────────────────────────
echo "==> Starting home monitor (Ctrl+C to stop)"
export TFL_API_KEY="${TFL_API_KEY:-}"
exec "$VENV_DIR/bin/python" "$MAIN_SCRIPT"
