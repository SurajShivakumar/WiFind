# WiFi Heatmap - T-Mobile 5G Room Mapper

Real-time WiFi signal strength visualization with room calibration and dynamic heatmap generation.

## Features

- **4-Point Room Calibration**: Map your physical room to the digital canvas
- **Real-Time Signal Monitoring**: Continuously tracks T-Mobile 5G signal strength
- **Dynamic Heatmap**: Visual representation of signal strength throughout the room
- **WebSocket Updates**: Live updates as you walk around with the Raspberry Pi
- **Responsive Web Interface**: Access from any device on your network

## Installation

### On your Raspberry Pi:

1. **Install Python dependencies:**
```bash
pip3 install flask flask-socketio python-socketio
```

2. **Transfer files to Raspberry Pi:**
```bash
# From your Windows machine
scp wifi_heatmap_server.py admin@<raspberry-pi-ip>:/home/admin/
scp -r templates admin@<raspberry-pi-ip>:/home/admin/
scp -r static admin@<raspberry-pi-ip>:/home/admin/
scp requirements.txt admin@<raspberry-pi-ip>:/home/admin/
```

3. **On Raspberry Pi, install requirements:**
```bash
cd /home/admin
pip3 install -r requirements.txt
```

4. **Run the server (requires sudo for WiFi scanning):**
```bash
sudo python3 wifi_heatmap_server.py
```

## Usage

### Step 1: Access the Web Interface

1. Find your Raspberry Pi's IP address:
```bash
hostname -I
```

2. Open a browser and navigate to:
```
http://<raspberry-pi-ip>:5000
```

### Step 2: Calibrate Your Room

1. Click **"Start Calibration"**
2. Click on the canvas to mark 4 corners of your room in order:
   - **Top-Left** corner
   - **Top-Right** corner
   - **Bottom-Right** corner
   - **Bottom-Left** corner
3. The calibration is automatically saved

### Step 3: Start Scanning

1. Click **"Start Scanning"**
2. Walk around your room with the Raspberry Pi
3. Watch the heatmap update in real-time!

### Understanding the Heatmap

The heatmap uses color gradients to show signal strength:

- 🔴 **Red** (-90 to -80 dBm): Weak signal
- 🟠 **Orange** (-80 to -70 dBm): Poor signal
- 🟡 **Yellow** (-70 to -60 dBm): Fair signal
- 🟢 **Light Green** (-60 to -50 dBm): Good signal
- 💚 **Green** (-50 to -30 dBm): Excellent signal

## API Endpoints

- `GET /` - Web interface
- `GET /api/status` - Current system status
- `GET /api/data` - All collected signal data
- `GET /api/calibration` - Get calibration points
- `POST /api/calibration` - Save calibration points
- `GET /api/scan/start` - Start scanning
- `GET /api/scan/stop` - Stop scanning
- `GET /api/clear` - Clear all data

## WebSocket Events

- `connect` - Client connected
- `disconnect` - Client disconnected
- `signal_update` - Real-time signal strength update

## Architecture

```
┌─────────────────┐         WebSocket          ┌──────────────┐
│  Raspberry Pi   │◄──────────────────────────►│ Web Browser  │
│                 │                             │              │
│  Flask Server   │         HTTP API            │   Canvas     │
│  WiFi Scanner   │◄──────────────────────────►│   Heatmap    │
└─────────────────┘                             └──────────────┘
```

## Improvements for Production

### Current State (Demo):
- Position is simulated with random walk
- Works great for testing the visualization

### For Real-World Use:
Add one of these positioning methods:

1. **Manual Input**: Add buttons to mark "I'm here" at specific locations
2. **GPS**: Use a GPS module on the Raspberry Pi
3. **Bluetooth Beacons**: Place beacons at known locations for triangulation
4. **Accelerometer/Gyroscope**: Track movement from a starting point
5. **Camera + Computer Vision**: Use visual markers in the room

### Example: Adding Manual Position Marking

Add this button to the HTML:
```javascript
// In heatmap.js
socket.on('mark_position', (data) => {
    currentPosition = data.position;
});

// Add button handler
document.getElementById('markPositionBtn').addEventListener('click', () => {
    // Prompt for X, Y coordinates
    const x = parseFloat(prompt('Enter X coordinate (0-10 meters):'));
    const y = parseFloat(prompt('Enter Y coordinate (0-10 meters):'));
    socket.emit('set_position', { x, y });
});
```

## Troubleshooting

### "Permission denied" when scanning WiFi
- Make sure to run with `sudo`

### Cannot connect to web interface
- Check Raspberry Pi IP address with `hostname -I`
- Ensure firewall allows port 5000
- Try from another device on the same network

### No signal data appearing
- Verify WiFi interface name (default is `wlan0`)
- Check that Raspberry Pi is connected to WiFi
- Run `iw wlan0 link` manually to test

### Heatmap not showing
- Complete the 4-point calibration first
- Start scanning
- Walk around with the Raspberry Pi

## Next Steps

1. **Add Position Tracking**: Implement one of the positioning methods above
2. **Save Sessions**: Export heatmap data to file
3. **Multiple Floors**: Add floor selection
4. **Comparison Mode**: Compare signal strength at different times
5. **Alert System**: Notify when signal drops below threshold

## License

MIT License - Feel free to modify and use!
