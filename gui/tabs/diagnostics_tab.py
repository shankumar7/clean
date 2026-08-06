"""
Tab 4: System Diagnostics, Hardware Status & Event Logs (With Theme Support).
"""

import time
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTextEdit, QGridLayout
)
from PyQt6.QtCore import Qt
from gui.components.cards import MetricCard
from gui.theme import ThemeManager
import config


class DiagnosticsTab(QWidget):
    def __init__(self, monitor_engine, parent=None):
        super().__init__(parent)
        self.monitor = monitor_engine
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)
        
        # Title
        self.title_lbl = QLabel("SYSTEM DIAGNOSTICS & LOGS")
        main_layout.addWidget(self.title_lbl)
        
        # Grid of hardware status cards
        grid_layout = QGridLayout()
        grid_layout.setSpacing(6)
        
        self.card_serial = MetricCard("PMS5003 UART", "")
        self.card_serial.set_value(config.DEFAULT_SERIAL_PORT)
        
        self.card_gpio = MetricCard("GPIO Relay Pin", "")
        self.card_gpio.set_value(f"GPIO {config.RELAY_GPIO_PIN}")
        
        self.card_port = MetricCard("Web Server Port", "")
        self.card_port.set_value(str(config.SERVER_PORT))
        
        self.card_status = MetricCard("System Engine", "")
        self.card_status.set_value("RUNNING")
        
        grid_layout.addWidget(self.card_serial, 0, 0)
        grid_layout.addWidget(self.card_gpio, 0, 1)
        grid_layout.addWidget(self.card_port, 1, 0)
        grid_layout.addWidget(self.card_status, 1, 1)
        
        main_layout.addLayout(grid_layout)
        
        # Live Activity Log Console Box
        self.log_frame = QFrame()
        log_layout = QVBoxLayout(self.log_frame)
        log_layout.setContentsMargins(10, 8, 10, 8)
        log_layout.setSpacing(4)
        
        self.log_title = QLabel("REAL-TIME SYSTEM ACTIVITY LOG")
        log_layout.addWidget(self.log_title)
        
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        log_layout.addWidget(self.log_console, stretch=1)
        
        main_layout.addWidget(self.log_frame, stretch=1)
        
        self.apply_theme(ThemeManager.get_theme())
        
        self.append_log("System Diagnostics Initialized.")
        self.append_log(f"Listening on Host Port: {config.SERVER_PORT}")
        self.append_log(f"UART Serial Target: {config.DEFAULT_SERIAL_PORT}")
        self.append_log(f"GPIO Active-LOW Output Pin: {config.RELAY_GPIO_PIN}")

    def apply_theme(self, theme):
        self.title_lbl.setStyleSheet(f"color: {theme['accent']}; font-size: 11px; font-weight: bold; letter-spacing: 0.5px;")
        
        self.card_serial.apply_theme(theme)
        self.card_gpio.apply_theme(theme)
        self.card_port.apply_theme(theme)
        self.card_status.apply_theme(theme)
        
        self.log_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {theme['card_bg']};
                border: 1px solid {theme['card_border']};
                border-radius: 12px;
            }}
        """)
        self.log_title.setStyleSheet(f"color: {theme['text_secondary']}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        self.log_console.setStyleSheet(f"""
            QTextEdit {{
                background-color: {theme['log_bg']};
                color: {theme['log_text']};
                font-family: 'Courier New', monospace;
                font-size: 11px;
                border: 1px solid {theme['card_border']};
                border-radius: 6px;
                padding: 6px;
            }}
        """)

    def append_log(self, text):
        timestamp = time.strftime("[%H:%M:%S]")
        self.log_console.append(f"{timestamp} {text}")

    def update_ui(self, state):
        pm25 = state["pm2_5"]
        motor = "ON" if state["motor"] == 1 else "OFF"
        mode = "MANUAL" if state["manual"] == 1 else "AUTO"
        
        if not hasattr(self, "_last_logged_pm25") or self._last_logged_pm25 != pm25:
            self._last_logged_pm25 = pm25
            self.append_log(f"Update -> PM2.5: {pm25} µg/m³, Mode: {mode}, Motor: {motor}")
