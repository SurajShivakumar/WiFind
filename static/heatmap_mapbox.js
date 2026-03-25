// WiFi Heatmap with Mapbox + Heatmap.js overlay
// Inspired by hnykda/wifi-heatmapper professional approach
// Keeps GPS phone tracking + Raspberry Pi scanning
console.log('🗺️ Loading Mapbox heatmap...');

const socket = io();

// Mapbox token - Get FREE token at https://account.mapbox.com/
// Free tier: 50,000 map loads/month
mapboxgl.accessToken = 'pk.eyJ1IjoiZXhhbXBsZSIsImEiOiJjbGV4YW1wbGUifQ.example'; // Replace with your token

// State
let map = null;
let heatmapInstance = null;
let signalPoints = [];
let latestGPS = null;
let markers = [];

// Heatmap configuration (like wifi-heatmapper)
let heatmapConfig = {
    container: document.getElementById('heatmapOverlay'),
    radius: 40,
    maxOpacity: 0.7,
    minOpacity: 0,
    blur: 0.75,
    // GREEN (strong) → TURQUOISE → BLUE → YELLOW → RED (weak)
    // This matches wifi-heatmapper's color scheme exactly!
    gradient: {
        0.0: '#00ff00',  // Green - Excellent signal
        0.2: '#00ffff',  // Turquoise (Cyan)
        0.4: '#0000ff',  // Blue - Acceptable
        0.6: '#ffff00',  // Yellow - Poor
        0.8: '#ff8800',  // Orange
        1.0: '#ff0000'   // Red - Weak signal
    }
};

// Initialize Mapbox
function initMap() {
    console.log('🗺️ Initializing Mapbox...');
    
    // Check if Mapbox token is set
    if (mapboxgl.accessToken.includes('example')) {
        console.warn('⚠️ Using demo token - get your FREE token at https://account.mapbox.com/');
        // Try to use without token (will fall back to basic view)
        mapboxgl.accessToken = '';
    }
    
    // Create map
    try {
        map = new mapboxgl.Map({
            container: 'mapContainer',
            style: 'mapbox://styles/mapbox/satellite-streets-v12', // Satellite with labels
            center: [-122.3321, 47.6062], // Seattle default
            zoom: 19,
            pitch: 0,
            bearing: 0
        });
        
        // Add navigation controls
        map.addControl(new mapboxgl.NavigationControl(), 'top-right');
        
        // Add style switcher
        const styleControl = document.createElement('div');
        styleControl.className = 'mapboxgl-ctrl mapboxgl-ctrl-group';
        styleControl.style.cssText = 'position: absolute; top: 10px; left: 10px; background: white; border-radius: 4px; box-shadow: 0 0 0 2px rgba(0,0,0,0.1);';
        styleControl.innerHTML = `
            <select id="styleSelector" style="padding: 8px; border: none; font-size: 12px; cursor: pointer; outline: none;">
                <option value="satellite-streets-v12">🛰️ Satellite</option>
                <option value="streets-v12">🗺️ Streets</option>
                <option value="light-v11">☀️ Light</option>
                <option value="dark-v11">🌙 Dark</option>
            </select>
        `;
        map.getContainer().appendChild(styleControl);
        
        document.getElementById('styleSelector').addEventListener('change', (e) => {
            map.setStyle(`mapbox://styles/mapbox/${e.target.value}`);
        });
        
        // Initialize heatmap overlay
        map.on('load', () => {
            initHeatmap();
            console.log('✅ Mapbox initialized!');
        });
        
    } catch (error) {
        console.error('❌ Mapbox error:', error);
        alert('Mapbox failed to load. Get a FREE token at: https://account.mapbox.com/\n\nFree tier: 50,000 map loads/month!');
    }
}

// Initialize Heatmap.js overlay (wifi-heatmapper style)
function initHeatmap() {
    console.log('🎨 Initializing heatmap overlay...');
    
    heatmapInstance = h337.create(heatmapConfig);
    
    console.log('✅ Heatmap overlay ready!');
}

// Signal strength to value (for heatmap intensity)
// wifi-heatmapper uses: Strong = Green, Weak = Red
// We invert: stronger signal = lower value (0.0 = green)
function signalToHeatValue(signal) {
    // -30 dBm (best) → 0.0 (green)
    // -90 dBm (worst) → 1.0 (red)
    const normalized = Math.max(0, Math.min(1, (-30 - signal) / -60));
    return normalized; // No inversion needed with our gradient
}

// Signal strength to color (for markers)
function signalToColor(signal) {
    if (signal >= -50) return '#00ff00'; // Green
    if (signal >= -60) return '#00ffff'; // Turquoise
    if (signal >= -70) return '#0000ff'; // Blue
    if (signal >= -80) return '#ffff00'; // Yellow
    return '#ff0000'; // Red
}

// Convert GPS to screen coordinates
function gpsToScreen(lat, lon) {
    const point = map.project([lon, lat]);
    return { x: Math.round(point.x), y: Math.round(point.y) };
}

