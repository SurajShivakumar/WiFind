#!/usr/bin/env python3
"""
Ultra-Simple WiFi Scanner - Plain HTTP Only
No SSL, no HTTPS, just HTTP
"""

import subprocess
import re
import time
import json
import http.client

SERVER_HOST = "172.20.10.8"
SERVER_PORT = 5000

def get_signal():
    """Get WiFi signal strength"""
    try:
        result = subprocess.run(['iw', 'wlan0', 'link'], capture_output=True, text=True)
        signal_match = re.search(r'signal:\s*(-?\d+)\s*dBm', result.stdout)
        ssid_match = re.search(r'SSID:\s*(.+)', result.stdout)
        
        if signal_match:
            return {
                'signal': int(signal_match.group(1)),
                'ssid': ssid_match.group(1).strip() if ssid_match else 'Unknown',
                'device_id': 'raspberrypi',
                'x': None,
                'y': None
            }
    except Exception as e:
        print(f"Signal error: {e}")
    return None

def send_signal(data):
    """Send signal using plain HTTP - NO SSL"""
    try:
        # Use http.client for plain HTTP only
        conn = http.client.HTTPConnection(SERVER_HOST, SERVER_PORT, timeout=5)
        
        headers = {'Content-Type': 'application/json'}
        body = json.dumps(data)
        
        conn.request('POST', '/api/signal', body, headers)
        response = conn.getresponse()
        
        success = response.status == 200
        conn.close()
        return success
    except Exception as e:
        print(f"Send error: {e}")
        return False

print("=" * 60)
print("WiFi Scanner - Plain HTTP Only")
print(f"Server: {SERVER_HOST}:{SERVER_PORT}")
print("=" * 60)

while True:
    try:
        data = get_signal()
        if data:
            if send_signal(data):
                print(f"✓ {data['signal']} dBm | {data['ssid']}")
            else:
                print(f"✗ Failed to send")
        else:
            print("⚠ No signal")
        time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped")
        break
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(1)
