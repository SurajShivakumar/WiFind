# 🚀 Quick Start Guide - Raspberry Pi

## 📋 What You Need to Run

You have **TWO scripts** to run on your Raspberry Pi:

### 1️⃣ WiFi Scanner (ALWAYS RUNNING)
**File:** `pi_simple_http.py`  
**Purpose:** Continuously scans WiFi signal strength and sends to server

### 2️⃣ Speed Test (RUN WHEN NEEDED)
**File:** `pi_speedtest.py`  
**Purpose:** Tests Pi's internet speed and sends results to server

---

## 🎯 Step-by-Step: Start Everything

### On Raspberry Pi (SSH or Terminal):

```bash
# Navigate to your project folder
cd ~/

# Copy the scripts from your PC first (if not already there)
# Use WinSCP, FileZilla, or SCP to transfer:
# - pi_simple_http.py
# - pi_speedtest.py

# Make them executable
chmod +x pi_simple_http.py
chmod +x pi_speedtest.py

# START WiFi Scanner (runs forever)
python3 pi_simple_http.py
```

You should see:
```
============================================================
WiFi Scanner - Plain HTTP Only
Server: 10.185.124.107:5000
============================================================
✓ -67 dBm | YourNetworkName
✓ -65 dBm | YourNetworkName
✓ -68 dBm | YourNetworkName
```

**Leave this running!** Open a new SSH session for other tasks.

---

## 🏃‍♂️ Quick Commands

### Start WiFi Scanner
```bash
python3 pi_simple_http.py
```

### Run Speed Test (in a NEW terminal/SSH session)
```bash
# First time: Install speedtest-cli
sudo apt-get update
sudo apt-get install speedtest-cli

# Then run test
python3 pi_speedtest.py
```

### Stop WiFi Scanner
Press `Ctrl + C`

---

## 🔧 Run WiFi Scanner in Background (Optional)

Want to run WiFi scanner and still use the terminal?

```bash
# Start in background
python3 pi_simple_http.py &

# Check if running
ps aux | grep pi_simple_http

# Stop it later
pkill -f pi_simple_http.py

# Or use screen/tmux for professional approach
screen -S wifi
python3 pi_simple_http.py
# Press Ctrl+A then D to detach
# Reconnect: screen -r wifi
```

---

## ✅ Checklist

Before starting:
- [ ] Server running on Windows PC (http://10.185.124.107:5000)
- [ ] Pi connected to WiFi
- [ ] Pi can reach server: `ping 10.185.124.107`
- [ ] Scripts copied to Pi
- [ ] Scripts are executable: `chmod +x *.py`

To verify it's working:
- [ ] WiFi scanner shows `✓` checkmarks
- [ ] Windows server logs show: `POST /api/signal HTTP/1.1" 200`
- [ ] Webpage shows "Total Points" increasing
- [ ] Latest Signal value updating on webpage

---

## 🆘 Troubleshooting

### "No module named 'http'"
**Fix:** You're using Python 2. Use Python 3:
```bash
python3 pi_simple_http.py
```

### "Connection refused"
**Fix:** Make sure server is running on Windows PC
```bash
# Test from Pi
ping 10.185.124.107
curl http://10.185.124.107:5000
```

### "iw: command not found"
**Fix:** Install wireless tools:
```bash
sudo apt-get install wireless-tools iw
```

### WiFi scanner stops randomly
**Fix:** Use `screen` or add to systemd service (see advanced section below)

---

## 🚀 Advanced: Auto-Start on Boot

Want WiFi scanner to start automatically when Pi boots?

### Create Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/wifi-scanner.service
```

Paste this:
```ini
[Unit]
Description=WiFi Signal Scanner
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi
ExecStart=/usr/bin/python3 /home/pi/pi_simple_http.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
# Enable auto-start on boot
sudo systemctl enable wifi-scanner.service

# Start now
sudo systemctl start wifi-scanner.service

# Check status
sudo systemctl status wifi-scanner.service

# View logs
sudo journalctl -u wifi-scanner.service -f
```

---

## 📊 Current Setup

**Your Configuration:**
- **Server IP:** 10.185.124.107
- **Server Port:** 5000
- **Pi IP:** 10.185.124.49 (probably - check with `hostname -I`)
- **Scan Interval:** 1 second
- **Protocol:** Plain HTTP (no SSL)

**What's Working:**
- ✅ Server receiving signals (you saw this before)
- ✅ WiFi strength detection
- ✅ Real-time updates via WebSocket

**What You Still Need:**
- [ ] Start Pi WiFi scanner again
- [ ] Set up Pi speed test (optional)
- [ ] Configure GPS on phone (for map positioning)
- [ ] Get Mapbox token (for satellite map view)

---

## 🎯 Right Now - Do This:

1. **SSH into your Raspberry Pi:**
   ```bash
   ssh pi@10.185.124.49
   # Password: raspberry (or whatever you set)
   ```

2. **Navigate to scripts:**
   ```bash
   cd ~/
   # Or wherever you copied the scripts
   ```

3. **Start WiFi Scanner:**
   ```bash
   python3 pi_simple_http.py
   ```

4. **See it working!**
   - Pi terminal shows: `✓ -67 dBm | NetworkName`
   - Windows server logs show: `POST /api/signal`
   - Webpage shows signals updating

That's it! The Pi is now scanning and sending data! 🎉

For speed test, open a NEW terminal and run `python3 pi_speedtest.py` whenever you want to test speed.
