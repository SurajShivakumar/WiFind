# Raspberry Pi Setup Instructions

## Quick Start

Your PC Server is running at: **http://10.185.124.107:5000**

## Step 1: Transfer Files to Raspberry Pi

From your PC, copy the files to your Raspberry Pi:

```bash
scp pi_client_simple.py START_RASPBERRY_PI.sh admin@10.185.124.49:/home/admin/
```

## Step 2: SSH into Raspberry Pi

```bash
ssh admin@10.185.124.49
```

## Step 3: Make Script Executable

```bash
chmod +x START_RASPBERRY_PI.sh
```

## Step 4: Run the Scanner

```bash
./START_RASPBERRY_PI.sh
```

**OR manually run:**

```bash
sudo python3 pi_client_simple.py
```

## What You'll See

The Raspberry Pi will start scanning WiFi and sending data to your PC:

```
==============================================
WiFi Scanner - Sending to http://10.185.124.107:5000
==================================================
✓ -45 dBm | T-Mobile 5G Gateway
✓ -47 dBm | T-Mobile 5G Gateway
✓ -46 dBm | T-Mobile 5G Gateway
```

## Troubleshooting

### Can't Connect to Server

1. **Check if PC firewall is blocking:**
   - On your Windows PC, run PowerShell as Administrator:
   ```powershell
   New-NetFirewallRule -DisplayName "Python Flask" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
   ```

2. **Test connection from Pi:**
   ```bash
   curl http://10.185.124.107:5000/api/status
   ```

### No WiFi Signal Data

- Make sure you're running with `sudo`
- Check your WiFi interface name: `ip link` or `iwconfig`
- If not `wlan0`, edit `pi_client_simple.py` line 12

### Permission Denied

- The script needs sudo to scan WiFi: `sudo python3 pi_client_simple.py`

## Using the System

1. **Open web interface** on your PC: http://localhost:5000
2. **Start this Pi scanner** (you should see green checkmarks)
3. **Calibrate the room** in the web interface (click 4 corners)
4. **Walk around** with the Raspberry Pi
5. **Click where you are** on the map as you walk
6. **Watch the heatmap** build in real-time!

## Stop the Scanner

Press `Ctrl+C` in the terminal where the scanner is running.