// Add WiFi signal to heatmap
function addSignalToMap(signalData) {
    const lat = signalData.gps_lat || signalData.latitude;
    const lon = signalData.gps_lon || signalData.longitude;
    
    if (!lat || !lon) {
        console.log('⚠️ Signal missing GPS - waiting for phone location');
        return;
    }
    
    const signal = signalData.signal;
    const color = signalToColor(signal);
    const value = signalToHeatValue(signal);
    
    // Add marker
    const el = document.createElement('div');
    el.className = 'signal-marker';
    el.style.cssText = `
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background-color: ${color};
        border: 2px solid white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        cursor: pointer;
    `;
    
    const marker = new mapboxgl.Marker({ element: el })
        .setLngLat([lon, lat])
        .setPopup(new mapboxgl.Popup({ offset: 15 })
            .setHTML(`
                <div style="font-family: sans-serif; min-width: 180px;">
                    <div style="background: ${color}; color: white; padding: 8px; margin: -10px -10px 10px -10px; font-weight: bold;">
                        📶 ${signal} dBm
                    </div>
                    <div style="padding: 5px 0; font-size: 12px;">
                        <strong>📡 SSID:</strong> ${signalData.ssid || 'N/A'}<br>
                        <strong>📍 GPS:</strong> ${lat.toFixed(6)}, ${lon.toFixed(6)}<br>
                        <strong>💪 Quality:</strong> ${(value * 100).toFixed(0)}%
                    </div>
                </div>
            `))
        .addTo(map);
    
    markers.push(marker);
    
    // Update heatmap with screen coordinates
    updateHeatmap();
    
    // Center on first signal
    if (markers.length === 1) {
        map.flyTo({ center: [lon, lat], zoom: 20, duration: 2000 });
    }
    
    console.log(`✅ Mapped: ${signal} dBm at (${lat.toFixed(6)}, ${lon.toFixed(6)})`);
}

// Update heatmap overlay with all points
function updateHeatmap() {
    if (!heatmapInstance || !map) return;
    
    const dataPoints = [];
    const maxValue = 100;
    
    signalPoints.forEach(point => {
        const lat = point.gps_lat || point.latitude;
        const lon = point.gps_lon || point.longitude;
        
        if (lat && lon) {
            const screenPos = gpsToScreen(lat, lon);
            const value = signalToHeatValue(point.signal);
            
            dataPoints.push({
                x: screenPos.x,
                y: screenPos.y,
                value: Math.round((1 - value) * maxValue) // Invert for intensity
            });
        }
    });
    
    heatmapInstance.setData({
        max: maxValue,
        data: dataPoints
    });
}

// Load data
async function loadData() {
    try {
        const response = await fetch('/api/data');
        const data = await response.json();
        
        signalPoints = data.points || [];
        
        signalPoints.forEach(point => {
            if (point.gps_linked && (point.gps_lat || point.latitude) && (point.gps_lon || point.longitude)) {
                addSignalToMap(point);
            }
        });
        
        updateStatus();
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

// Update status
async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        document.getElementById('totalPoints').textContent = data.total_points;
        document.getElementById('mappedPoints').textContent = data.positioned_points;
        
        if (data.latest_signal) {
            document.getElementById('latestSignal').textContent = `${data.latest_signal.signal} dBm`;
            document.getElementById('ssid').textContent = data.latest_signal.ssid || '--';
        }
    } catch (error) {
        console.error('Error updating status:', error);
    }
}

// Heatmap controls
document.getElementById('radiusSlider')?.addEventListener('input', (e) => {
    const radius = parseInt(e.target.value);
    document.getElementById('radiusValue').textContent = radius;
    if (heatmapInstance) {
        heatmapInstance.configure({ radius: radius });
        updateHeatmap();
    }
});

document.getElementById('opacitySlider')?.addEventListener('input', (e) => {
    const opacity = parseFloat(e.target.value);
    document.getElementById('opacityValue').textContent = opacity.toFixed(1);
    if (heatmapInstance) {
        heatmapInstance.configure({ maxOpacity: opacity });
        updateHeatmap();
    }
});

// Redraw heatmap when map moves/zooms
if (map) {
    map.on('move', updateHeatmap);
    map.on('zoom', updateHeatmap);
}

// Clear data button
document.getElementById('clearDataBtn')?.addEventListener('click', async () => {
    if (confirm('Clear all WiFi data?')) {
        try {
            await fetch('/api/clear', { method: 'POST' });
            
            markers.forEach(m => m.remove());
            markers = [];
            signalPoints = [];
            updateHeatmap();
            
            await updateStatus();
            console.log('✅ Data cleared');
        } catch (error) {
            console.error('Error:', error);
        }
    }
});

// Socket: Signal update
socket.on('signal_update', (data) => {
    console.log('📶 Signal:', data);
    
    signalPoints.push(data);
    
    if (data.gps_linked && (data.gps_lat || data.latitude) && (data.gps_lon || data.longitude)) {
        addSignalToMap(data);
        console.log(`✅ GPS-positioned: ${data.signal} dBm`);
    }
    
    updateStatus();
    document.getElementById('latestSignal').textContent = `${data.signal} dBm`;
    document.getElementById('ssid').textContent = data.ssid || '--';
});

// Socket: GPS update
socket.on('gps_update', (gps) => {
    console.log(`📍 GPS: ${gps.latitude}, ${gps.longitude} (accuracy: ${gps.acc}m)`);
    latestGPS = gps;
    
    // Center map on first GPS location
    if (markers.length === 0 && map) {
        map.flyTo({ center: [gps.longitude, gps.latitude], zoom: 20, duration: 2000 });
        console.log('🗺️ Map centered on your location');
    }
});

// Socket: Data cleared
socket.on('data_cleared', () => {
    markers.forEach(m => m.remove());
    markers = [];
    signalPoints = [];
    updateHeatmap();
    updateStatus();
});

// Initialize
socket.on('connect', () => {
    console.log('✅ Connected');
    loadData();
});

document.addEventListener('DOMContentLoaded', () => {
    console.log('📄 Initializing Mapbox heatmap...');
    setTimeout(() => {
        initMap();
        setInterval(updateStatus, 1000);
    }, 100);
});
