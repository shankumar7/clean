"""
Thread-safe shared state management engine for Air Quality Monitor.
"""

import threading
import time
from collections import deque
import config


class AirQualityMonitor:
    def __init__(self, pm25_threshold=config.DEFAULT_PM25_THRESHOLD):
        self._lock = threading.Lock()
        
        # Sensor data
        self.pm1_0 = 0
        self.pm2_5 = 0
        self.pm10 = 0
        self.last_update_time = 0
        
        # Operational controls
        self.manual_mode = False       # False = AUTO, True = MANUAL
        self.motor_state = False       # False = OFF, True = ON
        self.pm25_threshold = pm25_threshold
        
        # Hardware Driver Callbacks
        self.relay_callback = None     # Callable: func(motor_on: bool)
        
        # Historical buffer for live charts (timestamp, pm1_0, pm2_5, pm10)
        self.history = deque(maxlen=config.HISTORICAL_DATA_POINTS)
        
        # Change listeners (GUI callbacks)
        self._listeners = []

    def register_listener(self, callback):
        """Register a callback function to be invoked on state updates."""
        with self._lock:
            if callback not in self._listeners:
                self._listeners.append(callback)

    def set_relay_callback(self, callback):
        """Set hardware relay handler."""
        with self._lock:
            self.relay_callback = callback

    def update_sensor_data(self, pm1_0: int, pm2_5: int, pm10: int):
        """
        Update particulate matter readings and evaluate automated safety triggers.
        """
        with self._lock:
            self.pm1_0 = max(0, int(pm1_0))
            self.pm2_5 = max(0, int(pm2_5))
            self.pm10 = max(0, int(pm10))
            self.last_update_time = time.time()
            
            # Record in history buffer
            self.history.append({
                "timestamp": time.strftime("%H:%M:%S"),
                "pm1_0": self.pm1_0,
                "pm2_5": self.pm2_5,
                "pm10": self.pm10,
                "motor": self.motor_state,
                "manual": self.manual_mode
            })
            
            # AUTOMATED SAFETY CONTROL (In AUTO Mode)
            if not self.manual_mode:
                target_motor_state = (self.pm2_5 > self.pm25_threshold)
                if self.motor_state != target_motor_state:
                    self._apply_motor_state(target_motor_state)
        
        self._notify_listeners()

    def set_manual_mode(self, manual: bool):
        """Switch between AUTO (false) and MANUAL (true) modes."""
        with self._lock:
            self.manual_mode = bool(manual)
            # If returning to AUTO mode, re-evaluate safety trigger immediately
            if not self.manual_mode:
                target_motor_state = (self.pm2_5 > self.pm25_threshold)
                self._apply_motor_state(target_motor_state)
        
        self._notify_listeners()

    def set_motor_state(self, state: bool):
        """Manually toggle motor state (Only allowed in MANUAL mode)."""
        with self._lock:
            if not self.manual_mode:
                return False  # Rejected: Cannot manually set motor state in AUTO mode
            
            self._apply_motor_state(state)
        
        self._notify_listeners()
        return True

    def set_pm25_threshold(self, threshold: int):
        """Update PM2.5 trigger limit for Auto Mode."""
        with self._lock:
            self.pm25_threshold = max(10, int(threshold))
            if not self.manual_mode:
                target_motor_state = (self.pm2_5 > self.pm25_threshold)
                self._apply_motor_state(target_motor_state)
        
        self._notify_listeners()

    def _apply_motor_state(self, state: bool):
        """Internal helper to change motor state and trigger hardware relay."""
        self.motor_state = bool(state)
        if self.relay_callback:
            try:
                self.relay_callback(self.motor_state)
            except Exception as e:
                print(f"[AirQualityMonitor] Relay callback error: {e}")

    def get_aqi_info(self):
        """Get AQI category label, color badge, and health recommendation."""
        val = self.pm2_5
        for level in config.AQI_LEVELS:
            if val <= level["max"]:
                return level
        return config.AQI_LEVELS[-1]

    def get_state_dict(self):
        """Get full state payload for Web API & GUI."""
        with self._lock:
            aqi = self.get_aqi_info()
            return {
                "pm1_0": self.pm1_0,
                "pm2_5": self.pm2_5,
                "pm10": self.pm10,
                "motor": 1 if self.motor_state else 0,
                "manual": 1 if self.manual_mode else 0,
                "pm25_threshold": self.pm25_threshold,
                "aqi_label": aqi["label"],
                "aqi_color": aqi["color"],
                "precaution": aqi["precaution"],
                "last_update": self.last_update_time,
                "history": list(self.history)
            }

    def _notify_listeners(self):
        """Notify registered GUI listeners of changes."""
        with self._lock:
            listeners_copy = list(self._listeners)
        
        state = self.get_state_dict()
        for cb in listeners_copy:
            try:
                cb(state)
            except Exception as e:
                print(f"[AirQualityMonitor] Listener callback error: {e}")
