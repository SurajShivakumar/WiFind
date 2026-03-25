// WiFi Heatmap Visualization - Client Side
const socket = io();

// Canvas setup
const canvas = document.getElementById('heatmapCanvas');
const ctx = canvas.getContext('2d');

// State
let calibrationMode = false;
let gpsCalibrationMode = false;
let mappingMode = false;
let corners = [];
let gpsCorners = [];
let signalPoints = [];
let pendingSignal = null;

// Resize canvas
function resizeCanvas() {
    const container = canvas.parentElement;
    canvas.width = container.clientWidth - 50;
    canvas.height = 600;
    redraw();
}

window.addEventListener('resize', resizeCanvas);
resizeCanvas();

// Signal strength to color mapping
function signalToColor(signal) {
    // signal: -90 (weak) to -30 (strong)
    const normalized = Math.max(0, Math.min(1, (signal + 90) / 60));
    
    let r, g, b;
    if (normalized < 0.25) {
        // Red to Orange
        const t = normalized / 0.25;
        r = 214 + (225 - 214) * t;
        g = 48 + (112 - 48) * t;
        b = 49 + (85 - 49) * t;
    } else if (normalized < 0.5) {
        // Orange to Yellow
        const t = (normalized - 0.25) / 0.25;
        r = 225 + (253 - 225) * t;
        g = 112 + (203 - 112) * t;
        b = 85 + (110 - 85) * t;
    } else if (normalized < 0.75) {
        // Yellow to Green
        const t = (normalized - 0.5) / 0.25;
        r = 253 - (253 - 0) * t;
        g = 203 - (203 - 184) * t;
        b = 110 - (110 - 148) * t;
    } else {
        // Green to Cyan
        const t = (normalized - 0.75) / 0.25;
        r = 0 + (0 - 0) * t;
        g = 184 + (206 - 184) * t;
        b = 148 + (201 - 148) * t;
    }
    
    return `rgb(${Math.round(r)}, ${Math.round(g)}, ${Math.round(b)})`;
}

// Draw heatmap using radial gradients
function drawHeatmap() {
    if (corners.length !== 4) return;
    
    // Filter points that have positions
    const mappedPoints = signalPoints.filter(p => p.x !== null && p.y !== null);
    
    if (mappedPoints.length === 0) return;
    
    // Draw each point with radial gradient
    mappedPoints.forEach(point => {
        // Calculate radius based on signal strength
        // Stronger signal = larger radius of influence
        const signalStrength = (point.signal + 90) / 60; // Normalize 0-1
        const baseRadius = 100;
        const radius = baseRadius + (signalStrength * 100);
        
        const gradient = ctx.createRadialGradient(
            point.x, point.y, 0,
            point.x, point.y, radius
        );
        
        const color = signalToColor(point.signal);
        gradient.addColorStop(0, color.replace('rgb', 'rgba').replace(')', ', 0.8)'));
        gradient.addColorStop(0.5, color.replace('rgb', 'rgba').replace(')', ', 0.4)'));
        gradient.addColorStop(1, color.replace('rgb', 'rgba').replace(')', ', 0)'));
        
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(point.x, point.y, radius, 0, Math.PI * 2);
        ctx.fill();
    });
    
    // Draw measurement points
    mappedPoints.forEach(point => {
        ctx.fillStyle = signalToColor(point.signal);
        ctx.beginPath();
        ctx.arc(point.x, point.y, 6, 0, Math.PI * 2);
        ctx.fill();
        
        // White border
        ctx.strokeStyle = 'white';
        ctx.lineWidth = 2;
        ctx.stroke();
        
        // Draw signal value
        ctx.fillStyle = 'black';
        ctx.font = 'bold 11px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(`${point.signal}`, point.x, point.y - 12);
    });
}

// Draw calibration corners
function drawCalibration() {
    if (corners.length === 0) return;
    
    // Draw room outline
    if (corners.length > 1) {
        ctx.strokeStyle = '#9c27b0';
        ctx.lineWidth = 3;
        ctx.setLineDash([10, 5]);
        ctx.beginPath();
        ctx.moveTo(corners[0].x, corners[0].y);
        for (let i = 1; i < corners.length; i++) {
            ctx.lineTo(corners[i].x, corners[i].y);
        }
        if (corners.length === 4) {
            ctx.closePath();
        }
        ctx.stroke();
        ctx.setLineDash([]);
    }
    
    // Draw corner markers
    const labels = ['TL', 'TR', 'BR', 'BL'];
    corners.forEach((corner, index) => {
        ctx.fillStyle = '#e91e63';
        ctx.beginPath();
        ctx.arc(corner.x, corner.y, 10, 0, Math.PI * 2);
        ctx.fill();
        
        ctx.fillStyle = 'white';
        ctx.font = 'bold 10px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(labels[index], corner.x, corner.y);
    });
}

