#!/usr/bin/env python3
"""
WiFi Scanner Client - Runs on Raspberry Pi
Sends signal data to the PC server
"""

import subprocess
import re
import time
import requests
import argparse
from datetime import datetime

class WiFiClient:
    def __init__(self, server_url, interface='wlan0'):
        self.server_url = server_url.rstrip('/')
        self.interface = interface
        
    def get_signal_data(self):
        """Get WiFi signal strength"""
        try:
            result = subprocess.run(
                ['iw', self.interface, 'link'],
                capture_output=True,
                text=True,
                check=True
            )
            
            signal_match = re.search(r'signal:\s*(-?\d+)\s*dBm', result.stdout)
            ssid_match = re.search(r'SSID:\s*(.+)', result.stdout)
            
            if signal_match:
                return {
                    'signal': int(signal_match.group(1)),
                    'ssid': ssid_match.group(1).strip() if ssid_match else 'Unknown',
                    'device_id': 'raspberrypi',
                    'timestamp': datetime.now().isoformat(),
                    'x': None,
                    'y': None
                }
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def send_signal(self, data):
        """Send signal to server"""
        try:
            # Force HTTP (not HTTPS) - ensure no SSL
            url = f"{self.server_url}/api/signal"
            if url.startswith('https://'):
                url = url.replace('https://', 'http://')
            
            response = requests.post(
                url,
                json=data,
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Send error: {e}")
            return False
    
    def run(self, interval=1.0):
        """Main loop"""
        print("=" * 60)
        print("WiFi Scanner Client")
        print(f"Server: {self.server_url}")
        print(f"Interface: {self.interface}")
        print("=" * 60)
        
        failures = 0
        while True:
            try:
                data = self.get_signal_data()
                if data:
                    if self.send_signal(data):
                        print(f"✓ {data['signal']} dBm | {data['ssid']}")
                        failures = 0
                    else:
                        failures += 1
                        print(f"✗ Send failed ({failures})")
                else:
                    print("⚠ No signal")
                
                time.sleep(interval)
            except KeyboardInterrupt:
                print("\nStopping...")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(interval)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='WiFi Scanner Client')
    parser.add_argument('--server', required=True, help='Server URL (e.g., http://192.168.1.100:5000)')
    parser.add_argument('--interface', default='wlan0', help='WiFi interface (default: wlan0)')
    parser.add_argument('--interval', type=float, default=1.0, help='Scan interval in seconds (default: 1.0)')
    
    args = parser.parse_args()
    client = WiFiClient(args.server, args.interface)
    client.run(args.interval)
