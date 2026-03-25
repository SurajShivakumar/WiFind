// WiFi Heatmap with Google Maps Integration
// Inspired by hnykda/wifi-heatmapper with GPS phone tracking + Raspberry Pi
console.log('🗺️ Loading Google Maps heatmap...');

const socket = io();

// State
let map = null;
let heatmapLayer = null;
let gpsCalibrationMode = false;
let gpsCorners = [];
let signalPoints = [];
let latestGPS = null;
let markers = [];
let circles = [];
let roomPolygon = null;

// Heatmap data for Google Maps
let heatmapData = [];

// Wait for Google Maps API to load
function initMap() {
    console.log('🗺️ Initializing Google Maps...');
    
    // Check if Google Maps is loaded
    if (typeof google === 'undefined' || typeof google.maps === 'undefined') {
        console.error('❌ Google Maps API not loaded! Retrying in 1 second...');
        setTimeout(initMap, 1000);
        return;
    }
    
    console.log('✅ Google Maps loaded, creating map...');
    
    // Default center (Seattle - will update with actual GPS)
    const defaultCenter = { lat: 47.6062, lng: -122.3321 };
    
    // Create map with satellite view
    map = new google.maps.Map(document.getElementById('mapContainer'), {
        center: defaultCenter,
        zoom: 20,
        mapTypeId: 'satellite', // Start with satellite view
        mapTypeControl: true,
        mapTypeControlOptions: {
            style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
            position: google.maps.ControlPosition.TOP_CENTER,
            mapTypeIds: ['roadmap', 'satellite', 'hybrid', 'terrain']
        },
        zoomControl: true,
        streetViewControl: false,
        fullscreenControl: true
    });
    
    // Initialize heatmap layer (Google Maps Visualization Library)
    heatmapLayer = new google.maps.visualization.HeatmapLayer({
        data: heatmapData,
        map: map,
        radius: 20, // Radius in pixels
        opacity: 0.7
    });
    
    // Color gradient: Green (strong) → Yellow → Red (weak)
    // This matches the wifi-heatmapper approach
    const gradient = [
        'rgba(0, 255, 0, 0)',      // Transparent at 0%
        'rgba(0, 255, 0, 1)',      // Green at 10% (strong signal -30 to -50 dBm)
        'rgba(127, 255, 0, 1)',    // Yellow-green at 30%
        'rgba(255, 255, 0, 1)',    // Yellow at 50% (medium -50 to -70 dBm)
        'rgba(255, 127, 0, 1)',    // Orange at 70%
        'rgba(255, 0, 0, 1)'       // Red at 100% (weak -70 to -90 dBm)
    ];
    
    heatmapLayer.set('gradient', gradient);
    
    console.log('✅ Google Maps initialized successfully!');
}

// Signal strength to weight (for heatmap intensity)
// Stronger signals get higher weight (more prominent on heatmap)
function signalToWeight(signal) {
    // Signal range: -30 (best) to -90 (worst)
    // Normalize to 0-1, then invert so strong signals are prominent
    const normalized = Math.max(0, Math.min(1, (-30 - signal) / -60));
    return 1 - normalized; // Invert: strong signal = high weight
}

// Signal strength to color (for individual markers)
function signalToColor(signal) {
    if (signal >= -50) return '#00ff00'; // Green - Excellent
    if (signal >= -60) return '#7fff00'; // Yellow-green - Good
    if (signal >= -70) return '#ffff00'; // Yellow - Fair
    if (signal >= -80) return '#ff7f00'; // Orange - Poor
    return '#ff0000'; // Red - Weak
}

