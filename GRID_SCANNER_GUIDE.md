# 🎯 9-Grid WiFi Analyzer Setup Guide

## 🌟 What This Does

This is a **voice-guided WiFi scanning system** that:
1. 🗣️ **Speaks instructions** using ElevenLabs AI voice
2. 📍 **Guides you** to 9 positions in a 3x3 grid
3. 📡 **Scans WiFi** signals at each position
4. 🎨 **Creates heatmap** visualization
5. 🤖 **AI Analysis** using Google Gemini
6. 📢 **Reads results** aloud with recommendations

## 🚀 Quick Start

### Step 1: Get API Keys (FREE!)

#### ElevenLabs API Key (for voice):
1. Go to: https://elevenlabs.io/
2. Sign up (FREE - 10,000 characters/month)
3. Go to Profile → API Keys
4. Copy your API key
5. Edit `pi_grid_scanner.py` line 18:
   ```python
   ELEVENLABS_API_KEY = "your_key_here"
   ```

#### Google Gemini API Key (for AI analysis):
1. Go to: https://ai.google.dev/
2. Click "Get API Key"
3. Create new key (FREE!)
4. Copy your API key
5. Edit `pi_grid_scanner.py` line 19:
   ```python
   GOOGLE_GEMINI_API_KEY = "your_key_here"
   ```

### Step 2: Install Dependencies on Pi

SSH into your Raspberry Pi and run:

```bash
# Install audio player
sudo apt-get update
sudo apt-get install mpg123 -y

# Install WiFi tools (if not already)
sudo apt-get install wireless-tools iw -y

# Install Python packages
pip3 install requests
```

### Step 3: Copy File to Pi

Use WinSCP to copy `pi_grid_scanner.py` to your Raspberry Pi.

### Step 4: Make Executable

```bash
chmod +x pi_grid_scanner.py
```

### Step 5: Run It!

```bash
python3 pi_grid_scanner.py
```

## 🎮 How to Use

### The Process:

1. **Start the program** - Voice says: "Please prepare to scan your room..."

2. **9 Positions** - You'll be guided to each position:
   ```
   Bottom-Left → Bottom-Center → Bottom-Right
   Middle-Left → Middle-Center → Middle-Right
   Top-Left    → Top-Center    → Top-Right
   ```

3. **At each position:**
   - 🔊 Voice: "Please move the Raspberry Pi to the bottom left of the room"
   - 🚶 You: Move Pi to that position
   - ⌨️ You: Press Enter
   - 📡 Pi: Scans all WiFi networks
   - 🔊 Voice: "Scan complete at bottom left. Signal strength recorded."

4. **After all 9 scans:**
   - 📊 See ASCII heatmap visualization
   - 🤖 AI analyzes the data
   - 🔊 Voice reads recommendations:
     - "The best position for WiFi is..."
     - "Top 3 positions are..."
     - "Signal patterns show..."
     - "Recommendations..."

5. **Results saved:**
   - `wifi_scan_data.json` - Complete data
   - Sent to your server automatically
   - Displayed on webpage

## 📊 Example Output

### Heatmap:
```
     LEFT    CENTER   RIGHT
   ┌────────┬────────┬────────┐
TOP│ 🟢 -45 │ 🟢 -42 │ 🟡 -58 │
   ├────────┼────────┼────────┤
MID│ 🟡 -55 │ 🟢 -40 │ 🟡 -60 │
   ├────────┼────────┼────────┤
BOT│ 🟠 -68 │ 🟡 -62 │ 🔴 -75 │
   └────────┴────────┴────────┘
```

### AI Analysis (spoken aloud):
> "Based on the analysis, the best position for WiFi connectivity is **Top-Center** with an average signal strength of -42 dBm. 
> 
> The top 3 best positions are:
> 1. Top-Center: -42 dBm (Excellent)
> 2. Top-Left: -45 dBm (Excellent)
> 3. Middle-Center: -40 dBm (Excellent)
>
> Signal patterns show that coverage is strongest in the upper half of the room and center positions. Signal degrades significantly in the bottom corners.
>
> Recommendations:
> - Place your router near the top-center or middle-center of the room
> - Avoid placing devices in bottom corners
> - For desk setup, choose top or middle positions for best connectivity"

## 🎨 Grid Layout

Your room is divided like this:

```
┌─────────────┬─────────────┬─────────────┐
│  Top-Left   │ Top-Center  │  Top-Right  │
│   (Pos 7)   │   (Pos 8)   │   (Pos 9)   │
├─────────────┼─────────────┼─────────────┤
│ Middle-Left │Middle-Center│Middle-Right │
│   (Pos 4)   │   (Pos 5)   │   (Pos 6)   │
├─────────────┼─────────────┼─────────────┤
│ Bottom-Left │Bottom-Center│Bottom-Right │
│   (Pos 1)   │   (Pos 2)   │   (Pos 3)   │
└─────────────┴─────────────┴─────────────┘
```

Scanning order: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9

## ⚙️ Configuration Options

### Change Voice (line 21):
```python
# Default (Rachel - female, American)
ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"

# Other options:
# Adam (male, American): "pNInz6obpgDQGcFmaJgB"
# Bella (female, American): "EXAVITQu4vr4xnSDxMaL"
```

### Customize Grid Order (line 24-34):
Change the order positions are scanned by reordering the list.

## 🔧 Troubleshooting

### "No audio player found"
```bash
sudo apt-get install mpg123
# Or install ffmpeg:
sudo apt-get install ffmpeg
```

### "Permission denied" for iwlist
```bash
# Run with sudo:
sudo python3 pi_grid_scanner.py
```

### Voice says "API key not set"
- You forgot to add your ElevenLabs API key
- Edit line 18 in `pi_grid_scanner.py`

### AI analysis not working
- Check Google Gemini API key (line 19)
- Make sure you activated the Gemini API in Google Cloud Console

### No WiFi networks found
```bash
# Check WiFi is enabled:
iwconfig

# Try manual scan:
sudo iwlist wlan0 scan
```

## 💡 Pro Tips

### 1. Room Preparation
- Clear path to all 9 positions
- Use consistent height (table/floor)
- Keep Pi in same orientation

### 2. Accurate Measurements
- Wait 2-3 seconds at each position before pressing Enter
- Keep Pi away from metal objects
- Don't block the WiFi antenna with your hand

### 3. Multiple Rooms
- Run separately for each room
- Data saves with timestamp
- Compare results between rooms

### 4. Best Practices
- Run during typical usage time (not 3 AM when everyone's asleep)
- Close doors as they'd normally be
- Turn on devices that might interfere (microwave, etc.)

## 📁 Output Files

- `wifi_scan_data.json` - Complete scan data
- `/tmp/speech.mp3` - Last voice message (temporary)
- Logs sent to server at `10.185.124.107:5000`

## 🎯 Use Cases

- **New home/office**: Find best router placement
- **Troubleshooting**: Identify dead zones
- **Optimization**: See if router position helps
- **Comparison**: Test before/after changes
- **Documentation**: Professional WiFi site survey

## 🆓 Free Tier Limits

- **ElevenLabs**: 10,000 characters/month (plenty!)
- **Google Gemini**: 60 requests/minute (more than enough)
- Both are FREE for personal use!

## 🚀 Ready to Scan!

```bash
# 1. Copy file to Pi (via WinSCP)
# 2. Add API keys
# 3. SSH to Pi
# 4. Run:
python3 pi_grid_scanner.py

# Follow voice instructions!
```

Your room WiFi analysis awaits! 🎯📡
