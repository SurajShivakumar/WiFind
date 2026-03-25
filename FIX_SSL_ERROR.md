# Fix SSL Connection Error

## Problem
The Raspberry Pi was trying to use HTTPS/SSL when connecting to the server, but the server only supports plain HTTP.

## Solution
I've updated both client files to force HTTP connections. Now you need to transfer the updated files to your Pi.

## Steps to Fix:

### 1. Transfer Updated Files to Pi

From your Windows PC in PowerShell:

```powershell
cd "C:\Users\User-A\Documents\dubhacks code"
scp pi_client.py pi_client_simple.py admin@10.185.124.49:/home/admin/
```

### 2. SSH to Pi and Run

```bash
ssh admin@10.185.124.49
```

### 3. Run the Updated Client

**Option A - Simple client:**
```bash
sudo python3 pi_client_simple.py
```

**Option B - Full client:**
```bash
sudo python3 pi_client.py --server http://10.185.124.107:5000
```

## What Fixed:
- Removed SSL/HTTPS attempts
- Force plain HTTP connections
- The server logs showed `10.185.124.49` was connecting but getting 400 errors due to SSL handshake attempts
- Now it will use plain HTTP correctly

## Expected Output:
```
==========================================================
WiFi Scanner Client
Server: http://10.185.124.107:5000
Interface: wlan0
==========================================================
✓ -45 dBm | T-Mobile 5G Gateway
✓ -47 dBm | T-Mobile 5G Gateway
✓ -46 dBm | T-Mobile 5G Gateway
```

The green checkmarks (✓) mean data is successfully sending to your PC!
