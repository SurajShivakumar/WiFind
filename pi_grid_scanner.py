#!/usr/bin/env python3
"""
9-Grid WiFi Analyzer with Voice Guidance and AI Analysis
Scans WiFi signals across 9 room positions with ElevenLabs voice instructions
and Google Gemini AI recommendations
"""

import subprocess
import re
import json
import time
import http.client
from datetime import datetime
import os
import sys
import google.generativeai as genai
from elevenlabs.client import ElevenLabs
from elevenlabs import play

# Configuration
SERVER_HOST = "10.185.124.107"
SERVER_PORT = 5000

# API Keys - SET THESE!
import os
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')  # Get from elevenlabs.io
GOOGLE_GEMINI_API_KEY = os.getenv('GOOGLE_GEMINI_API_KEY')  # Get from ai.google.dev
if not ELEVENLABS_API_KEY:
    raise ValueError("ELEVENLABS_API_KEY environment variable not set")
if not GOOGLE_GEMINI_API_KEY:
    raise ValueError("GOOGLE_GEMINI_API_KEY environment variable not set")

# ElevenLabs Configuration
ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice (default)
# Other voices: pNInz6obpgDQGcFmaJgB (Adam), EXAVITQu4vr4xnSDxMaL (Bella)

# 9-Grid Positions (3x3 grid)
GRID_POSITIONS = [
    # Scanning order: Bottom to Top, Left to Right (like reading)
    {"id": 1, "name": "Bottom-Left", "row": 2, "col": 0, "speak": "bottom left"},
    {"id": 2, "name": "Bottom-Center", "row": 2, "col": 1, "speak": "bottom center"},
    {"id": 3, "name": "Bottom-Right", "row": 2, "col": 2, "speak": "bottom right"},
    {"id": 4, "name": "Middle-Left", "row": 1, "col": 0, "speak": "middle left"},
    {"id": 5, "name": "Middle-Center", "row": 1, "col": 1, "speak": "center"},
    {"id": 6, "name": "Middle-Right", "row": 1, "col": 2, "speak": "middle right"},
    {"id": 7, "name": "Top-Left", "row": 0, "col": 0, "speak": "top left"},
    {"id": 8, "name": "Top-Center", "row": 0, "col": 1, "speak": "top center"},
    {"id": 9, "name": "Top-Right", "row": 0, "col": 2, "speak": "top right"},
]

# Store all scan data
scan_data = {
    "positions": [],
    "start_time": None,
    "end_time": None,
    "room_name": "Unknown Room"
}

def speak_text(text, save_to_file=None):
    """Use ElevenLabs API to generate and play speech"""
    print(f"🔊 Speaking: {text}")

    if not ELEVENLABS_API_KEY:
        print("⚠️  ElevenLabs API key not set - skipping voice output")
        print(f"📢 WOULD SAY: {text}")
        return False
    
    try:
        # Initialize ElevenLabs client
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        
        # Generate speech
        audio = client.generate(
            text=text,
            voice=ELEVENLABS_VOICE_ID,
            model="eleven_monolingual_v1"
        )
        
        # Save to file if specified
        if save_to_file:
            with open(save_to_file, 'wb') as f:
                for chunk in audio:
                    f.write(chunk)
            print(f"💾 Audio saved to {save_to_file}")
        
        # Play audio directly
        try:
            play(audio)
            return True
        except Exception as play_error:
            print(f"⚠️  Could not play audio directly: {play_error}")
            # Fallback: save and play with system player
            audio_file = save_to_file or "/tmp/speech.mp3"
            audio_generator = client.generate(
                text=text,
                voice=ELEVENLABS_VOICE_ID,
                model="eleven_monolingual_v1"
            )
            with open(audio_file, 'wb') as f:
                for chunk in audio_generator:
                    f.write(chunk)
            
            try:
                subprocess.run(['mpg123', '-q', audio_file], check=True)
                return True
            except FileNotFoundError:
                print("⚠️  No audio player found - install: sudo apt-get install mpg123")
                return False
            
    except Exception as e:
        print(f"❌ Speech error: {e}")
        return False

