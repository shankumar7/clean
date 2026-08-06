"""
Main PyQt6 Touchscreen Window & Tab Navigation Application (With 🌙 Dark / ☀️ Light Mode Toggle).
"""

import sys
import time
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, QTabBar, QFrame, QPushButton
)
from PyQt6.QtCore import Qt, QTimer
from gui.tabs.analysis_tab import AnalysisTab
from gui.tabs.control_tab import ControlTab
from gui.tabs.qrcode_tab import QRCodeTab
from gui.tabs.diagnostics_tab import DiagnosticsTab
from gui.theme import ThemeManager


class AirMonitorMainWindow(QMainWindow):
    def __init__(self, monitor_engine):
        super().__init__()
        self.monitor = monitor_engine
        
        self.setWindowTitle("Raspberry Pi Air Quality Monitor & Host Server")
        self.resize(800, 480)  # Standard 5" Touchscreen Resolution (800x480)
        self.setMinimumSize(480, 320)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(6, 6, 6, 6)
        self.layout.setSpacing(6)
        
        # Header Status Bar with Theme Toggle Button
        self.header = QFrame()
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(10, 4, 10, 4)
        
        self.title_lbl = QLabel("AIR MONITOR & HOST SERVER")
        self.clock_lbl = QLabel()
        self.status_indicator = QLabel("● ONLINE")
        
        # 🌙 / ☀️ Theme Toggle Button
        self.theme_btn = QPushButton("🌙 Dark")
        self.theme_btn.setMinimumHeight(28)
        self.theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_btn.clicked.connect(self._on_toggle_theme)
        
        # ❌ Exit Button
        self.exit_btn = QPushButton("❌ Exit")
        self.exit_btn.setMinimumHeight(28)
        self.exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.exit_btn.clicked.connect(self.close)
        
        header_layout.addWidget(self.title_lbl)
        header_layout.addStretch()
        header_layout.addWidget(self.theme_btn)
        header_layout.addWidget(self.exit_btn)
        header_layout.addWidget(self.status_indicator)
        header_layout.addWidget(self.clock_lbl)
        
        self.layout.addWidget(self.header)
        
        # Multi-Tab Navigation Widget
        self.tabs = QTabWidget()
        self.tabs.setTabBar(TouchTabBar())
        
        # Instantiate Tabs
        self.tab1_analysis = AnalysisTab(self.monitor)
        self.tab2_control = ControlTab(self.monitor)
        self.tab3_qrcode = QRCodeTab(self.monitor)
        self.tab4_diagnostics = DiagnosticsTab(self.monitor)
        
        self.tabs.addTab(self.tab1_analysis, "📊 Analysis")
        self.tabs.addTab(self.tab2_control, "⚙️ Controls")
        self.tabs.addTab(self.tab3_qrcode, "📲 QR Portal")
        self.tabs.addTab(self.tab4_diagnostics, "🔧 Diagnostic")
        
        self.layout.addWidget(self.tabs)
        
        # UI Refresh Timer (1 second interval)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_timer_tick)
        self.timer.start(1000)
        
        self.monitor.register_listener(self._on_state_changed)
        ThemeManager.register_listener(self.apply_theme)
        
        self.apply_theme(ThemeManager.get_theme())
        self._update_clock()

    def _on_toggle_theme(self):
        new_theme = ThemeManager.toggle_theme()
        if new_theme["mode"] == "dark":
            self.theme_btn.setText("🌙 Dark")
        else:
            self.theme_btn.setText("☀️ Light")

    def apply_theme(self, theme):
        is_dark = (theme["mode"] == "dark")
        self.theme_btn.setText("🌙 Dark" if is_dark else "☀️ Light")
        
        self.central_widget.setStyleSheet(f"background-color: {theme['bg']}; font-family: 'Outfit', sans-serif;")
        
        self.header.setStyleSheet(f"""
            QFrame {{
                background-color: {theme['header_bg']};
                border: 1px solid {theme['card_border']};
                border-radius: 10px;
            }}
        """)
        self.title_lbl.setStyleSheet(f"color: {theme['accent']}; font-size: 11px; font-weight: bold; letter-spacing: 0.5px;")
        self.clock_lbl.setStyleSheet(f"color: {theme['text_secondary']}; font-size: 11px; font-weight: bold;")
        self.status_indicator.setStyleSheet("color: #22c55e; font-size: 10px; font-weight: bold; margin-right: 8px;")
        
        self.theme_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme['tab_bg']};
                color: {theme['accent']};
                border: 1px solid {theme['accent']};
                border-radius: 6px;
                padding: 2px 8px;
                font-size: 10px;
                font-weight: bold;
            }}
        """)
        
        self.exit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme['tab_bg']};
                color: #ef4444;
                border: 1px solid #ef4444;
                border-radius: 6px;
                padding: 2px 8px;
                font-size: 10px;
                font-weight: bold;
            }}
            QPushButton:pressed {{
                background-color: #ef4444;
                color: white;
            }}
        """)
        
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {theme['card_border']};
                border-radius: 12px;
                background: {theme['card_bg']};
            }}
            QTabBar::tab {{
                background: {theme['tab_bg']};
                color: {theme['tab_text']};
                font-size: 11px;
                font-weight: bold;
                padding: 8px 12px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                min-width: 90px;
            }}
            QTabBar::tab:selected {{
                background: {theme['tab_selected_bg']};
                color: {theme['tab_selected_text']};
            }}
            QTabBar::tab:hover:!selected {{
                background: {theme['accent']};
                color: #ffffff;
            }}
        """)
        
        self.tab1_analysis.apply_theme(theme)
        self.tab2_control.apply_theme(theme)
        self.tab3_qrcode.apply_theme(theme)
        self.tab4_diagnostics.apply_theme(theme)

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
    """Custom TabBar with touch-friendly sizing."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
