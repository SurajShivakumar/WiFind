# GPS Calibration Guide

## 🎯 What's New
Your WiFi heatmap system now has **GPS-based automatic positioning**! No more manual clicking - your phone's GPS will automatically place WiFi signal readings on the map.

## 📱 Setup Steps

### 1. Configure OwnTracks App
1. Open **OwnTracks** on your Android phone
2. Go to **Settings** (⚙️ icon)
3. Set **Mode** to: **HTTP**
4. Set **URL** to: `http://10.185.124.107:5000/api/gps`
5. Set **Device ID** to anything (e.g., "phone")
6. Set **User ID** to anything (e.g., "user")
7. Enable **Location** reporting
8. Set update interval (recommended: 1-2 seconds for mapping)

### 2. Calibrate Room Boundaries
To accurately map GPS coordinates to your room:

1. **Open the web interface**: http://10.185.124.107:5000
2. Click the **"GPS Calibrate (Walk to Corners)"** button
3. **Walk to the TOP-LEFT corner** of your room with your phone
4. Click **"Record Corner 1"** and wait 2 seconds
5. **Walk to the TOP-RIGHT corner**
6. Click **"Record Corner 2"** and wait 2 seconds
7. **Walk to the BOTTOM-RIGHT corner**
8. Click **"Record Corner 3"** and wait 2 seconds
9. **Walk to the BOTTOM-LEFT corner**
10. Click **"Record Corner 4"** and wait 2 seconds
11. You'll see "GPS Calibration Complete!"

### 3. Start Mapping
1. Raspberry Pi should already be running and sending WiFi signals
2. Walk around the room with your phone (OwnTracks running)
3. WiFi signals will **automatically appear** on the heatmap at your GPS location
4. Watch the colored gradient build in real-time!

## 🎨 How It Works

### Color Guide
- **Red** = Strong signal (-30 to -50 dBm)
- **Yellow** = Medium signal (-50 to -70 dBm)
- **Green** = Weak signal (-70 to -90 dBm)

### Automatic Linking
- Your phone sends GPS coordinates every 1-2 seconds
- Raspberry Pi sends WiFi signal strength every second
- Server automatically links the latest GPS location with each WiFi reading
- Points appear on the canvas at the correct physical position

## 🔧 Troubleshooting

### No GPS Data Appearing?
1. Check OwnTracks is set to HTTP mode (not MQTT)
2. Verify URL is correct: `http://10.185.124.107:5000/api/gps`
3. Check phone has Location Services enabled
4. Open browser console (F12) and look for "📍 GPS Update" messages
5. Server terminal should show: "📍 GPS received: Lat=... Lon=..."

### WiFi Points Not Positioned?
1. Make sure you've completed GPS calibration (all 4 corners)
2. Check that OwnTracks is actively sending GPS
3. Verify Raspberry Pi is running: `python pi_simple_http.py`
4. Look for "✅ WiFi signal auto-positioned with GPS" in server logs

### Reset Everything
Click **"Reset Calibration"** button to clear GPS corners and start over.

## 📊 Status Indicators
- **Total Points**: All WiFi signals received
- **Positioned Points**: WiFi signals with GPS locations
- **Calibration Status**: GPS calibration progress (4/4 = complete)
- **Latest Signal**: Most recent WiFi strength reading

## 🚀 Quick Test
Test GPS endpoint from PowerShell:
```powershell
$body = @{
    lat = 47.6062
    lon = -122.3321
    acc = 10
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://10.185.124.107:5000/api/gps" -Method POST -Body $body -ContentType "application/json"
```

You should see: `{"status":"success",...}`

## 📝 Files Modified
- `heatmap_server.py` - Added GPS calibration backend
- `templates/index.html` - Added GPS Calibrate button
- `static/heatmap.js` - Added GPS calibration handlers and auto-positioning
- `pi_simple_http.py` - Raspberry Pi WiFi scanner (already working)

## ✅ Current Status
- ✅ Server running on http://10.185.124.107:5000
- ✅ Raspberry Pi sending WiFi signals from 10.185.124.49
- ✅ GPS endpoint ready at /api/gps
- ✅ GPS calibration system implemented
- ⏳ **Next**: Configure OwnTracks and calibrate room!

---

**Ready to map your room!** 🗺️📶
