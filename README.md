# WiFi Heatmap - T-Mobile 5G Room Mapper

## Quick Start

### 1. On Windows PC:

**Find your PC's IP:**
```powershell
ipconfig
```

**Install dependencies:**
```powershell
pip install flask flask-socketio flask-cors requests
```

**Start server:**
```powershell
python heatmap_server.py
```

**Open browser:**
```
http://localhost:5000
```

### 2. On Raspberry Pi:

**Transfer client:**
```bash
scp pi_client.py admin@10.19.3.201:/home/admin/
```

**SSH and run (replace <PC_IP> with your actual IP):**
```bash
ssh admin@10.19.3.201
sudo python3 pi_client.py --server http://<PC_IP>:5000
```

### 3. Use the System:

1. **Calibrate:** Click "Start Calibration" and mark 4 corners
2. **Enable Mapping:** Click "Enable Mapping" button
3. **Walk around:** Move with the Raspberry Pi
4. **Mark positions:** Click on the map where you are standing
5. **Watch:** The heatmap builds in real-time with radial gradients!

## How It Works

- **Raspberry Pi** scans WiFi signal strength every second
- **PC Server** receives the signal data
- **You** click on the map to mark where you measured that signal
- **Heatmap** draws radial gradients centered at each measurement point
- **Radius size** = signal strength (stronger signal = bigger radius)
- **Color** = signal quality (red=weak, green=strong)

## Files

- `heatmap_server.py` - Server (runs on PC)
- `pi_client.py` - Client (runs on Raspberry Pi)
- `templates/index.html` - Web interface
- `static/heatmap.js` - Visualization code
