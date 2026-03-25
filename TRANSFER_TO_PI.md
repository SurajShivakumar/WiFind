# Transfer Python Client to Raspberry Pi

## Quick Transfer Commands

Run these commands from your **Windows PC** (in PowerShell):

### Transfer pi_client.py (Recommended - Full Featured):
```powershell
scp pi_client.py admin@10.185.124.49:/home/admin/
```

### Or Transfer pi_client_simple.py (Simple Version):
```powershell
scp pi_client_simple.py admin@10.185.124.49:/home/admin/
```

### Or Transfer wifi_scanner_client.py:
```powershell
scp wifi_scanner_client.py admin@10.185.124.49:/home/admin/
```

## After Transfer - Run on Raspberry Pi:

### SSH into Pi:
```bash
ssh admin@10.185.124.49
```

### Run the client:

**If you transferred pi_client.py:**
```bash
sudo python3 pi_client.py --server http://10.185.124.107:5000
```

**If you transferred pi_client_simple.py:**
```bash
sudo python3 pi_client_simple.py
```

**If you transferred wifi_scanner_client.py:**
```bash
sudo python3 wifi_scanner_client.py --server http://10.185.124.107:5000
```

## Success Output:
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

## Troubleshooting:

### If file transfer fails:
- Make sure you're in the correct directory: `cd "C:\Users\User-A\Documents\dubhacks code"`
- Check SSH connection: `ssh admin@10.185.124.49 "echo connected"`

### If Python file not found on Pi:
- Check files on Pi: `ssh admin@10.185.124.49 "ls -la *.py"`
- Re-transfer the file using scp command above
