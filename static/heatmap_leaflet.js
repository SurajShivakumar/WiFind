// WiFi Heatmap with Leaflet + Heatmap Layer
// NO API KEY NEEDED! Uses free OpenStreetMap
// Inspired by hnykda/wifi-heatmapper gradient visualization
console.log('🗺️ Loading Leaflet heatmap...');

const socket = io();

// State
let map = null;
let heatLayer = null;
let gpsCalibrationMode = false;
let gpsCorners = [];
let signalPoints = [];
let latestGPS = null;
let markers = [];
let circles = [];
let roomPolygon = null;

// Heatmap data array [lat, lon, intensity]
let heatmapData = [];

// Initialize map
function initMap() {
    console.log('🗺️ Initializing Leaflet map...');
    
    // Check if Leaflet is loaded
    if (typeof L === 'undefined') {
        console.error('❌ Leaflet not loaded! Retrying...');
        setTimeout(initMap, 1000);
        return;
    }
    
    console.log('✅ Leaflet loaded, creating map...');
    
    // Default center (Seattle - will update with GPS)
    map = L.map('mapContainer', {
        center: [47.6062, -122.3321],
        zoom: 20,
        zoomControl: true
    });
    
    // Add OpenStreetMap base layer
    const osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 22,
        maxNativeZoom: 19
    });
    
    // Add satellite imagery (Esri)
    const satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Esri',
        maxZoom: 22,
        maxNativeZoom: 19
    });
    
    // Add hybrid (satellite + labels)
    const hybridLayer = L.layerGroup([
        satelliteLayer,
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            opacity: 0.3,
            maxZoom: 22,
            maxNativeZoom: 19
        })
    ]);
    
    // Start with satellite
    satelliteLayer.addTo(map);
    
    // Layer control
    const baseMaps = {
        "🛰️ Satellite": satelliteLayer,
        "🌍 Hybrid": hybridLayer,
        "🗺️ Street Map": osmLayer
    };
    
    L.control.layers(baseMaps).addTo(map);
    
    // Initialize heatmap layer
    // Gradient: Green (strong) → Yellow → Red (weak) like wifi-heatmapper
    heatLayer = L.heatLayer(heatmapData, {
        radius: 25,
        blur: 15,
        maxZoom: 22,
        max: 1.0,
        gradient: {
            0.0: '#00ff00',  // Green - strong signal
            0.3: '#7fff00',  // Yellow-green
            0.5: '#ffff00',  // Yellow - medium
            0.7: '#ff7f00',  // Orange
            1.0: '#ff0000'   // Red - weak signal
        }
    }).addTo(map);
    
    console.log('✅ Map initialized successfully!');
}

// Signal strength to intensity (inverted: strong = high intensity)
function signalToIntensity(signal) {
    // -30 dBm (best) = 1.0, -90 dBm (worst) = 0.0
    const normalized = Math.max(0, Math.min(1, (-30 - signal) / -60));
    return 1 - normalized; // Invert so strong = prominent
}

// Signal strength to color (for markers)
function signalToColor(signal) {
    if (signal >= -50) return '#00ff00'; // Green
    if (signal >= -60) return '#7fff00'; // Yellow-green
    if (signal >= -70) return '#ffff00'; // Yellow
    if (signal >= -80) return '#ff7f00'; // Orange
    return '#ff0000'; // Red
}

// Add WiFi signal to map
function addSignalToMap(signalData) {
    const lat = signalData.gps_lat || signalData.latitude;
    const lon = signalData.gps_lon || signalData.longitude;
    
    if (!lat || !lon) {
        console.log('⚠️ Signal missing GPS');
        return;
    }
    
    const signal = signalData.signal;
    const color = signalToColor(signal);
    const intensity = signalToIntensity(signal);
    
    // Add to heatmap layer
    heatmapData.push([lat, lon, intensity]);
    heatLayer.setLatLngs(heatmapData);
    
    // Add colored circle marker
    const circle = L.circleMarker([lat, lon], {
        radius: 6,
        fillColor: color,
        color: '#ffffff',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.8
    }).addTo(map);
    
    // Add popup
    circle.bindPopup(`
        <div style="font-family: sans-serif; min-width: 180px;">
            <div style="background: ${color}; color: white; padding: 8px; margin: -10px -10px 10px -10px; font-weight: bold; border-radius: 3px 3px 0 0;">
                📶 ${signal} dBm
            </div>
            <div style="padding: 5px 0;">
                <strong>📡 SSID:</strong> ${signalData.ssid || 'N/A'}<br>
                <strong>📍 GPS:</strong><br>
                ${lat.toFixed(6)}, ${lon.toFixed(6)}<br>
                <strong>💪 Intensity:</strong> ${(intensity * 100).toFixed(0)}%
            </div>
        </div>
    `);
    
    circles.push(circle);
    
    // Center on first signal
    if (circles.length === 1) {
        map.setView([lat, lon], 20);
    }
    
    console.log(`📍 Signal: ${signal} dBm at (${lat.toFixed(6)}, ${lon.toFixed(6)}) - intensity: ${intensity.toFixed(2)}`);
}

