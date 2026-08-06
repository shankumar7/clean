"""
Tab 4: System Diagnostics, Hardware Status & Event Logs.
"""

import time
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTextEdit, QGridLayout
)
from PyQt6.QtCore import Qt
from gui.components.cards import MetricCard
import config


class DiagnosticsTab(QWidget):
    def __init__(self, monitor_engine, parent=None):
        super().__init__(parent)
        self.monitor = monitor_engine
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)
        
        # Title
        title_lbl = QLabel("SYSTEM DIAGNOSTICS & SYSTEM LOGS")
        title_lbl.setStyleSheet("color: #38bdf8; font-size: 14px; font-weight: bold; letter-spacing: 1px;")
        main_layout.addWidget(title_lbl)
        
        # Grid of hardware status cards
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)
        
        self.card_serial = MetricCard("PMS5003 UART Port", "")
        self.card_serial.set_value(config.DEFAULT_SERIAL_PORT)
        
        self.card_gpio = MetricCard("GPIO Relay Pin", "")
        self.card_gpio.set_value(f"GPIO {config.RELAY_GPIO_PIN}")
        
        self.card_port = MetricCard("Web Server Port", "")
        self.card_port.set_value(str(config.SERVER_PORT))
        
        self.card_status = MetricCard("System Engine", "")
        self.card_status.set_value("RUNNING")
        
        grid_layout.addWidget(self.card_serial, 0, 0)
        grid_layout.addWidget(self.card_gpio, 0, 1)
        grid_layout.addWidget(self.card_port, 0, 2)
        grid_layout.addWidget(self.card_status, 0, 3)
        
        main_layout.addLayout(grid_layout)
        
        # Live Activity Log Console Box
        log_frame = QFrame()
        log_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(15, 23, 42, 0.8);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px;
            }
        """)
        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(16, 12, 16, 12)
        
        log_title = QLabel("REAL-TIME SYSTEM ACTIVITY & SENSOR EVENTS LOG")
        log_title.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        log_layout.addWidget(log_title)
        
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setStyleSheet("""
            QTextEdit {
                background-color: #090d16;
                color: #38bdf8;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                border: 1px solid #1e293b;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        log_layout.addWidget(self.log_console, stretch=1)
        
        main_layout.addWidget(log_frame, stretch=1)
        
        # Log initial event
        self.append_log("System Diagnostics Initialized.")
        self.append_log(f"Listening on Host Port: {config.SERVER_PORT}")
        self.append_log(f"UART Serial Device Target: {config.DEFAULT_SERIAL_PORT}")
        self.append_log(f"GPIO Active-LOW Output Pin: {config.RELAY_GPIO_PIN}")

    def append_log(self, text):
        timestamp = time.strftime("[%H:%M:%S]")
        self.log_console.append(f"{timestamp} {text}")

    def update_ui(self, state):
        pm25 = state["pm2_5"]
        motor = "ON" if state["motor"] == 1 else "OFF"
        mode = "MANUAL" if state["manual"] == 1 else "AUTO"
        
        # Periodically log state updates
        if not hasattr(self, "_last_logged_pm25") or self._last_logged_pm25 != pm25:
            self._last_logged_pm25 = pm25
            self.append_log(f"Sensor Update -> PM2.5: {pm25} µg/m³, Mode: {mode}, Motor: {motor}")
