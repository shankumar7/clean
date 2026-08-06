#!/usr/bin/env bash
# Setup Script for Raspberry Pi Touchscreen Air Quality Monitor & Host Web Server

set -e

echo "=========================================================="
echo " Raspberry Pi Air Quality Monitor Setup"
echo "=========================================================="

# 1. Update package list & install system dependencies
echo "[1/4] Installing Raspberry Pi OS dependencies..."
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-pyqt6 \
    python3-pyserial \
    python3-pil \
    python3-qrcode \
    python3-flask \
    python3-gpiozero \
    libatlas-base-dev

# 2. Install Python virtualenv or pip packages
echo "[2/4] Installing Python requirements..."
pip3 install -r requirements.txt --break-system-packages || pip3 install -r requirements.txt

# 3. Enable UART Serial & GPIO permissions
echo "[3/4] Granting user access permissions to UART dialout & GPIO..."
sudo usermod -a -G dialout,gpio $USER || true

# 4. Install systemd service
echo "[4/4] Configuring systemd autostart service..."
if [ -f "systemd/airmonitor.service" ]; then
    sudo cp systemd/airmonitor.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable airmonitor.service
    echo "Autostart service registered! Use 'sudo systemctl start airmonitor' to start."
fi

echo "=========================================================="
echo " Setup complete! Reboot your Raspberry Pi to apply permissions."
echo " Run manually with: python3 main.py"
echo "=========================================================="