// Add calibration corner
function addCalibrationCorner(corner) {
    const cornerLabels = ['🔴 TL', '🔵 TR', '🟢 BR', '🟡 BL'];
    const cornerColors = ['#FF0000', '#0000FF', '#00FF00', '#FFA500'];
    const cornerNames = ['Top-Left', 'Top-Right', 'Bottom-Right', 'Bottom-Left'];
    
    const marker = L.circleMarker([corner.lat, corner.lon], {
        radius: 10,
        fillColor: cornerColors[corner.index],
        color: '#ffffff',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.9
    }).addTo(map);
    
    marker.bindPopup(`
        <div style="font-family: sans-serif;">
            <strong style="color: ${cornerColors[corner.index]};">
                ${cornerLabels[corner.index]} ${cornerNames[corner.index]}
            </strong><br>
            <small>Lat: ${corner.lat.toFixed(6)}<br>
            Lon: ${corner.lon.toFixed(6)}</small>
        </div>
    `);
    
    // Add label
    const label = L.divIcon({
        className: 'corner-label',
        html: `<div style="background: ${cornerColors[corner.index]}; color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">${corner.index + 1}</div>`,
        iconSize: [24, 24]
    });
    
    const labelMarker = L.marker([corner.lat, corner.lon], { icon: label }).addTo(map);
    
    markers.push(marker, labelMarker);
    
    // Draw room boundary if all 4 corners
    if (gpsCorners.length === 4) {
        drawRoomBoundary();
    }
}

// Draw room boundary
function drawRoomBoundary() {
    if (gpsCorners.length !== 4) return;
    
    // Remove old
    if (roomPolygon) {
        map.removeLayer(roomPolygon);
    }
    
    const bounds = gpsCorners.map(c => [c.lat, c.lon]);
    
    roomPolygon = L.polygon(bounds, {
        color: '#9c27b0',
        weight: 3,
        fillColor: '#9c27b0',
        fillOpacity: 0.1,
        dashArray: '10, 5'
    }).addTo(map);
    
    roomPolygon.bindPopup('<strong>📐 Room Boundary</strong><br>GPS Calibrated Area');
    
    // Fit map to bounds
    map.fitBounds(roomPolygon.getBounds(), { padding: [50, 50] });
}

// Update calibration list
function updateCalibrationList() {
    const list = document.getElementById('calibrationList');
    list.innerHTML = '';
    
    const labels = ['Top-Left', 'Top-Right', 'Bottom-Right', 'Bottom-Left'];
    
    gpsCorners.forEach((corner, index) => {
        const li = document.createElement('li');
        li.textContent = `${labels[index]}: GPS (${corner.lat.toFixed(6)}, ${corner.lon.toFixed(6)})`;
        list.appendChild(li);
    });
}

// Update mode indicator
function updateModeIndicator() {
    const indicator = document.getElementById('modeIndicator');
    if (gpsCalibrationMode) {
        indicator.textContent = `GPS CALIBRATION - Walk to Corner ${gpsCorners.length + 1}/4`;
        indicator.className = 'mode-indicator mode-calibration';
    } else {
        indicator.textContent = 'GPS Auto-Positioning Active - FREE Map (No API Key!)';
        indicator.className = 'mode-indicator mode-viewing';
    }
}

// Load data
async function loadData() {
    try {
        const response = await fetch('/api/data');
        const data = await response.json();
        
        signalPoints = data.points || [];
        
        // Load GPS calibration
        const calibResponse = await fetch('/api/calibration');
        const calibData = await calibResponse.json();
        gpsCorners = calibData.gps_corners || [];
        
        // Render corners
        gpsCorners.forEach(corner => addCalibrationCorner(corner));
        
        // Render signals
        signalPoints.forEach(point => {
            if (point.gps_linked && (point.gps_lat || point.latitude) && (point.gps_lon || point.longitude)) {
                addSignalToMap(point);
            }
        });
        
        updateCalibrationList();
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
        document.getElementById('calibStatus').textContent = 
            data.calibration_complete ? '✓ GPS 4/4' : `GPS ${gpsCorners.length}/4`;
        
        if (data.latest_signal) {
            document.getElementById('latestSignal').textContent = `${data.latest_signal.signal} dBm`;
            document.getElementById('ssid').textContent = data.latest_signal.ssid || '--';
        }
    } catch (error) {
        console.error('Error updating status:', error);
    }
}

