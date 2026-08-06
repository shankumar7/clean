"""
Configuration settings for the Raspberry Pi Air Quality Monitor & Host Web Server.
"""

import os

# Server Configuration
SERVER_HOST = "0.0.0.0"
SERVER_PORT = int(os.environ.get("AIR_MONITOR_PORT", 5000))

# Hardware Configuration (Raspberry Pi UART & GPIO)
DEFAULT_SERIAL_PORT = "/dev/ttyS0"  # Alternatives: /dev/ttyAMA0, /dev/ttyUSB0
SERIAL_BAUDRATE = 9600
RELAY_GPIO_PIN = 23                 # Active LOW mapping (GPIO 23)
ACTIVE_LOW_RELAY = True

# Safety Controls & Defaults
DEFAULT_PM25_THRESHOLD = 200        # Automatic motor trigger limit (ug/m3)
HISTORICAL_DATA_POINTS = 60         # History queue size for live trend chart

# Simulation Mode (Auto-detected if RPi libraries or serial port are missing)
FORCE_SIMULATION = os.environ.get("SIMULATION_MODE", "false").lower() in ("1", "true", "yes")

# AQI Categories & Precautions (Matched to clean.txt)
AQI_LEVELS = [
    {
        "max": 50,
        "label": "Good",
        "color": "#4CAF50",
        "precaution": "Air quality is great! Safe to enjoy outdoor physical exercise."
    },
    {
        "max": 100,
        "label": "Moderate",
        "color": "#FF9800",
        "precaution": "Acceptable quality. Unusually sensitive people should limit heavy outdoor work."
    },
    {
        "max": 200,
        "label": "Poor",
        "color": "#F44336",
        "precaution": "Wear air masks outdoors. Sensitive individuals should remain inside."
    },
    {
        "max": 99999,
        "label": "Hazardous",
        "color": "#730202",
        "precaution": "Hazardous air! Close all windows, run air filters, and keep motor running."
    }
]