// Add WiFi signal point to map
function addSignalToMap(signalData) {
    const lat = signalData.gps_lat || signalData.latitude;
    const lon = signalData.gps_lon || signalData.longitude;
    
    if (!lat || !lon) {
        console.log('⚠️ Signal missing GPS coordinates');
        return;
    }
    
    const signal = signalData.signal;
    const color = signalToColor(signal);
    const weight = signalToWeight(signal);
    
    // Add to heatmap data
    const location = new google.maps.LatLng(lat, lon);
    const weightedLocation = {
        location: location,
        weight: weight
    };
    heatmapData.push(weightedLocation);
    heatmapLayer.setData(heatmapData);
    
    // Add colored circle marker
    const circle = new google.maps.Circle({
        center: { lat: lat, lng: lon },
        radius: 2, // 2 meters
        fillColor: color,
        fillOpacity: 0.7,
        strokeColor: '#ffffff',
        strokeWeight: 1,
        map: map
    });
    
    // Add info window
    const infoWindow = new google.maps.InfoWindow({
        content: `
            <div style="padding: 8px;">
                <strong style="color: ${color};">📶 ${signal} dBm</strong><br>
                <strong>📡 SSID:</strong> ${signalData.ssid || 'N/A'}<br>
                <strong>📍 Location:</strong><br>
                ${lat.toFixed(6)}, ${lon.toFixed(6)}
            </div>
        `
    });
    
    circle.addListener('click', () => {
        infoWindow.setPosition({ lat: lat, lng: lon });
        infoWindow.open(map);
    });
    
    circles.push(circle);
    
    // Center map on first signal
    if (circles.length === 1) {
        map.setCenter({ lat: lat, lng: lon });
        map.setZoom(20);
    }
    
    console.log(`📍 Added signal: ${signal} dBm at (${lat.toFixed(6)}, ${lon.toFixed(6)}) - weight: ${weight.toFixed(2)}`);
}

// Add GPS calibration corner marker
function addCalibrationCorner(corner) {
    const cornerLabels = ['🔴 Top-Left', '🔵 Top-Right', '🟢 Bottom-Right', '🟡 Bottom-Left'];
    const cornerColors = ['#FF0000', '#0000FF', '#00FF00', '#FFA500'];
    
    const marker = new google.maps.Marker({
        position: { lat: corner.lat, lng: corner.lon },
        map: map,
        label: {
            text: (corner.index + 1).toString(),
            color: 'white',
            fontWeight: 'bold'
        },
        icon: {
            path: google.maps.SymbolPath.CIRCLE,
            scale: 12,
            fillColor: cornerColors[corner.index],
            fillOpacity: 0.9,
            strokeColor: '#ffffff',
            strokeWeight: 2
        },
        title: cornerLabels[corner.index]
    });
    
    const infoWindow = new google.maps.InfoWindow({
        content: `
            <div style="padding: 8px;">
                <strong>${cornerLabels[corner.index]}</strong><br>
                Lat: ${corner.lat.toFixed(6)}<br>
                Lon: ${corner.lon.toFixed(6)}
            </div>
        `
    });
    
    marker.addListener('click', () => {
        infoWindow.open(map, marker);
    });
    
    markers.push(marker);
    
    // If we have all 4 corners, draw room boundary
    if (gpsCorners.length === 4) {
        drawRoomBoundary();
    }
}

// Draw room boundary polygon
function drawRoomBoundary() {
    if (gpsCorners.length !== 4) return;
    
    // Remove old boundary
    if (roomPolygon) {
        roomPolygon.setMap(null);
    }
    
    const bounds = gpsCorners.map(c => ({ lat: c.lat, lng: c.lon }));
    
    roomPolygon = new google.maps.Polygon({
        paths: bounds,
        strokeColor: '#9c27b0',
        strokeOpacity: 0.8,
        strokeWeight: 3,
        fillColor: '#9c27b0',
        fillOpacity: 0.15,
        map: map
    });
    
    const infoWindow = new google.maps.InfoWindow({
        content: '<div style="padding: 8px;"><strong>📐 Room Boundary</strong><br>GPS Calibrated Area</div>'
    });
    
    google.maps.event.addListener(roomPolygon, 'click', (event) => {
        infoWindow.setPosition(event.latLng);
        infoWindow.open(map);
    });
    
    // Fit map to room bounds
    const googleBounds = new google.maps.LatLngBounds();
    gpsCorners.forEach(c => googleBounds.extend({ lat: c.lat, lng: c.lon }));
    map.fitBounds(googleBounds, 50);
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
        indicator.textContent = 'GPS Auto-Positioning Active - Google Maps View';
        indicator.className = 'mode-indicator mode-viewing';
    }
}

