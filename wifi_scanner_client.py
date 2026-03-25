#!/usr/bin/env python3
"""
WiFi Scanner Client for Raspberry Pi
Scans WiFi signal and sends data to the PC server
"""

import subprocess
import re
import time
import requests
import json
from datetime import datetime
import argparse

class WiFiScannerClient:
    def __init__(self, server_url, interface='wlan0'):
        self.server_url = server_url.rstrip('/')
        self.interface = interface
        self.device_id = self.get_device_id()
        
    def get_device_id(self):
        """Get unique device identifier"""
        try:
            result = subprocess.run(['hostname'], capture_output=True, text=True)
            return result.stdout.strip()
        except:
            return 'raspberrypi'
    
    def get_signal_strength(self):
        """Get current WiFi signal strength in dBm"""
        try:
            result = subprocess.run(
                ['iw', self.interface, 'link'],
                capture_output=True,
                text=True,
                check=True
            )
            
            info = {
                'signal': None,
                'ssid': None,
                'frequency': None,
                'tx_bitrate': None
            }
            
            # Parse SSID
            ssid_match = re.search(r'SSID:\s*(.+)', result.stdout)
            if ssid_match:
                info['ssid'] = ssid_match.group(1).strip()
            
            # Parse signal strength
            signal_match = re.search(r'signal:\s*(-?\d+)\s*dBm', result.stdout)
            if signal_match:
                info['signal'] = int(signal_match.group(1))
            
            # Parse frequency
            freq_match = re.search(r'freq:\s*(\d+)', result.stdout)
            if freq_match:
                info['frequency'] = int(freq_match.group(1))
            
            # Parse bitrate
            bitrate_match = re.search(r'tx bitrate:\s*([\d.]+\s*\w+)', result.stdout)
            if bitrate_match:
                info['tx_bitrate'] = bitrate_match.group(1)
            
            return info
        except Exception as e:
            print(f"Error getting signal strength: {e}")
            return None
    
    def send_data(self, data):
        """Send signal data to the server"""
        try:
            # Ensure HTTP, not HTTPS
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
            print(f"Error sending data to server: {e}")
            return False
    
    def run(self, interval=0.5):
        """Continuously scan and send data"""
        print(f"WiFi Scanner Client Starting")
        print(f"Device ID: {self.device_id}")
        print(f"Server URL: {self.server_url}")
        print(f"Interface: {self.interface}")
        print(f"Scan interval: {interval}s")
        print("=" * 60)
        
        consecutive_failures = 0
        max_failures = 5
        
        while True:
            try:
                info = self.get_signal_strength()
                
                if info and info['signal'] is not None:
                    data = {
                        'device_id': self.device_id,
                        'timestamp': datetime.now().isoformat(),
                        'signal': info['signal'],
                        'ssid': info['ssid'],
                        'frequency': info['frequency'],
                        'bitrate': info['tx_bitrate']
                    }
                    
                    if self.send_data(data):
                        print(f"✓ Sent: {info['signal']} dBm | {info['ssid']}")
                        consecutive_failures = 0
                    else:
                        consecutive_failures += 1
                        print(f"✗ Failed to send data (attempt {consecutive_failures}/{max_failures})")
                else:
                    print("⚠ No WiFi signal detected")
                
                if consecutive_failures >= max_failures:
                    print(f"⚠ Warning: {consecutive_failures} consecutive failures. Check server connection.")
                    consecutive_failures = 0  # Reset to continue trying
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print("\nShutting down WiFi scanner...")
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(interval)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='WiFi Scanner Client for Raspberry Pi')
    parser.add_argument('--server', required=True, help='Server URL (e.g., http://192.168.1.100:5000)')
    parser.add_argument('--interface', default='wlan0', help='WiFi interface name (default: wlan0)')
    parser.add_argument('--interval', type=float, default=0.5, help='Scan interval in seconds (default: 0.5)')
    
    args = parser.parse_args()
    
    client = WiFiScannerClient(args.server, args.interface)
    client.run(args.interval)