// Main draw function
function redraw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Background
    ctx.fillStyle = '#fafafa';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw heatmap first (background layer)
    drawHeatmap();
    
    // Draw calibration on top
    drawCalibration();
}

// Canvas click handler
canvas.addEventListener('click', async (e) => {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    if (calibrationMode) {
        // Calibration mode
        if (corners.length < 4) {
            corners.push({ x, y });
            updateCalibrationList();
            redraw();
            
            if (corners.length === 4) {
                calibrationMode = false;
                document.getElementById('calibrateBtn').textContent = 'Start Calibration';
                updateModeIndicator();
                await saveCalibration();
            }
        }
    } else if (mappingMode) {
        // Mapping mode - mark current position
        try {
            const response = await fetch('/api/mark_position', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ x, y })
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('Position marked:', data);
                await loadData();
                redraw();
            }
        } catch (error) {
            console.error('Error marking position:', error);
        }
    }
});

// Update calibration list
function updateCalibrationList() {
    const list = document.getElementById('calibrationList');
    list.innerHTML = '';
    
    const labels = ['Top-Left', 'Top-Right', 'Bottom-Right', 'Bottom-Left'];
    
    if (gpsCorners.length > 0) {
        // Show GPS calibration corners
        gpsCorners.forEach((corner, index) => {
            const li = document.createElement('li');
            li.textContent = `${corner.label}: GPS (${corner.lat.toFixed(6)}, ${corner.lon.toFixed(6)})`;
            list.appendChild(li);
        });
    } else {
        // Show canvas calibration corners
        corners.forEach((corner, index) => {
            const li = document.createElement('li');
            li.textContent = `${labels[index]}: (${Math.round(corner.x)}, ${Math.round(corner.y)})`;
            list.appendChild(li);
        });
    }
}

// Update mode indicator
function updateModeIndicator() {
    const indicator = document.getElementById('modeIndicator');
    if (gpsCalibrationMode) {
        indicator.textContent = `GPS CALIBRATION - Walk to Corner ${gpsCorners.length + 1}/4`;
        indicator.className = 'mode-indicator mode-calibration';
    } else if (calibrationMode) {
        indicator.textContent = 'CALIBRATION MODE - Click 4 Corners';
        indicator.className = 'mode-indicator mode-calibration';
    } else if (mappingMode) {
        indicator.textContent = 'MAPPING MODE - Click Where You Are';
        indicator.className = 'mode-indicator mode-mapping';
    } else {
        indicator.textContent = 'Viewing Mode - GPS Auto-Positioning Active';
        indicator.className = 'mode-indicator mode-viewing';
    }
}

// Save calibration
async function saveCalibration() {
    try {
        await fetch('/api/calibration', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ corners })
        });
        updateStatus();
    } catch (error) {
        console.error('Error saving calibration:', error);
    }
}

// Load data
async function loadData() {
    try {
        const response = await fetch('/api/data');
        const data = await response.json();
        
        signalPoints = data.points || [];
        corners = data.corners || [];
        
        // Load GPS calibration if available
        const calibResponse = await fetch('/api/calibration');
        const calibData = await calibResponse.json();
        gpsCorners = calibData.gps_corners || [];
        
        updateCalibrationList();
        updateStatus();
        redraw();
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
            data.calibration_complete ? '✓ Complete' : `${corners.length}/4`;
        
        if (data.latest_signal) {
            document.getElementById('latestSignal').textContent = `${data.latest_signal.signal} dBm`;
            document.getElementById('ssid').textContent = data.latest_signal.ssid || '--';
        }
    } catch (error) {
        console.error('Error updating status:', error);
    }
}

