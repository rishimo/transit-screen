#!/bin/bash
set -e

echo "======================================"
echo "Transit Screen - Raspberry Pi Setup"
echo "======================================"
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo "⚠ Warning: This script is designed for Raspberry Pi"
    echo "   You may need to adjust GPIO settings manually"
    echo ""
fi

# Install uv if not present
if ! command -v uv &> /dev/null; then
    echo "Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

# Install Python dependencies
echo "Installing Python dependencies..."
cd "$(dirname "$0")/.."
uv sync

# Check for .env file
if [ ! -f .env ]; then
    echo ""
    echo "⚠ Missing .env file"
    echo "  Copy .env.example to .env and add your API keys:"
    echo ""
    echo "    cp .env.example .env"
    echo "    nano .env"
    echo ""
    exit 1
fi

# Check for config.yaml
if [ ! -f config.yaml ]; then
    echo ""
    echo "⚠ Missing config.yaml file"
    echo "  Copy config.example.yaml to config.yaml and customize:"
    echo ""
    echo "    cp config.example.yaml config.yaml"
    echo "    nano config.yaml"
    echo ""
    exit 1
fi

# Install systemd service
echo ""
echo "Installing systemd service..."
sudo cp transit-screen.service /etc/systemd/system/
sudo systemctl daemon-reload

echo ""
echo "======================================"
echo "✓ Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Enable the service to start on boot:"
echo "     sudo systemctl enable transit-screen"
echo ""
echo "2. Start the service:"
echo "     sudo systemctl start transit-screen"
echo ""
echo "3. Check status:"
echo "     sudo systemctl status transit-screen"
echo ""
echo "4. View logs:"
echo "     sudo journalctl -u transit-screen -f"
echo ""
echo "To stop the service:"
echo "     sudo systemctl stop transit-screen"
echo ""
