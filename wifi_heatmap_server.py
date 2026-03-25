#!/usr/bin/env python3
"""
WiFi Heatmap Server for Raspberry Pi
Real-time room mapping with T-Mobile 5G signal strength
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
from datetime import datetime
from threading import Lock
import os
import google.generativeai as genai
import socket
import subprocess
import platform
import psutil

# Configure Gemini AI
GOOGLE_GEMINI_API_KEY = os.getenv('GOOGLE_GEMINI_API_KEY')
if not GOOGLE_GEMINI_API_KEY:
    raise ValueError("GOOGLE_GEMINI_API_KEY environment variable not set")
genai.configure(api_key=GOOGLE_GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')  # Correct model for your API
chat_session = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'wifi-heatmap-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global data storage
signal_data = []
calibration_points = []
data_lock = Lock()
scanning_active = False

def get_network_info():
    """Gather comprehensive network information"""
    network_info = {}
    
    try:
        # Get hostname and local IP
        network_info['hostname'] = socket.gethostname()
        network_info['local_ip'] = socket.gethostbyname(socket.gethostname())
        
        # Get all network interfaces
        try:
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()
            
            interfaces = {}
            for interface_name, addrs in net_if_addrs.items():
                interface_info = {}
                for addr in addrs:
                    if addr.family == socket.AF_INET:  # IPv4
                        interface_info['ipv4'] = addr.address
                        interface_info['netmask'] = addr.netmask
                    elif addr.family == socket.AF_INET6:  # IPv6
                        interface_info['ipv6'] = addr.address
                
                # Get interface stats
                if interface_name in net_if_stats:
                    stats = net_if_stats[interface_name]
                    interface_info['is_up'] = stats.isup
                    interface_info['speed'] = f"{stats.speed} Mbps" if stats.speed > 0 else "Unknown"
                
                if interface_info:
                    interfaces[interface_name] = interface_info
            
            network_info['interfaces'] = interfaces
            
            # Get network IO statistics
            net_io = psutil.net_io_counters()
            network_info['bytes_sent'] = f"{net_io.bytes_sent / (1024**2):.2f} MB"
            network_info['bytes_received'] = f"{net_io.bytes_recv / (1024**2):.2f} MB"
            network_info['packets_sent'] = net_io.packets_sent
            network_info['packets_received'] = net_io.packets_recv
            
        except ImportError:
            network_info['note'] = "Install psutil for detailed network info"
        
        # Try to get WiFi info on Windows
        if platform.system() == 'Windows':
            try:
                # Get current WiFi connection info
                result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    output = result.stdout
                    wifi_info = {}
                    
                    for line in output.split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            key = key.strip()
                            value = value.strip()
                            
                            if 'SSID' in key and 'BSSID' not in key:
                                wifi_info['ssid'] = value
                            elif 'Signal' in key:
                                wifi_info['signal_quality'] = value
                            elif 'Radio type' in key:
                                wifi_info['radio_type'] = value
                            elif 'Channel' in key:
                                wifi_info['channel'] = value
                            elif 'Receive rate' in key:
                                wifi_info['receive_rate'] = value
                            elif 'Transmit rate' in key:
                                wifi_info['transmit_rate'] = value
                    
                    if wifi_info:
                        network_info['wifi'] = wifi_info
                        
            except Exception as e:
                network_info['wifi_error'] = str(e)
        
        # Get DNS info
        try:
            result = subprocess.run(['nslookup', 'google.com'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Server:' in line:
                        dns = line.split('Server:')[1].strip()
                        network_info['dns_server'] = dns
                        break
        except:
            pass
            
    except Exception as e:
        network_info['error'] = str(e)
    
    return network_info

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')

@app.route('/api/calibration', methods=['GET', 'POST'])
def calibration():
    """Handle calibration points"""
    global calibration_points
    
    if request.method == 'POST':
        data = request.json
        with data_lock:
            calibration_points = data.get('points', [])
        return jsonify({'status': 'success', 'points': calibration_points})
    
    else:
        with data_lock:
            return jsonify({'points': calibration_points})

@app.route('/api/data')
def get_data():
    """Get all signal data points"""
    with data_lock:
        return jsonify({'data': signal_data})

@app.route('/api/clear')
def clear_data():
    """Clear all signal data"""
    global signal_data
    with data_lock:
        signal_data = []
    return jsonify({'status': 'success'})

@app.route('/api/scan/start')
def start_scan():
    """Start continuous scanning - Not used in client mode"""
    return jsonify({'status': 'client_mode', 'message': 'Data comes from Raspberry Pi client'})

@app.route('/api/client/data', methods=['POST'])
def receive_client_data():
    """Receive signal data from remote Raspberry Pi client"""
    try:
        data = request.json
        
        with data_lock:
            signal_data.append(data)
            # Keep only last 1000 points
            if len(signal_data) > 1000:
                signal_data.pop(0)
        
        # Emit to all connected clients
        socketio.emit('signal_update', data)
        
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/status')
def status():
    """Get current status"""
    with data_lock:
        data_count = len(signal_data)
        calib_count = len(calibration_points)
        latest_signal = signal_data[-1] if signal_data else None
    
    return jsonify({
        'scanning': scanning_active,
        'data_points': data_count,
        'calibration_points': calib_count,
        'latest_signal': latest_signal
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle Magenta AI chat requests with comprehensive network info"""
    global chat_session
    
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Initialize chat session if needed
        if chat_session is None:
            chat_session = model.start_chat(history=[])
        
        # Get comprehensive network information
        network_info = get_network_info()
        
        # Build context from current signal data AND network info
        context = "🌐 COMPREHENSIVE NETWORK STATUS:\n\n"
        
        # Add network information
        context += f"📍 Network Details:\n"
        context += f"   • Hostname: {network_info.get('hostname', 'Unknown')}\n"
        context += f"   • Local IP: {network_info.get('local_ip', 'Unknown')}\n"
        
        if 'dns_server' in network_info:
            context += f"   • DNS Server: {network_info['dns_server']}\n"
        
        # Add WiFi specific info
        if 'wifi' in network_info:
            wifi = network_info['wifi']
            context += f"\n📡 WiFi Connection:\n"
            if 'ssid' in wifi:
                context += f"   • Network (SSID): {wifi['ssid']}\n"
            if 'signal_quality' in wifi:
                context += f"   • Signal Quality: {wifi['signal_quality']}\n"
            if 'radio_type' in wifi:
                context += f"   • Radio Type: {wifi['radio_type']}\n"
            if 'channel' in wifi:
                context += f"   • Channel: {wifi['channel']}\n"
            if 'receive_rate' in wifi:
                context += f"   • Download Speed: {wifi['receive_rate']}\n"
            if 'transmit_rate' in wifi:
                context += f"   • Upload Speed: {wifi['transmit_rate']}\n"
        
        # Add interface information
        if 'interfaces' in network_info:
            context += f"\n🔌 Network Interfaces:\n"
            for iface_name, iface_info in list(network_info['interfaces'].items())[:3]:  # Top 3
                if iface_info.get('is_up'):
                    context += f"   • {iface_name}:\n"
                    if 'ipv4' in iface_info:
                        context += f"      - IPv4: {iface_info['ipv4']}\n"
                    if 'speed' in iface_info:
                        context += f"      - Speed: {iface_info['speed']}\n"
        
        # Add data transfer statistics
        if 'bytes_sent' in network_info:
            context += f"\n📊 Data Transfer Statistics:\n"
            context += f"   • Data Sent: {network_info['bytes_sent']}\n"
            context += f"   • Data Received: {network_info['bytes_received']}\n"
            context += f"   • Packets Sent: {network_info['packets_sent']:,}\n"
            context += f"   • Packets Received: {network_info['packets_received']:,}\n"
        
        # Add signal history data
        with data_lock:
            if signal_data:
                latest = signal_data[-1]
                signal_strength = latest.get('signal', 'unknown')
                ssid = latest.get('ssid', 'unknown')
                data_points = len(signal_data)
                
                # Calculate average
                if len(signal_data) >= 5:
                    recent_signals = [s.get('signal', -100) for s in signal_data[-5:]]
                    avg_signal = sum(recent_signals) / len(recent_signals)
                else:
                    avg_signal = signal_strength
                
                context += f"\n📈 Signal History:\n"
                context += f"   • Current Signal: {signal_strength} dBm\n"
                context += f"   • Average (last 5): {avg_signal:.1f} dBm\n"
                context += f"   • Total Readings: {data_points}\n"
        
        # Create prompt with personality and full network data
        prompt = f"""You are Magenta 🤖, a super friendly WiFi and network expert with ChatGPT's warm personality!

{context}

USER QUESTION: "{user_message}"

Respond naturally and helpfully:
- Answer directly using the detailed network data above
- Reference specific metrics when relevant (IP, signal quality, speeds, etc.)
- Be warm, encouraging, and conversational
- Explain technical terms simply
- Keep responses concise (2-4 sentences)
- Show personality and provide actionable insights!

Be like a knowledgeable tech friend who has access to all the network details!"""
        
        # Get AI response
        response = chat_session.send_message(prompt)
        ai_response = response.text.strip() if response.text else "I'm processing that... 📡"
        
        return jsonify({
            'response': ai_response,
            'network_info': network_info,
            'context': context
        }), 200
        
    except Exception as e:
        print(f"Chat error: {e}")
        # Friendly fallback with basic network info
        try:
            network_info = get_network_info()
            wifi_status = network_info.get('wifi', {}).get('signal_quality', 'Good')
            fallback = f"Hey! I'm having a little hiccup with my AI brain right now. 😅 But I can see your WiFi signal is at {wifi_status}! Everything looks good! Try asking me again?"
        except:
            fallback = "Hey! I'm having a little trouble right now. 😅 But I'm here to help! Try asking me again?"
        
        return jsonify({
            'response': fallback,
            'error': str(e)
        }), 200

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('status', {'scanning': scanning_active})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

if __name__ == '__main__':
    print("=" * 60)
    print("WiFi Heatmap Server Starting")
    print("=" * 60)
    print(f"Access the web interface at: http://<raspberry-pi-ip>:5000")
    print("Make sure to run with sudo for WiFi scanning privileges")
    print("=" * 60)
    
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
