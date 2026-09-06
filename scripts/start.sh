#!/bin/bash
# start.sh
# Sets up the Python environment on the Raspberry Pi (if needed) and starts
# the home monitor. Re-run at any time — setup steps are skipped if already done.

set -e

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$REPO_DIR/.venv"

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
PACKAGES=(python3 python3-venv python3-pip libopenjp2-7)
MISSING=()
for pkg in "${PACKAGES[@]}"; do
    dpkg -s "$pkg" &>/dev/null || MISSING+=("$pkg")
done
# pick the right libtiff version
dpkg -s libtiff6 &>/dev/null || dpkg -s libtiff5 &>/dev/null || MISSING+=(libtiff6)

if [ ${#MISSING[@]} -gt 0 ]; then
    echo "==> Installing system packages: ${MISSING[*]}"
    sudo apt-get update -qq
    sudo apt-get install -y -qq "${MISSING[@]}" || \
    sudo apt-get install -y -qq "${MISSING[@]/%6/5}"
else
    echo "==> System packages already installed, skipping"
fi

# ── 3. Python virtual environment ────────────────────────────────────────────
if [ ! -d "$VENV_DIR" ]; then
    echo "==> Creating virtual environment at $VENV_DIR"
    python3 -m venv "$VENV_DIR"
fi

# ── 4. Install Python dependencies ───────────────────────────────────────────
echo "==> Installing Python dependencies"
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet -e "$REPO_DIR"

# ── 5. Install systemd service ────────────────────────────────────────────────
echo "==> Installing systemd service"
sudo cp "$REPO_DIR/scripts/home-monitor.service" /etc/systemd/system/home-monitor.service
sudo systemctl daemon-reload
sudo systemctl enable --now home-monitor

echo ""
echo "    Monitor is running as a systemd service."
echo "    Status:   systemctl status home-monitor"
echo "    Logs:     journalctl -u home-monitor -f"
echo "    Restart:  sudo systemctl restart home-monitor"
echo "    Stop:     sudo systemctl stop home-monitor"
