import urllib.request
import json
import time

# The default IP address for the ESP32 when acting as a Wi-Fi Access Point
ESP32_URL = "http://192.168.4.1/data"

def fetch_air_quality():
    try:
        # Fetch the data from the ESP32's /data route
        response = urllib.request.urlopen(ESP32_URL, timeout=5)
        
        # Read and decode the response
        data = response.read().decode('utf-8')
        
        # Parse the JSON data (which comes from your ESP32 handleData() function)
        sensor_data = json.loads(data)
        
        # Print the data nicely to the terminal
        print("\n--- Air Quality Reading ---")
        print(f"PM1.0: {sensor_data.get('pm1_0')} ug/m3")
        print(f"PM2.5: {sensor_data.get('pm2_5')} ug/m3")
        print(f"PM10:  {sensor_data.get('pm10')} ug/m3")
        
        mode = "Manual" if sensor_data.get('manual') == 1 else "Auto"
        motor = "ON" if sensor_data.get('motor') == 1 else "OFF"
        print(f"System Mode: {mode} | Motor Status: {motor}")
        print("---------------------------")
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        print("Make sure your Raspberry Pi is connected to the 'ESP32-Air-Monitor' Wi-Fi network.")

if __name__ == "__main__":
    print("Starting automatic data fetcher... (Press Ctrl+C to stop)")
    # Loop infinitely, fetching data every 5 seconds
    try:
        while True:
            fetch_air_quality()
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nData fetcher stopped.")