def get_wifi_networks():
    """Scan all WiFi networks and return signal strengths"""
    try:
        # Scan for all networks
        result = subprocess.run(['sudo', 'iwlist', 'wlan0', 'scan'], 
                              capture_output=True, text=True, timeout=10)
        
        networks = []
        current_network = {}
        
        for line in result.stdout.split('\n'):
            # SSID
            ssid_match = re.search(r'ESSID:"(.+)"', line)
            if ssid_match:
                current_network['ssid'] = ssid_match.group(1)
            
            # Signal strength
            signal_match = re.search(r'Signal level=(-?\d+) dBm', line)
            if signal_match:
                current_network['signal'] = int(signal_match.group(1))
            
            # Quality
            quality_match = re.search(r'Quality=(\d+)/(\d+)', line)
            if quality_match:
                current_network['quality'] = int(quality_match.group(1))
                current_network['quality_max'] = int(quality_match.group(2))
            
            # If we have complete network info, add it
            if 'ssid' in current_network and 'signal' in current_network:
                networks.append(current_network.copy())
                current_network = {}
        
        # Also get connected network info
        result = subprocess.run(['iw', 'wlan0', 'link'], 
                              capture_output=True, text=True)
        
        connected_ssid = None
        connected_signal = None
        
        ssid_match = re.search(r'SSID:\s*(.+)', result.stdout)
        if ssid_match:
            connected_ssid = ssid_match.group(1).strip()
        
        signal_match = re.search(r'signal:\s*(-?\d+)\s*dBm', result.stdout)
        if signal_match:
            connected_signal = int(signal_match.group(1))
        
        return {
            'all_networks': networks,
            'connected_network': connected_ssid,
            'connected_signal': connected_signal,
            'total_networks': len(networks)
        }
        
    except Exception as e:
        print(f"❌ Scan error: {e}")
        return None

def scan_position(position):
    """Scan WiFi at a specific grid position"""
    print(f"\n{'='*60}")
    print(f"📍 Scanning Position {position['id']}/9: {position['name']}")
    print(f"{'='*60}")
    
    # Speak instruction to move to position
    speak_text(f"Please move the Raspberry Pi to the {position['speak']} of the room.")
    
    # Wait for user confirmation
    input(f"Press Enter when Pi is at {position['name']} position...")
    
    print("🔍 Scanning WiFi networks...")
    
    # Scan WiFi
    wifi_data = get_wifi_networks()
    
    if wifi_data:
        position_data = {
            'position_id': position['id'],
            'position_name': position['name'],
            'row': position['row'],
            'col': position['col'],
            'timestamp': datetime.now().isoformat(),
            'wifi_data': wifi_data
        }
        
        scan_data['positions'].append(position_data)
        
        # Display results
        print(f"✅ Found {wifi_data['total_networks']} networks")
        if wifi_data['connected_network']:
            print(f"📶 Connected to: {wifi_data['connected_network']} ({wifi_data['connected_signal']} dBm)")
        
        # Speak confirmation
        speak_text(f"Scan complete at {position['speak']}. Signal strength recorded.")
        
        return True
    else:
        print("❌ Scan failed at this position")
        speak_text(f"Scan failed at {position['speak']}. Please try again.")
        return False

def create_heatmap_visualization():
    """Create ASCII heatmap visualization"""
    print("\n" + "="*60)
    print("📊 HEATMAP VISUALIZATION (Connected Network)")
    print("="*60)
    
    # Create 3x3 grid
    grid = [[None for _ in range(3)] for _ in range(3)]
    
    # Fill grid with signal strengths
    for pos_data in scan_data['positions']:
        row = pos_data['row']
        col = pos_data['col']
        signal = pos_data['wifi_data']['connected_signal']
        grid[row][col] = signal
    
    # Print grid
    print("\n     LEFT    CENTER   RIGHT")
    print("   ┌────────┬────────┬────────┐")
    
    row_labels = ["TOP", "MID", "BOT"]
    for i, row in enumerate(grid):
        print(f"{row_labels[i]}│", end="")
        for signal in row:
            if signal is not None:
                # Color code based on signal strength
                if signal >= -50:
                    color = "🟢"  # Excellent
                elif signal >= -60:
                    color = "🟡"  # Good
                elif signal >= -70:
                    color = "🟠"  # Fair
                else:
                    color = "🔴"  # Poor
                print(f" {color} {signal:3d} │", end="")
            else:
                print(f"   --   │", end="")
        print()
        if i < 2:
            print("   ├────────┼────────┼────────┤")
    
    print("   └────────┴────────┴────────┘")
    print()

