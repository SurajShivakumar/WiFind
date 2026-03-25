# 🚀 Raspberry Pi Speed Test Setup

## 📋 Overview

Your speed test now tests the **Raspberry Pi's connection**, not your browser! This gives you accurate results for the device that's actually scanning WiFi.

## 🎯 Quick Setup on Raspberry Pi

### Step 1: Install speedtest-cli

SSH into your Raspberry Pi and run ONE of these commands:

**Option A - APT (Recommended):**
```bash
sudo apt-get update
sudo apt-get install speedtest-cli
```

**Option B - PIP (If APT doesn't work):**
```bash
sudo pip3 install speedtest-cli
```

### Step 2: Copy the speed test script

The file `pi_speedtest.py` is already created! Just copy it to your Raspberry Pi:

**From your Windows PC:**
```powershell
# Using SCP (if you have it)
scp pi_speedtest.py pi@10.185.124.49:~/

# Or use WinSCP / FileZilla to transfer the file
```

**Or create it directly on Pi:**
```bash
nano pi_speedtest.py
# Copy the contents from the file on your PC
# Press Ctrl+X, then Y, then Enter to save
```

### Step 3: Make it executable

```bash
chmod +x pi_speedtest.py
```

### Step 4: Test it!

```bash
python3 pi_speedtest.py
```

## 🎮 How to Use

### From the Webpage:

1. Open: http://10.185.124.107:5000
2. Scroll to bottom - "Internet Speed Test" section
3. Click **"🚀 Test Raspberry Pi Speed"**
4. Follow the popup instructions:
   - SSH into Pi
   - Run: `python3 pi_speedtest.py`
   - Wait ~30 seconds
5. Results appear automatically on webpage!

### Direct on Pi:

```bash
# Just run anytime
python3 pi_speedtest.py
```

Results will:
- ✅ Display in terminal
- ✅ Send to server automatically
- ✅ Appear on all connected web browsers
- ✅ Show quality rating (EXCELLENT, GOOD, POOR, etc.)

## 📊 What Gets Tested

The Pi tests:
- **Download Speed** - How fast Pi can download
- **Upload Speed** - How fast Pi can upload  
- **Ping** - Pi's latency to speed test server
- **Server Info** - Which test server was used
- **IP Address** - Pi's public IP
- **ISP** - Your internet service provider

## 🎨 Quality Ratings

Same as before! Based on Pi's connection:

| Rating | Download | Upload | Ping |
|--------|----------|--------|------|
| 🟢 EXCELLENT | 100+ Mbps | 50+ Mbps | <20ms |
| 🟢 VERY GOOD | 50+ Mbps | 25+ Mbps | <40ms |
| 🟡 GOOD | 25+ Mbps | 10+ Mbps | <60ms |
| 🟠 FAIR | 10+ Mbps | 5+ Mbps | <100ms |
| 🔴 POOR | 5+ Mbps | 2+ Mbps | 100+ms |
| 🔴 VERY POOR | <5 Mbps | <2 Mbps | 100+ms |

## 🔧 Troubleshooting

### "speedtest-cli: command not found"
**Fix:** Install it:
```bash
sudo apt-get install speedtest-cli
# OR
sudo pip3 install speedtest-cli
```

### "Connection refused" error
**Fix:** Make sure server is running on Windows PC (10.185.124.107:5000)

### Speed test hangs
**Fix:** 
- Check Pi's internet connection: `ping google.com`
- Try different server: `speedtest-cli --list` (find nearest)
- Increase timeout in script

### Results not appearing on webpage
**Fix:**
- Check server logs on Windows PC
- Make sure webpage is open and connected
- Try refreshing page with Ctrl+Shift+R

## 💡 Pro Tips

### Automate Speed Tests

Run speed test every hour:
```bash
# Edit crontab
crontab -e

# Add this line (runs every hour)
0 * * * * /usr/bin/python3 /home/pi/pi_speedtest.py >> /home/pi/speedtest.log 2>&1
```

### Quick Alias

Add to `~/.bashrc`:
```bash
alias speedtest='python3 ~/pi_speedtest.py'
```

Then just type: `speedtest`

### Compare Locations

Run speed test as you walk around:
1. Go to room corner #1
2. Run: `python3 pi_speedtest.py`
3. Note the speeds
4. Move to different location
5. Run again
6. Compare results!

This shows if WiFi location affects internet speed!

## 📁 Files

- **pi_speedtest.py** - Run this on Raspberry Pi
- **heatmap_server.py** - Updated with `/api/speedtest` endpoint
- **templates/index.html** - Updated with Pi speed test UI

## 🚀 Next Steps

1. ✅ Install speedtest-cli on Pi
2. ✅ Copy pi_speedtest.py to Pi
3. ✅ Run test and watch results appear!

Your WiFi scanner is already running - now you can test actual internet speed too! 📡⚡
