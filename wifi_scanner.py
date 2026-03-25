import subprocess
import time
import matplotlib.pyplot as plt
from datetime import datetime


def scan_wifi(interface: str = "wlan0"):
    """
    Returns a list of dicts with keys: ESSID, Signal, BSSID.
    Always returns a list (empty on error) so callers can safely iterate.
    """
    networks = []

    # Try modern iw syntax; avoid sudo here to prevent permission prompts.
    # If the user lacks privileges, iw will print an error and we return [].
    result = subprocess.run(
        ["iw", "dev", interface, "scan"], capture_output=True, text=True
    )

    if result.returncode != 0:
        # Common causes: not enough privileges, rfkill, interface down/missing.
        # Do not raise; just return empty so the main loop keeps running.
        return []

    output = result.stdout

    current = {}
    for raw in output.splitlines():
        line = raw.strip()
        if line.startswith("BSS "):
            if current:
                networks.append(current)
            # e.g., "BSS aa:bb:cc:dd:ee:ff(on wlan0)"
            parts = line.split()
            bssid = parts[1] if len(parts) > 1 else None
            current = {"BSSID": bssid}
        elif "SSID:" in line:
            current["ESSID"] = line.split("SSID:", 1)[1].strip()
        elif "signal:" in line:
            # line like: signal: -45.00 dBm
            try:
                sig_val = line.split("signal:", 1)[1].strip().split()[0]
            except Exception:
                sig_val = None
            current["Signal"] = sig_val

    if current:
        networks.append(current)

    # Filter out incomplete/unknown entries here to reduce downstream work.
    cleaned = [
        n for n in networks if n.get("ESSID") not in (None, "", "Unknown") and n.get("Signal") not in (None, "N/A")
    ]
    return cleaned


def plot_signal_strength(data):
    """
    Plots signal strength over time for each ESSID.
    """
    plt.figure(figsize=(10, 6))
    for essid, values in data.items():
        times, signals = zip(*values)
        plt.plot(times, signals, label=essid)

    plt.xlabel("Time")
    plt.ylabel("Signal Strength (dBm)")
    plt.title("WiFi Signal Strength Over Time")
    plt.legend()
    plt.grid()
    plt.show()


# Old code commented out
# signal_data = {}
# while True:
#     networks = scan_wifi()
#     print("WiFi Scan Results:")
#     current_time = datetime.now().strftime("%H:%M:%S")
#     for net in networks:
#         essid = net.get("ESSID")
#         signal = float(net.get("Signal"))
#         print(f"Time: {current_time}, ESSID: {essid}, Signal: {signal}")

#         # Log data for plotting
#         if essid not in signal_data:
#             signal_data[essid] = []
#         signal_data[essid].append((current_time, signal))

#     # Plot the data every 5 scans
#     if len(signal_data) % 5 == 0:
#         plot_signal_strength(signal_data)

#     time.sleep(10)

# New code to calculate average signal strength every second
signal_data = {}
while True:
    networks = scan_wifi()
    print("WiFi Scan Results:")
    current_time = datetime.now().strftime("%H:%M:%S")
    total_signal = 0
    count = 0

    for net in networks:
        essid = net.get("ESSID")
        signal = float(net.get("Signal"))
        total_signal += signal
        count += 1
        print(f"Time: {current_time}, ESSID: {essid}, Signal: {signal}")

    if count > 0:
        average_signal = total_signal / count
        print(f"Time: {current_time}, Average Signal Strength: {average_signal:.2f} dBm")

    time.sleep(1)
