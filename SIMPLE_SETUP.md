# 🚀 SIMPLE SETUP - No Calibration Needed!

## ✅ What Changed

**REMOVED:**
- ❌ Room calibration (you don't need it!)
- ❌ Corner walking system
- ❌ Room boundary detection
- ❌ Complex GPS mapping

**SIMPLIFIED:**
- ✅ Just walk around with your phone
- ✅ Raspberry Pi scans WiFi automatically
- ✅ Map shows signal strength wherever you are
- ✅ 🟢 Green = strong signal, 🔴 Red = weak signal

## 🎯 Super Quick Setup

### Step 1: Get FREE Mapbox Token (5 minutes)
1. Go to: https://account.mapbox.com/
2. Sign up (free!)
3. Copy your token (starts with `pk.`)
4. Open: `static/heatmap_mapbox.js`
5. Line 7: Replace the example token with yours
6. Save file
7. **Hard refresh browser**: `Ctrl + Shift + R`

### Step 2: Set Up Phone GPS (5 minutes)
1. Install **OwnTracks** app (Android/iOS)
2. Open app settings
3. Set Mode: **HTTP**
4. Set URL: `http://10.185.124.107:5000/api/gps`
5. Turn on tracking

### Step 3: Start Mapping (NOW!)
1. Open browser: http://10.185.124.107:5000
2. Just walk around your house with phone in pocket!
3. Watch the map fill with colored dots:
   - 🟢 Green = Excellent signal
   - 🔵 Blue = Good signal
   - 🟡 Yellow = Fair signal
   - 🔴 Red = Weak signal

## 🎨 How It Works

### No Configuration Needed!
- Your **phone** sends GPS location (latitude/longitude)
- Your **Raspberry Pi** scans WiFi signal strength
- The **server** links them together automatically
- The **map** shows exactly where each signal was measured

### Adjust Heatmap Display
Two sliders in the sidebar:
- **Radius**: Make spots bigger/smaller (default 40px)
- **Opacity**: Make heatmap more/less see-through (default 0.7)

### Map Styles
Click dropdown in top-left corner:
- 🛰️ Satellite - See actual buildings
- 🗺️ Streets - Clean map view
- ☀️ Light - Minimal style
- 🌙 Dark - Dark mode

## 📊 What You'll See

### Status Bar (Top)
- **Latest Signal**: Current WiFi strength (-30 to -90 dBm)
- **Network**: WiFi SSID name
- **Total Points**: Number of measurements taken
- **Mapped Points**: How many have GPS location

### Map (Center)
- Colored dots = Individual measurements
- Click any dot to see details (dBm, GPS coords, SSID)
- Gradient overlay = Heatmap showing overall signal pattern

### Sidebar Controls
- **Radius/Opacity Sliders**: Adjust heatmap appearance
- **Clear All Data**: Start fresh

## 🔧 Troubleshooting

### Map is gray or shows error
**Problem**: Need Mapbox token
**Fix**: Get token at https://account.mapbox.com/ (Step 1 above)

### No dots appearing on map
**Problem**: GPS not configured yet
**Fix**: Set up OwnTracks app (Step 2 above)
**Note**: Pi is already sending WiFi signals (check logs), they just need GPS to show on map!

### Seeing dots but no gradient
**Problem**: Radius too small
**Fix**: Use radius slider, increase to 40-60px

### Map shows old version
**Problem**: Browser cache
**Fix**: Hard refresh with `Ctrl + Shift + R`

## 🎉 That's It!

No calibration needed! Just:
1. Get Mapbox token → Add to code → Refresh
2. Set up OwnTracks GPS on phone
3. Walk around → Watch heatmap build in real-time!

Your Raspberry Pi is **already working** (server logs show continuous WiFi signals).
Your server is **already running** (http://10.185.124.107:5000).

Just need those 2 quick setup steps and you're mapping! 📡🗺️
