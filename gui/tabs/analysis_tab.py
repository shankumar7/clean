"""
Tab 1: Live Analysis & Air Quality Dashboard.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
from PyQt6.QtCore import Qt
from gui.components.cards import MetricCard, AQIBadge

try:
    import pyqtgraph as pg
    PYQTGRAPH_AVAILABLE = True
except ImportError:
    PYQTGRAPH_AVAILABLE = False


class AnalysisTab(QWidget):
    def __init__(self, monitor_engine, parent=None):
        super().__init__(parent)
        self.monitor = monitor_engine
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        
        # Top Row: Hero PM2.5 Card + AQI Badge & Precautions
        top_frame = QFrame()
        top_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 41, 59, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 20px;
            }
        """)
        top_layout = QHBoxLayout(top_frame)
        top_layout.setContentsMargins(20, 16, 20, 16)
        
        # Hero Value PM2.5
        pm25_vbox = QVBoxLayout()
        pm25_label = QLabel("PM 2.5 MAIN READOUT")
        pm25_label.setStyleSheet("color: #38bdf8; font-size: 12px; font-weight: bold; letter-spacing: 1px;")
        
        self.pm25_num = QLabel("--")
        self.pm25_num.setStyleSheet("color: #ffffff; font-size: 52px; font-weight: bold;")
        
        pm25_unit = QLabel("µg/m³ (Fine Particulate)")
        pm25_unit.setStyleSheet("color: #94a3b8; font-size: 12px;")
        
        pm25_vbox.addWidget(pm25_label)
        pm25_vbox.addWidget(self.pm25_num)
        pm25_vbox.addWidget(pm25_unit)
        
        top_layout.addLayout(pm25_vbox, stretch=4)
        
        # AQI Precaution & Status Card
        info_vbox = QVBoxLayout()
        info_vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        badge_hbox = QHBoxLayout()
        badge_hbox.setContentsMargins(0, 0, 0, 0)
        self.aqi_badge = AQIBadge("Good", "#4CAF50")
        badge_hbox.addWidget(self.aqi_badge)
        badge_hbox.addStretch()
        
        self.precaution_lbl = QLabel("Air quality is great! Safe to enjoy outdoor physical exercise.")
        self.precaution_lbl.setWordWrap(True)
        self.precaution_lbl.setStyleSheet("color: #e2e8f0; font-size: 13px; margin-top: 8px; line-height: 1.4;")
        
        info_vbox.addLayout(badge_hbox)
        info_vbox.addWidget(self.precaution_lbl)
        
        top_layout.addLayout(info_vbox, stretch=6)
        main_layout.addWidget(top_frame)
        
        # Middle Row: Metric Cards Grid (PM1.0, PM10, System Mode, Motor Status)
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)
        
        self.pm1_card = MetricCard("PM 1.0", "µg/m³")
        self.pm10_card = MetricCard("PM 10", "µg/m³")
        self.mode_card = MetricCard("System Mode", "")
        self.motor_card = MetricCard("Motor Relay", "")
        
        grid_layout.addWidget(self.pm1_card, 0, 0)
        grid_layout.addWidget(self.pm10_card, 0, 1)
        grid_layout.addWidget(self.mode_card, 0, 2)
        grid_layout.addWidget(self.motor_card, 0, 3)
        
        main_layout.addLayout(grid_layout)
        
        # Bottom Row: Real-time Live Trend Chart
        chart_frame = QFrame()
        chart_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(15, 23, 42, 0.8);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px;
            }
        """)
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(12, 10, 12, 10)
        
        chart_title = QLabel("REAL-TIME PARTICULATE CONCENTRATION TREND")
        chart_title.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        chart_layout.addWidget(chart_title)
        
        if PYQTGRAPH_AVAILABLE:
            pg.setConfigOption('background', '#0f172a')
            pg.setConfigOption('foreground', '#94a3b8')
            self.plot_widget = pg.PlotWidget()
            self.plot_widget.showGrid(x=True, y=True, alpha=0.2)
            self.plot_widget.setYRange(0, 300)
            self.pm25_curve = self.plot_widget.plot(pen=pg.mkPen(color='#38bdf8', width=3), name="PM2.5")
            self.pm10_curve = self.plot_widget.plot(pen=pg.mkPen(color='#ec4899', width=2), name="PM10")
            chart_layout.addWidget(self.plot_widget)
        else:
            fallback_lbl = QLabel("Live Trend Chart (PyQtGraph module not installed)")
            fallback_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            fallback_lbl.setStyleSheet("color: #64748b; font-size: 13px;")
            chart_layout.addWidget(fallback_lbl)

        main_layout.addWidget(chart_frame, stretch=1)

    def update_ui(self, state):
        self.pm25_num.setText(str(state["pm2_5"]))
        self.pm1_card.set_value(state["pm1_0"])
        self.pm10_card.set_value(state["pm10"])
        
        mode_str = "MANUAL" if state["manual"] == 1 else "AUTO"
        self.mode_card.set_value(mode_str)
        
        motor_str = "ON" if state["motor"] == 1 else "OFF"
        self.motor_card.set_value(motor_str)
        
        self.aqi_badge.set_badge(state["aqi_label"], state["aqi_color"])
        self.precaution_lbl.setText(state["precaution"])
        
        # Update trend plot curve
        if PYQTGRAPH_AVAILABLE and "history" in state:
            history = state["history"]
            if history:
                y_pm25 = [item["pm2_5"] for item in history]
                y_pm10 = [item["pm10"] for item in history]
                x = list(range(len(history)))
                self.pm25_curve.setData(x, y_pm25)
                self.pm10_curve.setData(x, y_pm10)
