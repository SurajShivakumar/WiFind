# 🗺️ Google Maps Integration - Setup Guide

## ✨ What's New

Your WiFi heatmapper now uses **Google Maps** with a real heatmap visualization layer! Inspired by [wifi-heatmapper](https://github.com/hnykda/wifi-heatmapper), this version combines:

- ✅ **Google Maps** with satellite/hybrid/terrain views
- ✅ **Heatmap Layer** - gradient from Green (strong) → Yellow → Red (weak)
- ✅ **GPS phone tracking** (OwnTracks app)
- ✅ **Raspberry Pi WiFi scanning**
- ✅ **Automatic positioning** - no manual clicking!

## 🔑 Step 1: Get Google Maps API Key

### Create API Key (FREE for personal use)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable these APIs:
   - **Maps JavaScript API**
   - **Maps Visualization API**
4. Go to **Credentials** → **Create Credentials** → **API Key**
5. Copy your API key (looks like: `AIzaSyB...`)

### Restrict API Key (Security)

1. Click **Edit** on your API key
2. Under **Application restrictions**:
   - Select "HTTP referrers"
   - Add: `http://localhost:5000/*`
   - Add: `http://10.185.124.107:5000/*`
3. Under **API restrictions**:
   - Select "Restrict key"
   - Choose: Maps JavaScript API, Visualization API
4. Click **Save**

### Free Tier Limits

- **$200 free credit** every month
- ~28,000 map loads per month FREE
- Perfect for personal WiFi mapping!

## 🛠️ Step 2: Add API Key to Your App

Edit `templates/index.html` line 6:

```html
<script src="https://maps.googleapis.com/maps/api/js?key=YOUR_GOOGLE_MAPS_API_KEY&libraries=visualization" async defer></script>
```

Replace `YOUR_GOOGLE_MAPS_API_KEY` with your actual API key.

## 🎨 How It Works

### Heatmap Gradient (Inspired by wifi-heatmapper)
- 🟢 **Green**: Excellent signal (-30 to -50 dBm)
- 🟡 **Yellow**: Medium signal (-50 to -70 dBm)
- 🔴 **Red**: Weak signal (-70 to -90 dBm)

### Features Kept from Your Original System
✅ Raspberry Pi WiFi scanning (unchanged)
✅ OwnTracks GPS tracking (unchanged)
✅ Flask server backend (unchanged)
✅ Auto-linking WiFi with GPS (unchanged)
✅ 4-corner room calibration (unchanged)

### New Features from wifi-heatmapper Inspiration
✨ **Google Maps Heatmap Layer** - smooth gradient visualization
✨ **Weight-based intensity** - stronger signals show brighter
✨ **Multiple map types** - Satellite, Hybrid, Terrain, Roadmap
✨ **Colored circle markers** - click for signal details
✨ **Info windows** - popup with signal strength, SSID, location

## 📱 Step 3: Use the System

### A. Configure OwnTracks (Phone GPS)
1. Install **OwnTracks** on Android
2. **Mode**: HTTP
3. **URL**: `http://10.185.124.107:5000/api/gps`
4. **Device ID**: phone
5. **Update interval**: 1-2 seconds

### B. Start Raspberry Pi Scanner
```bash
python pi_simple_http.py
```

### C. Open the Map
1. Browse to: `http://10.185.124.107:5000`
2. You'll see **Google Maps** with satellite view
3. Switch map types in the top-center dropdown

### D. Calibrate Room (Walk to 4 Corners)
1. Click **"GPS Calibrate (Walk to Corners)"**
2. Walk to **Top-Left** corner → Click "Record Corner 1/4"
3. Walk to **Top-Right** corner → Click "Record Corner 2/4"
4. Walk to **Bottom-Right** corner → Click "Record Corner 3/4"
5. Walk to **Bottom-Left** corner → Click "Record Corner 4/4"
6. Purple polygon appears showing room boundary!

### E. Map WiFi Signals
- Just **walk around** with phone (GPS) + Raspberry Pi (WiFi)
- **Heatmap** appears automatically showing signal strength
- **Green areas** = strong WiFi
- **Red areas** = weak WiFi
- **Click circles** to see exact signal values

## 🎯 Comparison: wifi-heatmapper vs Your System

| Feature | wifi-heatmapper | Your System |
|---------|----------------|-------------|
| **WiFi Scanning** | Manual laptop moving | 🎉 Automatic Raspberry Pi |
| **Positioning** | Manual clicking on floor plan | 🎉 Automatic GPS (phone) |
| **Map Type** | Static floor plan image | 🎉 Live Google Maps |
| **Setup** | Complex Next.js/TypeScript | 🎉 Simple Flask + HTML |
| **Heatmap** | Canvas overlay on image | 🎉 Google Maps Heatmap Layer |
| **Color Scheme** | Green → Red | ✅ Same! Green → Red |
| **Mobile** | Must move laptop | 🎉 Phone GPS + stationary Pi |

### Your Advantages
✅ **Easier**: No need to carry laptop around
✅ **More accurate**: Real GPS coordinates, not clicked estimates
✅ **Real map**: Actual satellite/street view background
✅ **Simpler**: Basic Flask app, not complex Next.js

### Inspired Features from wifi-heatmapper
✅ **Heatmap gradient**: Green (good) → Red (bad) color scheme
✅ **Signal weighting**: Stronger signals more prominent
✅ **Radius adjustment**: Can tune heatmap spread
✅ **Survey points**: Click to see details

## 🚀 Current Status

✅ **Google Maps integrated** with heatmap visualization layer
✅ **Server running** at http://10.185.124.107:5000
✅ **Raspberry Pi active** - sending WiFi signals
✅ **GPS endpoint ready** - waiting for OwnTracks
⏳ **Pending**: Add your Google Maps API key!

## 📝 Files Modified

1. **`templates/index.html`**
   - Added Google Maps API script
   - Removed Leaflet dependencies
   - Updated styling for Google Maps

2. **`static/heatmap_google.js`** (NEW)
   - Google Maps initialization
   - Heatmap layer with gradient
   - GPS calibration markers (colored corners)
   - Room boundary polygon
   - Signal circles with info windows
   - Socket.IO real-time updates

3. **Backend** (NO CHANGES)
   - `heatmap_server.py` - unchanged
   - GPS endpoints - unchanged
   - Raspberry Pi client - unchanged

## 🎨 Map Controls

- **Zoom**: Mouse wheel or +/- buttons
- **Pan**: Click and drag
- **Map Type**: Top-center dropdown
  - 🗺️ Roadmap - street names
  - 🛰️ Satellite - aerial imagery
  - 🌍 Hybrid - satellite + labels
  - ⛰️ Terrain - topographic
- **Fullscreen**: Bottom-right button

## 💡 Tips

1. **Use Satellite view** to see your actual building
2. **Zoom to level 20-22** for room-level detail
3. **Heatmap radius** auto-set to 20 pixels (can adjust in code)
4. **Green = good spots** to place devices
5. **Red = dead zones** where you need extenders
6. **Click colored circles** for exact signal readings

## 🔧 Customization

### Adjust Heatmap Radius
In `heatmap_google.js` line 49:
```javascript
radius: 20, // Change this (10-50 works well)
```

### Change Gradient Colors
In `heatmap_google.js` lines 62-69:
```javascript
const gradient = [
    'rgba(0, 255, 0, 0)',   // Start
    'rgba(255, 255, 0, 1)', // Middle  
    'rgba(255, 0, 0, 1)'    // End
];
```

---

**Next**: Get your Google Maps API key and start mapping! 🗺️📶🎉
