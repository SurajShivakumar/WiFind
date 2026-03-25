#!/usr/bin/env python3
import subprocess
import re
import time
import urllib.request
import urllib.error
import json
import sys
import ssl

SERVER_URL = "http://10.185.124.107:5000"

def get_signal():
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
    except:
        pass
    return None

def send_signal(data):
    try:
        # Ensure we're using HTTP, not HTTPS
        url = f"{SERVER_URL}/api/signal"
        if url.startswith('https://'):
            url = url.replace('https://', 'http://')
            
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        # Don't use SSL context for plain HTTP
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status == 200
    except Exception as e:
        print(f"Send error: {e}")
        return False

print(f"WiFi Scanner - Sending to {SERVER_URL}")
print("=" * 50)

while True:
    try:
        data = get_signal()
        if data:
            if send_signal(data):
                print(f"✓ {data['signal']} dBm | {data['ssid']}")
            else:
                print("✗ Send failed")
        time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped")
        break