// Button: GPS Calibrate
document.getElementById('gpsCalibrateBtn').addEventListener('click', async () => {
    if (!gpsCalibrationMode) {
        gpsCalibrationMode = true;
        gpsCorners = [];
        
        markers.forEach(m => map.removeLayer(m));
        markers = [];
        if (roomPolygon) map.removeLayer(roomPolygon);
        
        await fetch('/api/calibration/reset', { method: 'POST' });
        document.getElementById('gpsCalibrateBtn').textContent = 'Record Corner 1/4';
        updateCalibrationList();
    } else {
        try {
            const response = await fetch('/api/calibration', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ use_gps: true })
            });
            const data = await response.json();
            
            if (data.gps_corners && data.gps_corners.length > gpsCorners.length) {
                const newCorner = data.gps_corners[data.gps_corners.length - 1];
                gpsCorners = data.gps_corners;
                addCalibrationCorner(newCorner);
                updateCalibrationList();
            }
            
            if (data.complete) {
                gpsCalibrationMode = false;
                document.getElementById('gpsCalibrateBtn').textContent = 'GPS Calibrate (Walk to Corners)';
                alert('🎉 GPS Calibration Complete! Room boundary set.');
            } else {
                document.getElementById('gpsCalibrateBtn').textContent = `Record Corner ${gpsCorners.length + 1}/4`;
            }
        } catch (error) {
            console.error('Error recording corner:', error);
            alert('❌ Error: Is OwnTracks sending GPS?');
        }
    }
    updateModeIndicator();
});

// Button: Reset
document.getElementById('resetCalBtn').addEventListener('click', async () => {
    if (confirm('Reset GPS calibration?')) {
        gpsCorners = [];
        gpsCalibrationMode = false;
        
        markers.forEach(m => map.removeLayer(m));
        markers = [];
        if (roomPolygon) map.removeLayer(roomPolygon);
        
        await fetch('/api/calibration/reset', { method: 'POST' });
        updateCalibrationList();
        updateModeIndicator();
    }
});

// Button: Clear Data
document.getElementById('clearDataBtn').addEventListener('click', async () => {
    if (confirm('Clear all WiFi data?')) {
        try {
            await fetch('/api/clear');
            
            circles.forEach(c => map.removeLayer(c));
            circles = [];
            heatmapData = [];
            heatLayer.setLatLngs(heatmapData);
            signalPoints = [];
            
            await updateStatus();
        } catch (error) {
            console.error('Error clearing:', error);
        }
    }
});

// Button: Mapping (info)
document.getElementById('mappingBtn').addEventListener('click', () => {
    alert('ℹ️ GPS Auto-Positioning Active!\n\nJust walk around with:\n• Phone (OwnTracks GPS)\n• Raspberry Pi (WiFi scanning)\n\nHeatmap builds automatically!');
});

// Button: Manual Calibration (redirect)
document.getElementById('calibrateBtn').addEventListener('click', () => {
    alert('ℹ️ Use "GPS Calibrate" for map-based calibration!');
});

// Socket: Connect
socket.on('connect', () => {
    console.log('✅ Connected to server');
    loadData();
});

// Socket: Signal Update
socket.on('signal_update', (data) => {
    console.log('📶 Signal update:', data);
    
    signalPoints.push(data);
    
    if (data.gps_linked && (data.gps_lat || data.latitude) && (data.gps_lon || data.longitude)) {
        addSignalToMap(data);
        const lat = data.gps_lat || data.latitude;
        const lon = data.gps_lon || data.longitude;
        console.log(`✅ GPS-positioned: ${data.signal} dBm at (${lat}, ${lon})`);
    } else {
        console.log('⚠️ Signal not GPS-linked');
    }
    
    updateStatus();
    document.getElementById('latestSignal').textContent = `${data.signal} dBm`;
    document.getElementById('ssid').textContent = data.ssid || '--';
});

// Socket: GPS Update
socket.on('gps_update', (gps) => {
    console.log(`📍 GPS: Lat=${gps.latitude}, Lon=${gps.longitude}`);
    latestGPS = gps;
    
    if (markers.length === 0 && circles.length === 0) {
        map.setView([gps.latitude, gps.longitude], 20);
    }
});

// Socket: Data Cleared
socket.on('data_cleared', () => {
    circles.forEach(c => map.removeLayer(c));
    circles = [];
    heatmapData = [];
    heatLayer.setLatLngs(heatmapData);
    signalPoints = [];
    updateStatus();
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('📄 DOM loaded, initializing...');
    
    setTimeout(() => {
        try {
            initMap();
            loadData();
            setInterval(updateStatus, 1000);
            console.log('✅ App initialized!');
        } catch (error) {
            console.error('❌ Init error:', error);
            alert('Map initialization failed: ' + error.message);
        }
    }, 100);
});
