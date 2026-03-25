# GPS-WiFi Heatmap System - Complete Setup

## 🎯 How It Works Now:

The system automatically combines:
1. **GPS from your phone** (via OwnTracks) → Provides location (lat/lon)
2. **WiFi signal from Raspberry Pi** → Provides signal strength (dBm)
3. **Server auto-links them** → Creates positioned heatmap points automatically!

---

## 📱 Step 1: Configure OwnTracks on Your Phone

### Android / iOS:
1. Open **OwnTracks** app
2. Go to **Settings** → **Connection**
3. Set **Mode** to **HTTP**
4. Enter URL: `http://10.185.124.107:5000/api/gps`
5. **Save** and **Start Tracking**

### What it does:
- Sends your GPS coordinates to the server every few seconds
- Server converts GPS (lat/lon) → canvas coordinates (x, y)

---

## 🖥️ Step 2: Raspberry Pi is Already Running

Your Pi is sending WiFi signal strength to the server.

**Current status:** ✅ Pi is connected and sending data

---

## 🗺️ Step 3: How Auto-Positioning Works

### The Magic:
```
1. Phone sends GPS: Lat=47.6062, Lon=-122.3321
   → Server stores: latest_gps = {lat, lon}

2. Pi sends WiFi: Signal=-45 dBm
   → Server checks: Do we have latest_gps?
   → YES! Auto-position: x=350, y=200

3. Heatmap shows: Point at (350, 200) with -45 dBm signal
```

### In the terminal you'll see:
```
📍 GPS received: Lat=47.6062, Lon=-122.3321, Accuracy=10m
✅ WiFi signal auto-positioned: -45 dBm at (350, 200) from GPS
```

---

## 🚶 Step 4: Walk Around and Map!

1. **Start OwnTracks** on your phone
2. **Walk around the room** with your phone
3. **WiFi Pi stays with you** (or in a fixed location)
4. **Map auto-builds** as you move!

---

## 📊 What You'll See:

### In Terminal:
```
📍 GPS received: Lat=47.6062, Lon=-122.3321, Accuracy=5m
✅ WiFi signal auto-positioned: -42 dBm at (380, 250) from GPS
📍 GPS received: Lat=47.6063, Lon=-122.3320, Accuracy=5m
✅ WiFi signal auto-positioned: -38 dBm at (420, 180) from GPS
```

### In Web Browser (http://localhost:5000):
- Points appear automatically on the map
- Colors show signal strength (green=strong, red=weak)
- Heatmap builds as you walk around

---

## 🎨 Coordinate Mapping:

The system maps GPS coordinates to canvas:
- **GPS bounds** → Automatically calculated from all received points
- **Canvas size** → 800x650 pixels
- **Relative positioning** → Points positioned relative to each other

Example:
```
GPS Point 1: 47.6062, -122.3321 → Canvas: (200, 300)
GPS Point 2: 47.6065, -122.3318 → Canvas: (450, 150)
GPS Point 3: 47.6060, -122.3323 → Canvas: (100, 450)
```

---

## 🧪 Test It:

### Simulate GPS from PC:
```powershell
$body = '{"lat":47.6062,"lon":-122.3321,"acc":10}' | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:5000/api/gps" -Method POST -Body $body -ContentType "application/json"
```

Watch terminal for:
```
📍 GPS received: Lat=47.6062, Lon=-122.3321, Accuracy=10m
```

Then your next WiFi signal from Pi will be auto-positioned!

---

## 📈 Current Status:

✅ Server running on http://10.185.124.107:5000
✅ GPS endpoint ready: `/api/gps`
✅ WiFi Pi connected and sending signals
✅ Auto-positioning enabled
✅ Web interface live

**Next:** Configure OwnTracks and start walking! 🚶📱
