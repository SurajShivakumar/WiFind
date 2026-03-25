// WiFi Heatmap with GPS Map Integration
console.log('🗺️ Loading heatmap_map.js...');
const socket = io();

// State
let gpsCalibrationMode = false;
let gpsCorners = [];
let signalPoints = [];
let latestGPS = null;
let map = null;
let markers = [];
let heatCircles = [];

// Initialize map centered on default location (will update with first GPS)
function initMap() {
    console.log('🗺️ Initializing Leaflet map...');
    
    // Check if Leaflet is loaded
    if (typeof L === 'undefined') {
        console.error('❌ Leaflet library not loaded!');
        alert('Error: Leaflet map library failed to load. Check internet connection.');
        return;
    }
    
    // Check if map container exists
    const container = document.getElementById('mapContainer');
    if (!container) {
        console.error('❌ Map container element not found!');
        return;
    }
    
    console.log('✅ Leaflet loaded, initializing map...');
    
    // Default center (Seattle area - will update with actual GPS)
    map = L.map('mapContainer').setView([47.6062, -122.3321], 20);
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 22,
        maxNativeZoom: 19
    }).addTo(map);
    
    // Add satellite imagery option
    const satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles &copy; Esri',
        maxZoom: 22,
        maxNativeZoom: 19
    });
    
    // Layer control to switch between street and satellite
    L.control.layers({
        'Street Map': L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 22,
            maxNativeZoom: 19
        }),
        'Satellite': satellite
    }).addTo(map);
    
    console.log('✅ Map initialized successfully!');
}

// Signal strength to color mapping
function signalToColor(signal) {
    if (signal >= -50) return '#ff0000'; // Red - Strong
    if (signal >= -60) return '#ff6600'; // Orange
    if (signal >= -70) return '#ffcc00'; // Yellow
    if (signal >= -80) return '#66ff00'; // Light green
    return '#00ff00'; // Green - Weak
}

// Signal strength to opacity
function signalToOpacity(signal) {
    if (signal >= -50) return 0.8;
    if (signal >= -60) return 0.7;
    if (signal >= -70) return 0.6;
    if (signal >= -80) return 0.5;
    return 0.4;
}

// Signal strength to radius (in meters)
function signalToRadius(signal) {
    if (signal >= -50) return 3; // Strong signal - smaller radius
    if (signal >= -60) return 5;
    if (signal >= -70) return 7;
    if (signal >= -80) return 10;
    return 15; // Weak signal - larger radius
}

// Add WiFi signal point to map
function addSignalToMap(signalData) {
    // Check for GPS coordinates (use gps_lat/gps_lon or latitude/longitude)
    const lat = signalData.gps_lat || signalData.latitude;
    const lon = signalData.gps_lon || signalData.longitude;
    
    if (!lat || !lon) {
        console.log('⚠️ Signal missing GPS coordinates');
        return;
    }
    
    const signal = signalData.signal;
    const color = signalToColor(signal);
    const opacity = signalToOpacity(signal);
    const radius = signalToRadius(signal);
    
    // Add circle overlay for heatmap effect
    const circle = L.circle([lat, lon], {
        color: color,
        fillColor: color,
        fillOpacity: opacity,
        radius: radius,
        weight: 1
    }).addTo(map);
    
    // Add popup with signal info
    circle.bindPopup(`
        <strong>📶 Signal Strength:</strong> ${signal} dBm<br>
        <strong>📡 SSID:</strong> ${signalData.ssid || 'N/A'}<br>
        <strong>📍 Location:</strong> ${lat.toFixed(6)}, ${lon.toFixed(6)}
    `);
    
    heatCircles.push(circle);
    
    // Center map on first signal
    if (heatCircles.length === 1) {
        map.setView([lat, lon], 20);
    }
    
    console.log(`📍 Added signal: ${signal} dBm at (${lat.toFixed(6)}, ${lon.toFixed(6)})`);
}

// Add GPS calibration corner marker
function addCalibrationCorner(corner) {
    const cornerLabels = ['🔴 Top-Left', '🔵 Top-Right', '🟢 Bottom-Right', '🟡 Bottom-Left'];
    const cornerColors = ['red', 'blue', 'green', 'orange'];
    
    const marker = L.circleMarker([corner.lat, corner.lon], {
        radius: 10,
        fillColor: cornerColors[corner.index],
        color: '#fff',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.8
    }).addTo(map);
    
    marker.bindPopup(`
        <strong>${cornerLabels[corner.index]}</strong><br>
        Lat: ${corner.lat.toFixed(6)}<br>
        Lon: ${corner.lon.toFixed(6)}
    `);
    
    markers.push(marker);
    
    // If we have all 4 corners, draw room boundary
    if (gpsCorners.length === 4) {
        drawRoomBoundary();
    }
}

// Draw room boundary polygon
function drawRoomBoundary() {
    if (gpsCorners.length !== 4) return;
    
    // Remove old boundary if exists
    if (window.roomBoundary) {
        map.removeLayer(window.roomBoundary);
    }
    
    const bounds = gpsCorners.map(c => [c.lat, c.lon]);
    
    window.roomBoundary = L.polygon(bounds, {
        color: '#9c27b0',
        weight: 3,
        fillColor: '#9c27b0',
        fillOpacity: 0.1,
        dashArray: '10, 5'
    }).addTo(map);
    
    window.roomBoundary.bindPopup('<strong>📐 Room Boundary</strong><br>GPS Calibrated Area');
    
    // Fit map to room bounds
    map.fitBounds(window.roomBoundary.getBounds(), { padding: [50, 50] });
}

