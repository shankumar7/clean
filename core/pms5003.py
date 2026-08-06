"""
PMS5003 Particulate Matter Sensor UART driver & simulation fallback.
"""

import time
import random
import threading
import config

try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False


class PMS5003Reader(threading.Thread):
    def __init__(self, monitor_engine, port=config.DEFAULT_SERIAL_PORT, baudrate=config.SERIAL_BAUDRATE):
        super().__init__(daemon=True)
        self.monitor = monitor_engine
        self.port = port
        self.baudrate = baudrate
        self.running = False
        self.is_simulated = False
        self.serial_conn = None

    def run(self):
        self.running = True
        
        # Check if simulation is explicitly forced or serial port unavailable
        if config.FORCE_SIMULATION or not SERIAL_AVAILABLE:
            print("[PMS5003] Running in SIMULATED mode.")
            self.is_simulated = True
            self._run_simulation()
            return

        # Attempt hardware serial connection
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=2)
            print(f"[PMS5003] Connected to UART serial on {self.port} @ {self.baudrate} baud.")
            self._run_hardware_reader()
        except Exception as e:
            print(f"[PMS5003] Unable to open serial port '{self.port}': {e}")
            print("[PMS5003] Falling back to SIMULATED sensor mode.")
            self.is_simulated = True
            self._run_simulation()

    def stop(self):
        self.running = False
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.close()
            except Exception:
                pass

    def _run_hardware_reader(self):
        """Reads 32-byte PMS5003 frame from UART serial stream."""
        buffer = bytearray()
        
        while self.running:
            try:
                if self.serial_conn.in_waiting > 0:
                    byte = self.serial_conn.read(1)
                    if not byte:
                        continue
                    
                    buffer.append(byte[0])
                    
                    # Look for frame start header 0x42 0x4D
                    if len(buffer) == 1 and buffer[0] != 0x42:
                        buffer.clear()
                        continue
                    if len(buffer) == 2 and buffer[1] != 0x4D:
                        buffer.clear()
                        continue
                    
                    # Read full 32-byte frame
                    if len(buffer) == 32:
                        # Verify checksum
                        calc_checksum = sum(buffer[0:30])
                        frame_checksum = (buffer[30] << 8) | buffer[31]
                        
                        if calc_checksum == frame_checksum:
                            pm1_0 = (buffer[4] << 8) | buffer[5]
                            pm2_5 = (buffer[6] << 8) | buffer[7]
                            pm10  = (buffer[8] << 8) | buffer[9]
                            
                            self.monitor.update_sensor_data(pm1_0, pm2_5, pm10)
                        else:
                            print("[PMS5003] Checksum mismatch error!")
                        
                        buffer.clear()
                else:
                    time.sleep(0.1)
            except Exception as e:
                print(f"[PMS5003] Serial read error: {e}")
                time.sleep(1)

    def _run_simulation(self):
        """Generates realistic varying particulate readings for testing."""
        sim_pm2_5 = 35.0
        
        while self.running:
            # Random walk variation
            change = random.uniform(-4.0, 5.0)
            sim_pm2_5 = max(5.0, min(350.0, sim_pm2_5 + change))
            
            # Periodically spike to test Hazardous safety trigger
            if random.random() < 0.05:
                sim_pm2_5 = random.uniform(205.0, 260.0)
            
            pm2_5 = int(sim_pm2_5)
            pm1_0 = int(pm2_5 * random.uniform(0.6, 0.8))
            pm10 = int(pm2_5 * random.uniform(1.2, 1.5))
            
            self.monitor.update_sensor_data(pm1_0, pm2_5, pm10)
            time.sleep(2.0)
