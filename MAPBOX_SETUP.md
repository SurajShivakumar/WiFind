# 🗺️ Mapbox + Heatmap.js Setup Guide

## ✅ What's Done

Your system now uses the **wifi-heatmapper professional approach**:
- ✅ Mapbox GL JS v3.0.1 (satellite maps!)
- ✅ Heatmap.js v2.0.5 overlay (Green→Yellow→Red gradient)
- ✅ Adjustable radius/opacity controls (like wifi-heatmapper)
- ✅ GPS auto-positioning (your phone tracks location)
- ✅ Raspberry Pi WiFi scanning (automatic signal collection)
- ✅ 4-corner GPS calibration system

## 🎯 Get Your FREE Mapbox Token

### Step 1: Sign up at Mapbox
1. Go to: https://account.mapbox.com/
2. Click "Sign Up" (it's FREE!)
3. Free tier includes: **50,000 map loads/month** (plenty for your project!)

### Step 2: Create Access Token
1. After signing in, you'll see your dashboard
2. Look for "Access tokens" section
3. Copy your **default public token** (starts with `pk.`)
   - It looks like: `pk.eyJ1IjoiZXhhbXBsZSIsImEiOiJjbGV4YW1wbGUifQ.example`

### Step 3: Add Token to Code
1. Open: `static/heatmap_mapbox.js`
2. Find line 7:
   ```javascript
   mapboxgl.accessToken = 'pk.eyJ1IjoiZXhhbXBsZSIsImEiOiJjbGV4YW1wbGUifQ.example';
   ```
3. Replace the example token with YOUR token:
   ```javascript
   mapboxgl.accessToken = 'pk.YOUR_ACTUAL_TOKEN_HERE';
   ```
4. Save the file
5. **Hard refresh browser**: `Ctrl + Shift + R`

## 🚀 Testing Your Setup

### Quick Test (No GPS needed yet)
1. Open browser: http://10.185.124.107:5000
2. You should see:
   - 🛰️ Mapbox satellite map (zoomed to Seattle by default)
   - 📶 Raspberry Pi sending signals (check sidebar stats)
   - ⚠️ Points NOT appearing yet (need GPS!)

### Full Test (With GPS)
1. **Configure OwnTracks on your phone**:
   - Mode: HTTP
   - URL: `http://10.185.124.107:5000/api/gps`
   - (See GPS_WIFI_SETUP.md for details)

2. **Calibrate Room**:
   - Click "GPS Calibrate" button
   - Walk to Top-Left corner → Click "Record Corner 1/4"
   - Walk to Top-Right corner → Click "Record Corner 2/4"
   - Walk to Bottom-Right corner → Click "Record Corner 3/4"
   - Walk to Bottom-Left corner → Click "Record Corner 4/4"
   - Map will draw purple boundary around your room!

3. **Start Mapping**:
   - Just walk around with your phone!
   - Raspberry Pi sends WiFi signals every ~1 second
   - Each signal gets GPS position from your phone
   - Map shows colored dots: 🟢 Green (strong) → 🔴 Red (weak)
   - Heatmap gradient builds up automatically!

## 🎨 Features Like wifi-heatmapper

### Heatmap Controls
- **Radius Slider** (10-100px): Adjust until spots "grow together"
  - Small radius = tight spots
  - Large radius = smooth gradient
- **Opacity Slider** (0-1): Make heatmap more/less transparent
  - 0.0 = invisible
  - 1.0 = solid colors

### Map Styles
Click the dropdown in top-left:
- 🛰️ **Satellite** - Best for seeing real buildings/terrain
- 🗺️ **Streets** - Clean street map view
- ☀️ **Light** - Minimal white background
- 🌙 **Dark** - Dark mode map

### Color Gradient (Signal Strength)
Our gradient matches wifi-heatmapper exactly:
- 🟢 **Green** (-30 to -50 dBm): Excellent signal
- 🔵 **Turquoise/Blue** (-50 to -70 dBm): Good signal
- 🟡 **Yellow** (-70 to -80 dBm): Fair signal
- 🔴 **Red** (-80 to -90 dBm): Weak signal

### Click Signal Markers
Each colored dot is clickable:
- Shows exact dBm value
- WiFi SSID name
- GPS coordinates
- Signal quality percentage

## 🔧 Troubleshooting

### Map shows gray tiles or error
- **Cause**: Missing or invalid Mapbox token
- **Fix**: Get token from https://account.mapbox.com/ and add to `heatmap_mapbox.js`

### WiFi signals visible but no GPS position
- **Cause**: OwnTracks not configured yet
- **Fix**: Set up OwnTracks app (see GPS_WIFI_SETUP.md)
- **Tip**: Signals won't appear on map until GPS is linked!

### Browser shows old version
- **Cause**: Browser cache
- **Fix**: Hard refresh with `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)

### Heatmap overlay not visible
- **Cause**: Radius too small or opacity too low
- **Fix**: Adjust radius to 40-60px and opacity to 0.7

## 📊 What Makes This Better

Compared to wifi-heatmapper:
- ✅ **GPS Auto-Positioning**: No manual clicking! Phone tracks you automatically
- ✅ **Real-time Updates**: See heatmap build as you walk
- ✅ **Raspberry Pi Integration**: Dedicated WiFi scanner (more accurate)
- ✅ **Live Satellite View**: See actual building/room layout
- ✅ **Socket.IO**: Real-time data streaming
- ✅ **4-Corner Calibration**: Automatically maps GPS to your room boundaries

Like wifi-heatmapper:
- ✅ **Heatmap.js Overlay**: Professional gradient visualization
- ✅ **Adjustable Controls**: Radius/opacity sliders
- ✅ **Green→Yellow→Red**: Same color scheme
- ✅ **Clean UI**: Professional look

## 🎯 Next Steps

1. **Get Mapbox token** (5 minutes)
2. **Add token to code** (1 minute)
3. **Refresh browser** (5 seconds)
4. **Set up OwnTracks** (5 minutes)
5. **Calibrate 4 corners** (2 minutes)
6. **Start walking and mapping!** 🚶‍♂️📡

## 📝 Files Updated

- `templates/index.html` - Mapbox + Heatmap.js libraries
- `static/heatmap_mapbox.js` - **NEW FILE** with Mapbox implementation
- This guide - Setup instructions

## 🆘 Need Help?

Check these files:
- `GPS_WIFI_SETUP.md` - OwnTracks setup
- `GPS_CALIBRATION_GUIDE.md` - Calibration walkthrough
- `README.md` - General system overview

Your Raspberry Pi is already working! (Logs show continuous signals)
Your server is running! (http://10.185.124.107:5000)
Just need: Mapbox token + OwnTracks GPS = DONE! 🎉
