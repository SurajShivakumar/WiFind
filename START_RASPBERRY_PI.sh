#!/bin/bash
# WiFi Scanner Client for Raspberry Pi
# This script will start sending WiFi signal data to your PC

SERVER_IP="10.185.124.107"
SERVER_PORT="5000"
INTERFACE="wlan0"

echo "=============================================="
echo "WiFi Heatmap Scanner - Raspberry Pi Client"
echo "=============================================="
echo "Server: http://${SERVER_IP}:${SERVER_PORT}"
echo "Interface: ${INTERFACE}"
echo "=============================================="
echo ""
echo "Starting WiFi scanner..."
echo "Press Ctrl+C to stop"
echo ""

# Run the scanner with sudo (required for WiFi scanning)
sudo python3 pi_client_simple.py

