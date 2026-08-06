import time
import json
import urllib.request
import threading

ESP32_URL = "http://192.168.4.1/data"

class ESP32Fetcher(threading.Thread):
    def __init__(self, monitor_engine):
        super().__init__(daemon=True)
        self.monitor = monitor_engine
        self.running = False

    def run(self):
        self.running = True
        print(f"[ESP32Fetcher] Starting to fetch data from {ESP32_URL}")
        
        while self.running:
            try:
                response = urllib.request.urlopen(ESP32_URL, timeout=3)
                data = response.read().decode('utf-8')
                sensor_data = json.loads(data)
                
                pm1_0 = int(sensor_data.get('pm1_0', 0))
                pm2_5 = int(sensor_data.get('pm2_5', 0))
                pm10 = int(sensor_data.get('pm10', 0))
                
                # Update the shared monitor engine so the GUI and Web Server see it
                self.monitor.update_sensor_data(pm1_0, pm2_5, pm10)
                
            except Exception as e:
                print(f"[ESP32Fetcher] Error fetching data: {e}")
                
            # Wait 2 seconds before fetching again
            time.sleep(2.0)

    def stop(self):
        self.running = False
