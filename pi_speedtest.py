#!/usr/bin/env python3
"""
Raspberry Pi Speed Test Runner
Runs speedtest-cli on the Pi and sends results to server
"""

import subprocess
import json
import time
import http.client
from datetime import datetime

# Server configuration
SERVER_HOST = "10.185.124.107"
SERVER_PORT = 5000

def run_speedtest():
    """Run speedtest-cli and return results"""
    print("🚀 Starting speed test on Raspberry Pi...")
    
    try:
        # Run speedtest-cli with JSON output
        result = subprocess.run(
            ['speedtest-cli', '--json'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            print(f"❌ Speed test failed: {result.stderr}")
            return None
        
        # Parse JSON output
        data = json.loads(result.stdout)
        
        # Extract relevant data (convert to Mbps)
        speed_data = {
            'download': round(data['download'] / 1_000_000, 2),  # bits to Mbps
            'upload': round(data['upload'] / 1_000_000, 2),      # bits to Mbps
            'ping': round(data['ping'], 2),
            'server': data['server']['sponsor'],
            'server_location': f"{data['server']['name']}, {data['server']['country']}",
            'ip': data['client']['ip'],
            'isp': data['client']['isp'],
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"✅ Download: {speed_data['download']} Mbps")
        print(f"✅ Upload: {speed_data['upload']} Mbps")
        print(f"✅ Ping: {speed_data['ping']} ms")
        print(f"✅ Server: {speed_data['server']}")
        
        return speed_data
        
    except subprocess.TimeoutExpired:
        print("❌ Speed test timed out")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse speed test results: {e}")
        return None
    except Exception as e:
        print(f"❌ Error running speed test: {e}")
        return None

def send_to_server(speed_data):
    """Send speed test results to server"""
    try:
        conn = http.client.HTTPConnection(SERVER_HOST, SERVER_PORT, timeout=5)
        
        headers = {'Content-Type': 'application/json'}
        body = json.dumps(speed_data)
        
        conn.request('POST', '/api/speedtest', body, headers)
        response = conn.getresponse()
        
        if response.status == 200:
            print(f"✅ Results sent to server: {response.status}")
            return True
        else:
            print(f"❌ Server error: {response.status}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to send to server: {e}")
        return False
    finally:
        conn.close()

def main():
    print("=" * 50)
    print("🔬 Raspberry Pi Speed Test")
    print("=" * 50)
    
    # Check if speedtest-cli is installed
    try:
        subprocess.run(['speedtest-cli', '--version'], 
                      capture_output=True, 
                      check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ speedtest-cli not installed!")
        print("📦 Install with: sudo apt-get install speedtest-cli")
        print("   OR: sudo pip3 install speedtest-cli")
        return
    
    # Run speed test
    speed_data = run_speedtest()
    
    if speed_data:
        # Send to server
        send_to_server(speed_data)
        print("\n✅ Speed test complete!")
    else:
        print("\n❌ Speed test failed!")

if __name__ == "__main__":
    main()
