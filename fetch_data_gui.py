import urllib.request
import json
import tkinter as tk
from tkinter import ttk

# The default IP address for the ESP32 Access Point
ESP32_URL = "http://192.168.4.1/data"

class AirQualityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Air Quality Monitor")
        self.root.geometry("400x350")
        self.root.configure(padx=20, pady=20)
        
        # Set up some basic styling
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", font=("Helvetica", 14))
        style.configure("Header.TLabel", font=("Helvetica", 20, "bold"))
        style.configure("Value.TLabel", font=("Helvetica", 18, "bold"), foreground="#007BFF")
        
        # Header Label
        ttk.Label(root, text="ESP32 Air Quality Monitor", style="Header.TLabel").pack(pady=(0, 20))
        
        # Variables to hold the text for the labels
        self.pm1_var = tk.StringVar(value="PM1.0: -- ug/m3")
        self.pm25_var = tk.StringVar(value="PM2.5: -- ug/m3")
        self.pm10_var = tk.StringVar(value="PM10:  -- ug/m3")
        self.status_var = tk.StringVar(value="Mode: --  |  Motor: --")
        self.error_var = tk.StringVar(value="Connecting to ESP32...")
        
        # Create and pack the display labels
        ttk.Label(root, textvariable=self.pm1_var, style="Value.TLabel").pack(pady=5)
        ttk.Label(root, textvariable=self.pm25_var, style="Value.TLabel").pack(pady=5)
        ttk.Label(root, textvariable=self.pm10_var, style="Value.TLabel").pack(pady=5)
        
        # A horizontal separator line
        ttk.Separator(root, orient='horizontal').pack(fill='x', pady=20)
        
        # Status Label (Motor & Mode)
        ttk.Label(root, textvariable=self.status_var).pack(pady=5)
        
        # Error / Status message Label
        error_label = ttk.Label(root, textvariable=self.error_var, foreground="red", font=("Helvetica", 10))
        error_label.pack(pady=10)
        
        # Start fetching data in the background
        self.update_data()
        
    def update_data(self):
        try:
            # Fetch the data from the ESP32's /data route
            response = urllib.request.urlopen(ESP32_URL, timeout=3)
            data = response.read().decode('utf-8')
            sensor_data = json.loads(data)
            
            # Update the Tkinter string variables
            self.pm1_var.set(f"PM1.0: {sensor_data.get('pm1_0', '--')} ug/m3")
            self.pm25_var.set(f"PM2.5: {sensor_data.get('pm2_5', '--')} ug/m3")
            self.pm10_var.set(f"PM10:  {sensor_data.get('pm10', '--')} ug/m3")
            
            mode = "Manual" if sensor_data.get('manual') == 1 else "Auto"
            motor = "ON" if sensor_data.get('motor') == 1 else "OFF"
            self.status_var.set(f"Mode: {mode}  |  Motor: {motor}")
            
            # Clear error text if connection is successful
            self.error_var.set("Connected - Live Data")
            error_label_color = "green"
            
        except Exception as e:
            # Show error if Wi-Fi drops or ESP32 is off
            self.error_var.set("Connection Error. Ensure Pi is on 'ESP32-Air-Monitor' Wi-Fi.")
            
        # Schedule this function to run again in 2000 milliseconds (2 seconds)
        self.root.after(2000, self.update_data)

if __name__ == "__main__":
    # Initialize the Tkinter window
    root = tk.Tk()
    app = AirQualityApp(root)
    # Start the GUI event loop
    root.mainloop()
