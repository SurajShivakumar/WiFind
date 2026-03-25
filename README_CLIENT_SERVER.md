# WiFi Heatmap - Client-Server Architecture

## Architecture Overview

**Windows PC (Server):**
- Runs the Flask web server
- Displays the heatmap interface
- Receives WiFi signal data from Raspberry Pi

**Raspberry Pi (Client):**
- Scans WiFi signal strength
- Sends data to the PC server
- You walk around with it

## Setup Instructions

### 1. On Your Windows PC:

**Install Python (if not already installed):**
- Download from: https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation

**Install required packages:**
```powershell
pip install flask flask-socketio
```

**Find your PC's IP address:**
```powershell
ipconfig
```
Look for your IPv4 address (e.g., 192.168.1.100 or 10.185.x.x)

**Start the server:**
```powershell
python wifi_heatmap_server.py
```

Or double-click: `start_server.bat`

**Open browser:**
```
http://localhost:5000
```

### 2. On Your Raspberry Pi:

**Transfer the client script:**
```bash
scp wifi_scanner_client.py admin@10.185.124.49:/home/admin/
```

**SSH into the Pi:**
```bash
ssh admin@10.185.124.49
```

**Install requests library (if not installed):**
```bash
pip3 install requests
```

**Run the client (replace <PC_IP> with your Windows PC IP):**
```bash
sudo python3 wifi_scanner_client.py --server http://<PC_IP>:5000
```

Example:
```bash
sudo python3 wifi_scanner_client.py --server http://192.168.1.100:5000
```

### 3. Use the System:

1. **Calibrate the room** in the web interface (click 4 corners)
2. **Walk around** with the Raspberry Pi
3. **Watch the heatmap** update in real-time on your PC!

## Troubleshooting

### Can't connect from Pi to PC:

**Check Windows Firewall:**
```powershell
# Allow Python through firewall
New-NetFirewallRule -DisplayName "Python Flask" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
```

**Test connection from Pi:**
```bash
curl http://<PC_IP>:5000/api/status
```

### No signal data:

- Make sure you're running the client with `sudo`
- Check that wlan0 is the correct interface: `ip link`
- Verify Pi is connected to WiFi: `iw wlan0 link`

## Files

- `wifi_heatmap_server.py` - Web server (runs on Windows PC)
- `wifi_scanner_client.py` - WiFi scanner (runs on Raspberry Pi)
- `templates/index.html` - Web interface
- `static/heatmap.js` - Frontend JavaScript
- `start_server.bat` - Quick start script for Windows

## Command Line Options (Client)

```bash
python3 wifi_scanner_client.py --server http://PC_IP:5000 --interface wlan0 --interval 0.5
```

- `--server` - PC server URL (required)
- `--interface` - WiFi interface name (default: wlan0)
- `--interval` - Scan interval in seconds (default: 0.5)