// Update calibration list display
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
        indicator.textContent = 'GPS Auto-Positioning Active - Map View';
        indicator.className = 'mode-indicator mode-viewing';
    }
}

// Load initial data
async function loadData() {
    try {
        const response = await fetch('/api/data');
        const data = await response.json();
        
        signalPoints = data.points || [];
        
        // Load GPS calibration if available
        const calibResponse = await fetch('/api/calibration');
        const calibData = await calibResponse.json();
        gpsCorners = calibData.gps_corners || [];
        
        // Render existing corners
        gpsCorners.forEach(corner => addCalibrationCorner(corner));
        
        // Render existing signals
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

// Update status display
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

// Button handlers
document.getElementById('gpsCalibrateBtn').addEventListener('click', async () => {
    if (!gpsCalibrationMode) {
        // Start GPS calibration
        gpsCalibrationMode = true;
        gpsCorners = [];
        
        // Clear old markers and boundary
        markers.forEach(m => map.removeLayer(m));
        markers = [];
        if (window.roomBoundary) {
            map.removeLayer(window.roomBoundary);
        }
        
        // Reset calibration on server
        await fetch('/api/calibration/reset', { method: 'POST' });
        document.getElementById('gpsCalibrateBtn').textContent = 'Record Corner 1/4';
        updateCalibrationList();
    } else {
        // Record current GPS as calibration corner
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
                alert('🎉 GPS Calibration Complete! Room boundaries set on map.');
            } else {
                document.getElementById('gpsCalibrateBtn').textContent = `Record Corner ${gpsCorners.length + 1}/4`;
            }
        } catch (error) {
            console.error('Error recording GPS corner:', error);
            alert('❌ Error: Make sure OwnTracks is sending GPS data!');
        }
    }
    updateModeIndicator();
});

document.getElementById('resetCalBtn').addEventListener('click', async () => {
    if (confirm('Reset GPS calibration and clear all markers?')) {
        gpsCorners = [];
        gpsCalibrationMode = false;
        
        // Clear map markers
        markers.forEach(m => map.removeLayer(m));
        markers = [];
        
        if (window.roomBoundary) {
            map.removeLayer(window.roomBoundary);
        }
        
        await fetch('/api/calibration/reset', { method: 'POST' });
        updateCalibrationList();
        updateModeIndicator();
    }
});

document.getElementById('clearDataBtn').addEventListener('click', async () => {
    if (confirm('Clear all WiFi signal data from map?')) {
        try {
            await fetch('/api/clear');
            
            // Remove all heat circles
            heatCircles.forEach(circle => map.removeLayer(circle));
            heatCircles = [];
            signalPoints = [];
            
            await updateStatus();
        } catch (error) {
            console.error('Error clearing data:', error);
        }
    }
});

// Mapping button (not needed for GPS mode, but kept for compatibility)
document.getElementById('mappingBtn').addEventListener('click', () => {
    alert('ℹ️ GPS Auto-Positioning is active! No need for manual mapping.\n\nJust walk around with your phone running OwnTracks.');
});

// Calibrate button (manual mode - hidden in GPS mode)
document.getElementById('calibrateBtn').addEventListener('click', () => {
    alert('ℹ️ Use "GPS Calibrate" instead for automatic map-based calibration!');
});

// Socket.IO event handlers
socket.on('connect', () => {
    console.log('✅ Connected to server');
    loadData();
});

socket.on('signal_update', (data) => {
    console.log('📶 Signal update:', data);
    
    signalPoints.push(data);
    
    // If GPS linked, add to map
    if (data.gps_linked && (data.gps_lat || data.latitude) && (data.gps_lon || data.longitude)) {
        addSignalToMap(data);
        const lat = data.gps_lat || data.latitude;
        const lon = data.gps_lon || data.longitude;
        console.log(`✅ GPS-positioned signal: ${data.signal} dBm at (${lat}, ${lon})`);
    } else {
        console.log('⚠️ Signal not GPS-linked');
    }
    
    updateStatus();
    
    // Update latest signal display
    document.getElementById('latestSignal').textContent = `${data.signal} dBm`;
    document.getElementById('ssid').textContent = data.ssid || '--';
});

socket.on('gps_update', (gps) => {
    console.log(`📍 GPS Update: Lat=${gps.latitude}, Lon=${gps.longitude}`);
    latestGPS = gps;
    
    // Update map center on first GPS
    if (!map.hasLayer(markers[0])) {
        map.setView([gps.latitude, gps.longitude], 20);
    }
});

socket.on('data_cleared', () => {
    heatCircles.forEach(circle => map.removeLayer(circle));
    heatCircles = [];
    signalPoints = [];
    updateStatus();
});

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    console.log('📄 DOM loaded, starting initialization...');
    
    // Wait a bit for Leaflet to fully load
    setTimeout(() => {
        try {
            initMap();
            loadData();
            setInterval(updateStatus, 1000);
            console.log('✅ Application initialized successfully!');
        } catch (error) {
            console.error('❌ Initialization error:', error);
            alert('Map initialization failed: ' + error.message);
        }
    }, 100);
});
