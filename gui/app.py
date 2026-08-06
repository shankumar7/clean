"""
Main PyQt6 Touchscreen Window & Tab Navigation Application (Optimized for 5" Displays).
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
        self.resize(800, 480)  # Standard 5" Touchscreen Resolution (800x480)
        self.setMinimumSize(480, 320)  # Compact 5" SPI fallback (480x320)
        
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #0f172a; font-family: 'Outfit', sans-serif;")
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)
        
        # Header Status Bar (Compact for 5" Screen)
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 41, 59, 0.9);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 4, 10, 4)
        
        title_lbl = QLabel("AIR MONITOR & HOST SERVER")
        title_lbl.setStyleSheet("color: #38bdf8; font-size: 11px; font-weight: bold; letter-spacing: 0.5px;")
        
        self.clock_lbl = QLabel()
        self.clock_lbl.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: bold;")
        
        status_indicator = QLabel("● ONLINE")
        status_indicator.setStyleSheet("color: #22c55e; font-size: 10px; font-weight: bold; margin-right: 8px;")
        
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        header_layout.addWidget(status_indicator)
        header_layout.addWidget(self.clock_lbl)
        
        layout.addWidget(header)
        
        # Multi-Tab Navigation Widget (Compact Touch Styling)
        self.tabs = QTabWidget()
        self.tabs.setTabBar(TouchTabBar())
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                background: rgba(15, 23, 42, 0.6);
            }
            QTabBar::tab {
                background: #1e293b;
                color: #94a3b8;
                font-size: 11px;
                font-weight: bold;
                padding: 8px 12px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                min-width: 90px;
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
        
        self.tabs.addTab(self.tab1_analysis, "📊 Analysis")
        self.tabs.addTab(self.tab2_control, "⚙️ Controls")
        self.tabs.addTab(self.tab3_qrcode, "📲 QR Portal")
        self.tabs.addTab(self.tab4_diagnostics, "🔧 Diagnostic")
        
        layout.addWidget(self.tabs)
        
        # UI Refresh Timer (1 second interval)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_timer_tick)
        self.timer.start(1000)
        
        self.monitor.register_listener(self._on_state_changed)
        self._update_clock()

    def _on_timer_tick(self):
        self._update_clock()
        state = self.monitor.get_state_dict()
        self._on_state_changed(state)

    def _update_clock(self):
        self.clock_lbl.setText(time.strftime("%H:%M:%S"))

    def _on_state_changed(self, state):
        self.tab1_analysis.update_ui(state)
        self.tab2_control.update_ui(state)
        self.tab3_qrcode.update_ui(state)
        self.tab4_diagnostics.update_ui(state)


class TouchTabBar(QTabBar):
    """Custom TabBar with touch-friendly sizing for 5-inch screens."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
