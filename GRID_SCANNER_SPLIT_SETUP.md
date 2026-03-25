# 🎙️ WiFi Grid Scanner - Split System Setup

## System Overview
- **Windows Laptop**: Gives voice commands, shows web interface, runs AI analysis
- **Raspberry Pi**: Scans WiFi networks at each position

## Setup Instructions

### 1. On Windows Laptop

Install Flask and Flask-SocketIO:
```powershell
pip install flask flask-socketio requests
```

Run the controller:
```powershell
python grid_controller_windows.py
```

Open browser to:
```
http://localhost:5000
```

### 2. On Raspberry Pi

Transfer `pi_grid_client.py` to the Pi (via WinSCP or similar).

Install required packages:
```bash
sudo apt-get update
sudo apt-get install wireless-tools
pip3 install requests
```

Edit the file to set your laptop's IP:
```python
CONTROLLER_URL = "http://YOUR_LAPTOP_IP:5000"
```

Run the client:
```bash
python3 pi_grid_client.py
```

## How to Use

1. **Start controller on laptop** - Opens web interface
2. **Start client on Pi** - Waits for commands
3. **Click "Start Scan" on laptop** - Voice welcomes you
4. **Move Pi to first position** (voice tells you where)
5. **Click "Next Position"** - Pi automatically scans WiFi
6. **Repeat for all 9 positions**
7. **AI analysis plays** - Results shown on screen

## The Flow

```
Laptop (Voice) → "Move Pi to bottom left"
You → Move Pi to bottom left corner
Laptop (Web) → Click "Next Position"
Pi → Scans WiFi automatically
Pi → Sends data to laptop
Laptop (Voice) → "Scan complete at bottom left"
Laptop (Voice) → "Move Pi to bottom center"
... repeat for all 9 positions ...
Laptop (Voice) → "All positions scanned. Analyzing..."
Laptop (AI) → Speaks analysis and recommendations
```

## 9 Grid Positions

```
Top-Left      Top-Center      Top-Right
   (7)            (8)             (9)

Middle-Left   Center          Middle-Right
   (4)          (5)              (6)

Bottom-Left   Bottom-Center   Bottom-Right
   (1)            (2)             (3)
```

## Troubleshooting

**Pi can't connect to laptop:**
- Check laptop IP with `ipconfig` on Windows
- Update `CONTROLLER_URL` in `pi_grid_client.py`
- Make sure laptop firewall allows port 5000

**Pi not scanning:**
- Test with: `sudo iwlist wlan0 scan`
- Make sure wlan0 is your WiFi interface
- Check `sudo ifconfig` to see interfaces

**Voice not playing:**
- Check ElevenLabs API key in controller file
- Test audio with any MP3 file on Windows
- Volume up! 🔊

**AI analysis not working:**
- Check Google Gemini API key in controller file
- Internet connection required

## API Keys Already Configured

✅ ElevenLabs: `sk_92ec67...` (embedded)
✅ Google Gemini: `AIzaSyDC9E1...` (embedded)

No additional setup needed!