// Load initial data
async function loadData() {
    try {
        const response = await fetch('/api/data');
        const data = await response.json();
        
        signalPoints = data.points || [];
        
        // Load GPS calibration
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

// Button: GPS Calibration
document.getElementById('gpsCalibrateBtn').addEventListener('click', async () => {
    if (!gpsCalibrationMode) {
        // Start GPS calibration
        gpsCalibrationMode = true;
        gpsCorners = [];
        
        // Clear old markers and boundary
        markers.forEach(m => m.setMap(null));
        markers = [];
        if (roomPolygon) {
            roomPolygon.setMap(null);
        }
        
        await fetch('/api/calibration/reset', { method: 'POST' });
        document.getElementById('gpsCalibrateBtn').textContent = 'Record Corner 1/4';
        updateCalibrationList();
    } else {
        // Record current GPS as corner
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
                alert('🎉 GPS Calibration Complete! Room boundaries set on Google Maps.');
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

// Button: Reset Calibration
document.getElementById('resetCalBtn').addEventListener('click', async () => {
    if (confirm('Reset GPS calibration and clear all markers?')) {
        gpsCorners = [];
        gpsCalibrationMode = false;
        
        markers.forEach(m => m.setMap(null));
        markers = [];
        
        if (roomPolygon) {
            roomPolygon.setMap(null);
        }
        
        await fetch('/api/calibration/reset', { method: 'POST' });
        updateCalibrationList();
        updateModeIndicator();
    }
});

// Button: Clear Data
document.getElementById('clearDataBtn').addEventListener('click', async () => {
    if (confirm('Clear all WiFi signal data from map?')) {
        try {
            await fetch('/api/clear');
            
            // Remove all circles and clear heatmap
            circles.forEach(circle => circle.setMap(null));
            circles = [];
            heatmapData = [];
            heatmapLayer.setData(heatmapData);
            signalPoints = [];
            
            await updateStatus();
        } catch (error) {
            console.error('Error clearing data:', error);
        }
    }
});

// Button: Mapping (informational)
document.getElementById('mappingBtn').addEventListener('click', () => {
    alert('ℹ️ GPS Auto-Positioning is active!\n\nJust walk around with:\n• Phone running OwnTracks (GPS)\n• Raspberry Pi (WiFi scanning)\n\nThe heatmap builds automatically!');
});

// Button: Manual Calibration (redirect to GPS)
document.getElementById('calibrateBtn').addEventListener('click', () => {
    alert('ℹ️ Use "GPS Calibrate" instead for automatic map-based calibration!');
});

// Socket.IO: Connect
socket.on('connect', () => {
    console.log('✅ Connected to server');
    loadData();
});

// Socket.IO: Signal Update
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

// Socket.IO: GPS Update
socket.on('gps_update', (gps) => {
    console.log(`📍 GPS Update: Lat=${gps.latitude}, Lon=${gps.longitude}`);
    latestGPS = gps;
    
    // Center map on first GPS
    if (markers.length === 0 && circles.length === 0) {
        map.setCenter({ lat: gps.latitude, lng: gps.longitude });
        map.setZoom(20);
    }
});

// Socket.IO: Data Cleared
socket.on('data_cleared', () => {
    circles.forEach(circle => circle.setMap(null));
    circles = [];
    heatmapData = [];
    heatmapLayer.setData(heatmapData);
    signalPoints = [];
    updateStatus();
});

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('📄 DOM loaded, waiting for Google Maps API...');
    
    // Wait for Google Maps to load
    const checkGoogle = setInterval(() => {
        if (typeof google !== 'undefined' && typeof google.maps !== 'undefined') {
            clearInterval(checkGoogle);
            initMap();
            loadData();
            setInterval(updateStatus, 1000);
            console.log('✅ Application initialized!');
        }
    }, 100);
});
