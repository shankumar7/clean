"""
Main PyQt6 Touchscreen Window & Tab Navigation Application.
"""

import sys
import time
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, QTabBar, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from gui.tabs.analysis_tab import AnalysisTab
from gui.tabs.control_tab import ControlTab
from gui.tabs.qrcode_tab import QRCodeTab
from gui.tabs.diagnostics_tab import DiagnosticsTab


class AirMonitorMainWindow(QMainWindow):
    def __init__(self, monitor_engine):
        super().__init__()
        self.monitor = monitor_engine
        
        self.setWindowTitle("Raspberry Pi Air Quality Monitor & Host Server")
        self.resize(800, 480)  # Standard 7" Raspberry Pi Touchscreen Resolution
        self.setMinimumSize(720, 440)
        
        # Main central container widget
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #0f172a; font-family: 'Outfit', sans-serif;")
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)
        
        # Header Status Bar
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 41, 59, 0.9);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 14px;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 8, 16, 8)
        
        title_lbl = QLabel("AIR QUALITY MONITORING & HOST SERVER")
        title_lbl.setStyleSheet("color: #38bdf8; font-size: 14px; font-weight: bold; letter-spacing: 1px;")
        
        self.clock_lbl = QLabel()
        self.clock_lbl.setStyleSheet("color: #94a3b8; font-size: 13px; font-weight: bold;")
        
        status_indicator = QLabel("● SERVER ONLINE")
        status_indicator.setStyleSheet("color: #22c55e; font-size: 12px; font-weight: bold; margin-right: 12px;")
        
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        header_layout.addWidget(status_indicator)
        header_layout.addWidget(self.clock_lbl)
        
        layout.addWidget(header)
        
        # Multi-Tab Navigation Widget
        self.tabs = QTabWidget()
        self.tabs.setTabBar(TouchTabBar())
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                background: rgba(15, 23, 42, 0.6);
            }
            QTabBar::tab {
                background: #1e293b;
                color: #94a3b8;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
                margin-right: 6px;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                min-width: 140px;
            }
            QTabBar::tab:selected {
                background: #38bdf8;
                color: #0f172a;
            }
            QTabBar::tab:hover:!selected {
                background: #334155;
                color: #ffffff;
            }
        """)
        
        # Instantiate Tabs
        self.tab1_analysis = AnalysisTab(self.monitor)
        self.tab2_control = ControlTab(self.monitor)
        self.tab3_qrcode = QRCodeTab(self.monitor)
        self.tab4_diagnostics = DiagnosticsTab(self.monitor)
        
        self.tabs.addTab(self.tab1_analysis, "📊 Live Analysis")
        self.tabs.addTab(self.tab2_control, "⚙️ System Controls")
        self.tabs.addTab(self.tab3_qrcode, "📲 QR Code Portal")
        self.tabs.addTab(self.tab4_diagnostics, "🔧 Diagnostics")
        
        layout.addWidget(self.tabs)
        
        # UI Refresh Timer (1 second interval)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_timer_tick)
        self.timer.start(1000)
        
        # Register monitor callback
        self.monitor.register_listener(self._on_state_changed)
        self._update_clock()

    def _on_timer_tick(self):
        self._update_clock()
        state = self.monitor.get_state_dict()
        self._on_state_changed(state)

    def _update_clock(self):
        self.clock_lbl.setText(time.strftime("%Y-%m-%d  %H:%M:%S"))

    def _on_state_changed(self, state):
        self.tab1_analysis.update_ui(state)
        self.tab2_control.update_ui(state)
        self.tab3_qrcode.update_ui(state)
        self.tab4_diagnostics.update_ui(state)


class TouchTabBar(QTabBar):
    """Custom TabBar with touch-friendly sizing."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