// Button handlers
document.getElementById('calibrateBtn').addEventListener('click', () => {
    calibrationMode = !calibrationMode;
    if (calibrationMode) {
        corners = [];
        gpsCalibrationMode = false;
        mappingMode = false;
        updateCalibrationList();
        document.getElementById('calibrateBtn').textContent = 'Cancel Calibration';
        document.getElementById('gpsCalibrateBtn').textContent = 'GPS Calibrate (Walk to Corners)';
        document.getElementById('mappingBtn').textContent = 'Enable Mapping';
    } else {
        document.getElementById('calibrateBtn').textContent = 'Start Calibration';
    }
    updateModeIndicator();
    redraw();
});

document.getElementById('gpsCalibrateBtn').addEventListener('click', async () => {
    if (!gpsCalibrationMode) {
        // Start GPS calibration
        gpsCalibrationMode = true;
        calibrationMode = false;
        mappingMode = false;
        gpsCorners = [];
        // Reset calibration on server
        await fetch('/api/calibration/reset', { method: 'POST' });
        document.getElementById('gpsCalibrateBtn').textContent = 'Record Corner ' + (gpsCorners.length + 1);
        document.getElementById('calibrateBtn').textContent = 'Start Calibration';
    } else {
        // Record current GPS as calibration corner
        try {
            const response = await fetch('/api/calibration', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ use_gps: true })
            });
            const data = await response.json();
            gpsCorners = data.gps_corners || [];
            updateCalibrationList();
            
            if (data.complete) {
                gpsCalibrationMode = false;
                document.getElementById('gpsCalibrateBtn').textContent = 'GPS Calibrate (Walk to Corners)';
                alert('GPS Calibration Complete! Room boundaries set.');
            } else {
                document.getElementById('gpsCalibrateBtn').textContent = 'Record Corner ' + (gpsCorners.length + 1);
            }
        } catch (error) {
            console.error('Error recording GPS corner:', error);
        }
    }
    updateModeIndicator();
    redraw();
});

document.getElementById('resetCalBtn').addEventListener('click', async () => {
    if (confirm('Reset calibration?')) {
        corners = [];
        gpsCorners = [];
        calibrationMode = false;
        gpsCalibrationMode = false;
        updateCalibrationList();
        await fetch('/api/calibration/reset', { method: 'POST' });
        await saveCalibration();
        redraw();
    }
});

document.getElementById('mappingBtn').addEventListener('click', () => {
    mappingMode = !mappingMode;
    if (mappingMode) {
        calibrationMode = false;
        document.getElementById('calibrateBtn').textContent = 'Start Calibration';
        document.getElementById('mappingBtn').textContent = 'Disable Mapping';
    } else {
        document.getElementById('mappingBtn').textContent = 'Enable Mapping';
    }
    updateModeIndicator();
});

document.getElementById('clearDataBtn').addEventListener('click', async () => {
    if (confirm('Clear all data points?')) {
        try {
            await fetch('/api/clear');
            await loadData();
            redraw();
        } catch (error) {
            console.error('Error clearing data:', error);
        }
    }
});

// WebSocket handlers
socket.on('connect', () => {
    console.log('Connected to server');
    loadData();
});

socket.on('signal_update', (data) => {
    console.log('Signal update:', data);
    signalPoints.push(data);
    
    // If GPS linked, automatically positioned
    if (data.gps_linked && data.x !== null && data.y !== null) {
        console.log(`📍 GPS-positioned signal: ${data.signal} dBm at (${data.x}, ${data.y})`);
    }
    
    updateStatus();
    redraw();
    
    // Update latest signal display
    document.getElementById('latestSignal').textContent = `${data.signal} dBm`;
    document.getElementById('ssid').textContent = data.ssid || '--';
});

socket.on('gps_update', (gps) => {
    console.log(`📍 GPS Update: Lat=${gps.latitude}, Lon=${gps.longitude}, Canvas=(${gps.x}, ${gps.y})`);
    // GPS updates are automatically linked with WiFi signals when they arrive
});

socket.on('position_marked', (point) => {
    console.log('Position marked:', point);
    // Update the point in our local array
    const index = signalPoints.findIndex(p => p.timestamp === point.timestamp);
    if (index !== -1) {
        signalPoints[index] = point;
    }
    redraw();
});

socket.on('data_cleared', () => {
    signalPoints = [];
    redraw();
    updateStatus();
});

// Auto-update status
setInterval(updateStatus, 3000);

// Initial load
loadData();
