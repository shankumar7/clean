"""
Tab 4: System Diagnostics, Hardware Status, Uptime Counter & Event Logs.
"""

import time
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTextEdit, QGridLayout, QPushButton
)
from PyQt6.QtCore import Qt
from gui.components.cards import MetricCard
from gui.theme import ThemeManager
import config


class DiagnosticsTab(QWidget):
    def __init__(self, monitor_engine, parent=None):
        super().__init__(parent)
        self.monitor = monitor_engine
        self.start_time = time.time()
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)
        
        # Header with Uptime counter
        top_hbox = QHBoxLayout()
        self.title_lbl = QLabel("🔧 SYSTEM DIAGNOSTICS & HARDWARE HEALTH")
        top_hbox.addWidget(self.title_lbl)
        top_hbox.addStretch()
        
        self.uptime_lbl = QLabel("Uptime: 00:00:00")
        top_hbox.addWidget(self.uptime_lbl)
        
        main_layout.addLayout(top_hbox)
        
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
        
        log_hdr = QHBoxLayout()
        self.log_title = QLabel("📜 REAL-TIME EVENT & DIAGNOSTIC LOGS")
        log_hdr.addWidget(self.log_title)
        log_hdr.addStretch()
        
        self.clear_btn = QPushButton("Clear Console")
        self.clear_btn.setMinimumHeight(24)
        self.clear_btn.clicked.connect(self.clear_logs)
        log_hdr.addWidget(self.clear_btn)
        
        log_layout.addLayout(log_hdr)
        
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        log_layout.addWidget(self.log_console, stretch=1)
        
        main_layout.addWidget(self.log_frame, stretch=1)
        
        self.apply_theme(ThemeManager.get_theme())
        
        self.append_log("System Diagnostics Initialized.", "SYSTEM")
        self.append_log(f"Listening on Host Port: {config.SERVER_PORT}", "SERVER")
        self.append_log(f"UART Serial Target: {config.DEFAULT_SERIAL_PORT}", "HARDWARE")
        self.append_log(f"GPIO Active-LOW Output Pin: {config.RELAY_GPIO_PIN}", "HARDWARE")

    def clear_logs(self):
        self.log_console.clear()
        self.append_log("Log console cleared.", "SYSTEM")

    def apply_theme(self, theme):
        self.title_lbl.setStyleSheet(f"color: {theme['accent']}; font-size: 11px; font-weight: bold; letter-spacing: 0.5px;")
        self.uptime_lbl.setStyleSheet(f"color: {theme['text_secondary']}; font-size: 10px; font-weight: bold;")
        
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
        self.clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme['tab_bg']};
                color: {theme['text_secondary']};
                border: 1px solid {theme['card_border']};
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 9px;
                font-weight: bold;
            }}
        """)
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

    def append_log(self, text, tag="INFO"):
        timestamp = time.strftime("[%H:%M:%S]")
        self.log_console.append(f"{timestamp} [{tag}] {text}")

    def update_ui(self, state):
        # Update uptime counter
        elapsed = int(time.time() - self.start_time)
        hrs, rem = divmod(elapsed, 3600)
        mins, secs = divmod(rem, 60)
        self.uptime_lbl.setText(f"Uptime: {hrs:02d}:{mins:02d}:{secs:02d}")
        
        pm25 = state["pm2_5"]
        motor = "ON" if state["motor"] == 1 else "OFF"
        mode = "MANUAL" if state["manual"] == 1 else "AUTO"
        
        if not hasattr(self, "_last_logged_pm25") or self._last_logged_pm25 != pm25:
            self._last_logged_pm25 = pm25
            self.append_log(f"PM2.5: {pm25} µg/m³, Mode: {mode}, Motor: {motor}", "SENSOR")
