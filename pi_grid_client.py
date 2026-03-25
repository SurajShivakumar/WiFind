#!/usr/bin/env python3
"""
Raspberry Pi Grid Scanner Client
Scans WiFi and sends to Windows controller
"""

import subprocess
import time
import json
import requests
from datetime import datetime

# Windows laptop server address
CONTROLLER_URL = "http://10.185.124.107:5000"

def get_wifi_networks():
    """Scan WiFi networks on Raspberry Pi"""
    print("📡 Scanning WiFi networks...")
    
    try:
        # Run iwlist scan
        cmd = "sudo iwlist wlan0 scan"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print(f"❌ Scan failed: {result.stderr}")
            return []
        
        # Parse output
        networks = []
        current_network = {}
        
        for line in result.stdout.split('\n'):
            line = line.strip()
            
            if 'Cell' in line and 'Address:' in line:
                if current_network:
                    networks.append(current_network)
                current_network = {}
                # Extract MAC address
                parts = line.split('Address: ')
                if len(parts) > 1:
                    current_network['bssid'] = parts[1].strip()
            
            elif 'ESSID:' in line:
                essid = line.split('ESSID:')[1].strip().strip('"')
                if essid:
                    current_network['ssid'] = essid
            
            elif 'Signal level=' in line:
                # Extract signal level
                parts = line.split('Signal level=')[1].split()[0]
                try:
                    # Convert to dBm
                    signal = int(parts.split('/')[0])
                    # iwlist gives 0-70, convert to dBm
                    dbm = -100 + signal
                    current_network['signal'] = dbm
                except:
                    pass
            
            elif 'Frequency:' in line:
                freq = line.split('Frequency:')[1].split()[0]
                current_network['frequency'] = freq
            
            elif 'Channel:' in line:
                channel = line.split('Channel:')[1].strip().strip(')')
                current_network['channel'] = channel
        
        if current_network:
            networks.append(current_network)
        
        # Filter complete networks
        complete_networks = [n for n in networks if 'ssid' in n and 'signal' in n]
        
        print(f"✅ Found {len(complete_networks)} networks")
        for net in complete_networks:
            print(f"   {net['ssid']}: {net['signal']} dBm")
        
        return complete_networks
        
    except Exception as e:
        print(f"❌ Scan error: {e}")
        return []

def send_scan_to_controller(networks):
    """Send scan data to Windows controller"""
    print("📤 Sending data to controller...")
    
    try:
        data = {
            'networks': networks,
            'timestamp': datetime.now().isoformat(),
            'scanner': 'raspberry_pi'
        }
        
        response = requests.post(
            f"{CONTROLLER_URL}/api/scan_data",
            json=data,
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ Data sent successfully")
            return True
        else:
            print(f"❌ Server returned: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to controller at {CONTROLLER_URL}")
        return False
    except Exception as e:
        print(f"❌ Send error: {e}")
        return False

def main():
    """Main loop - wait for scan commands"""
    print("="*60)
    print("📡 Raspberry Pi Grid Scanner Client")
    print("="*60)
    print(f"Controller: {CONTROLLER_URL}")
    print("Waiting for scan commands from controller...")
    print("="*60)
    
    while True:
        try:
            # Check if controller wants a scan
            response = requests.get(f"{CONTROLLER_URL}/api/check_ready", timeout=2)
            
            if response.status_code == 200:
                status = response.json()
                
                if status.get('ready_to_scan'):
                    print("\n🎯 Scan requested!")
                    
                    # Do the scan
                    networks = get_wifi_networks()
                    
                    if networks:
                        # Send to controller
                        send_scan_to_controller(networks)
                    else:
                        print("⚠️ No networks found")
                    
                    print("\nWaiting for next command...")
            
            time.sleep(1)
            
        except requests.exceptions.ConnectionError:
            print("⚠️ Controller not reachable, retrying...")
            time.sleep(5)
        except KeyboardInterrupt:
            print("\n\n👋 Exiting...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(2)

if __name__ == '__main__':
    main()