def analyze_with_gemini():
    """Send data to Google Gemini for AI analysis"""
    print("\n🤖 Analyzing data with Google Gemini AI...")
    
    if GOOGLE_GEMINI_API_KEY == "your_gemini_api_key_here":
        print("⚠️  Google Gemini API key not set - skipping AI analysis")
        return None
    
    try:
        # Configure Gemini API
        genai.configure(api_key=GOOGLE_GEMINI_API_KEY)
        
        # Initialize the model
        model = genai.GenerativeModel('gemini-pro')
        
        # Prepare data for Gemini
        analysis_prompt = f"""
You are a WiFi network expert analyzing signal strength data from a room scan.

The room was divided into a 3x3 grid with 9 positions:
Top-Left, Top-Center, Top-Right
Middle-Left, Middle-Center, Middle-Right
Bottom-Left, Bottom-Center, Bottom-Right

Here is the complete scan data:
{json.dumps(scan_data, indent=2)}

Please analyze this data and provide:

1. THE SINGLE BEST POSITION for WiFi connectivity (name the exact grid position)
2. TOP 3 BEST POSITIONS ranked with their average signal strengths
3. Which networks perform best in which areas
4. Any patterns in signal distribution (e.g., "signal degrades toward corners", "center has best coverage")
5. Practical recommendations for:
   - Where to place a router in this room
   - Where to position devices for best connectivity
   - Dead zones to avoid

Please provide a clear, actionable summary that can be read aloud to a user.
Format your response in a conversational way suitable for text-to-speech.
"""
        
        # Generate content
        response = model.generate_content(analysis_prompt)
        
        # Extract text from response
        analysis_text = response.text
        
        print("\n" + "="*60)
        print("🤖 GEMINI AI ANALYSIS")
        print("="*60)
        print(analysis_text)
        print("="*60)
        
        return analysis_text
            
    except Exception as e:
        print(f"❌ Gemini analysis error: {e}")
        return None

def send_to_server():
    """Send complete scan data to server"""
    try:
        conn = http.client.HTTPConnection(SERVER_HOST, SERVER_PORT, timeout=5)
        
        headers = {'Content-Type': 'application/json'}
        body = json.dumps({
            'type': 'grid_scan',
            'data': scan_data
        })
        
        conn.request('POST', '/api/grid_scan', body, headers)
        response = conn.getresponse()
        
        if response.status == 200:
            print("✅ Data sent to server")
            return True
        else:
            print(f"⚠️  Server error: {response.status}")
            return False
            
    except Exception as e:
        print(f"⚠️  Could not send to server: {e}")
        return False
    finally:
        conn.close()

def main():
    """Main program"""
    print("\n" + "="*60)
    print("📡 9-GRID WiFi ANALYZER with AI Analysis")
    print("="*60)
    print()
    
    # Initial voice instructions
    intro_text = (
        "Please prepare to scan your room. "
        "You will be guided to 9 different positions in a 3x3 grid pattern. "
        "At each position, place the Raspberry Pi and press Enter to scan the WiFi signal strength."
    )
    
    speak_text(intro_text)
    
    print("🎯 This program will:")
    print("  1. Guide you to 9 room positions")
    print("  2. Scan WiFi signals at each position")
    print("  3. Create a heatmap visualization")
    print("  4. Use Google Gemini AI to analyze the data")
    print("  5. Provide voice recommendations")
    print()
    
    input("Press Enter to begin the scan...")
    
    scan_data['start_time'] = datetime.now().isoformat()
    
    # Scan all 9 positions
    for i, position in enumerate(GRID_POSITIONS, 1):
        success = scan_position(position)
        if not success:
            retry = input("Retry this position? (y/n): ")
            if retry.lower() == 'y':
                scan_position(position)
        
        print(f"\n✅ Completed {i}/9 positions")
        
        if i < len(GRID_POSITIONS):
            time.sleep(1)  # Brief pause between positions
    
    scan_data['end_time'] = datetime.now().isoformat()
    
    # Show heatmap visualization
    create_heatmap_visualization()
    
    # Save data to file
    with open('wifi_scan_data.json', 'w') as f:
        json.dumps(scan_data, f, indent=2)
    print("💾 Data saved to wifi_scan_data.json")
    
    # Send to server
    send_to_server()
    
    # Get AI analysis
    speak_text("Analysis complete. Now consulting artificial intelligence for recommendations.")
    analysis = analyze_with_gemini()
    
    # Read analysis aloud
    if analysis:
        speak_text("Here are the AI recommendations based on your room scan.")
        speak_text(analysis)
    else:
        speak_text("AI analysis is not available. Please check the printed results.")
    
    # Final summary
    print("\n" + "="*60)
    print("✅ SCAN COMPLETE!")
    print("="*60)
    print(f"Total positions scanned: {len(scan_data['positions'])}")
    print(f"Data saved to: wifi_scan_data.json")
    print("="*60)
    
    speak_text("Room scan complete. Thank you for using the WiFi analyzer.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Scan interrupted by user")
        sys.exit(0)
