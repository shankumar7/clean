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
                motor = int(sensor_data.get('motor', 0))
                manual = int(sensor_data.get('manual', 0))
                
                # Update the shared monitor engine so the GUI and Web Server see it
                self.monitor.update_sensor_data(pm1_0, pm2_5, pm10)
                
                # Sync the motor and manual mode from the ESP32 (if it changed remotely)
                if hasattr(self.monitor, '_lock'):
                    with self.monitor._lock:
                        self.monitor.motor_state = (motor == 1)
                        self.monitor.manual_mode = (manual == 1)
                    # Use a private variable to avoid infinite loops, just notify listeners
                    self.monitor._notify_listeners()
                
            except Exception as e:
                print(f"[ESP32Fetcher] Error fetching data: {e}")
                
            # Wait 2 seconds before fetching again
            time.sleep(2.0)

    def stop(self):
        self.running = False
