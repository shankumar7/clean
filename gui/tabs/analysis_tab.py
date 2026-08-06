"""
Tab 1: Live Analysis & Air Quality Dashboard (With High-Contrast Theme Switching).
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
from PyQt6.QtCore import Qt
from gui.components.cards import MetricCard, AQIBadge
from gui.components.gauge import AQIGaugeWidget
from gui.theme import ThemeManager

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
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)
        
        # Top Row: Custom Arc Gauge + AQI Badge & Health Precautions
        self.top_frame = QFrame()
        top_layout = QHBoxLayout(self.top_frame)
        top_layout.setContentsMargins(12, 8, 12, 8)
        top_layout.setSpacing(10)
        
        # Arc Gauge Widget
        self.gauge = AQIGaugeWidget()
        top_layout.addWidget(self.gauge, stretch=0)
        
        # AQI Precaution & Status Card
        info_vbox = QVBoxLayout()
        info_vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        info_vbox.setSpacing(4)
        
        badge_hbox = QHBoxLayout()
        badge_hbox.setContentsMargins(0, 0, 0, 0)
        
        self.title_tag = QLabel("AIR QUALITY ASSESSMENT")
        badge_hbox.addWidget(self.title_tag)
        badge_hbox.addStretch()
        
        self.aqi_badge = AQIBadge("Good", "#10b981")
        badge_hbox.addWidget(self.aqi_badge)
        
        self.precaution_lbl = QLabel("Air quality is great! Safe to enjoy outdoor physical exercise.")
        self.precaution_lbl.setWordWrap(True)
        
        info_vbox.addLayout(badge_hbox)
        info_vbox.addWidget(self.precaution_lbl)
        
        top_layout.addLayout(info_vbox, stretch=1)
        main_layout.addWidget(self.top_frame)
        
        # Middle Row: Metric Cards Grid
        grid_layout = QGridLayout()
        grid_layout.setSpacing(6)
        
        self.pm1_card = MetricCard("PM 1.0", "µg/m³")
        self.pm10_card = MetricCard("PM 10", "µg/m³")
        self.mode_card = MetricCard("System Mode", "")
        self.motor_card = MetricCard("Motor Relay", "")
        
        grid_layout.addWidget(self.pm1_card, 0, 0)
        grid_layout.addWidget(self.pm10_card, 0, 1)
        grid_layout.addWidget(self.mode_card, 1, 0)
        grid_layout.addWidget(self.motor_card, 1, 1)
        
        main_layout.addLayout(grid_layout)
        
        # Bottom Row: Live Trend Chart
        self.chart_frame = QFrame()
        chart_layout = QVBoxLayout(self.chart_frame)
        chart_layout.setContentsMargins(8, 6, 8, 6)
        chart_layout.setSpacing(4)
        
        self.chart_title = QLabel("📈 REAL-TIME PARTICULATE DENSITY TREND")
        chart_layout.addWidget(self.chart_title)
        
        if PYQTGRAPH_AVAILABLE:
            self.plot_widget = pg.PlotWidget()
            self.plot_widget.showGrid(x=True, y=True, alpha=0.2)
            self.plot_widget.setYRange(0, 300)
            self.pm25_curve = self.plot_widget.plot(pen=pg.mkPen(color='#00b4d8', width=2), name="PM2.5")
            self.pm10_curve = self.plot_widget.plot(pen=pg.mkPen(color='#ec4899', width=2), name="PM10")
            chart_layout.addWidget(self.plot_widget)
        else:
            self.fallback_lbl = QLabel("Live Trend Chart")
            self.fallback_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            chart_layout.addWidget(self.fallback_lbl)

        main_layout.addWidget(self.chart_frame, stretch=1)
        
        self.apply_theme(ThemeManager.get_theme())

    def apply_theme(self, theme):
        self.gauge.apply_theme(theme)
        
        self.top_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {theme['card_bg']};
                border: 1px solid {theme['card_border']};
                border-radius: 14px;
            }}
        """)
        self.title_tag.setStyleSheet(f"color: {theme['accent']}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        self.precaution_lbl.setStyleSheet(f"color: {theme['text_primary']}; font-size: 11px; margin-top: 4px; line-height: 1.2;")
        
        self.pm1_card.apply_theme(theme)
        self.pm10_card.apply_theme(theme)
        self.mode_card.apply_theme(theme)
        self.motor_card.apply_theme(theme)
        
        self.chart_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {theme['card_bg']};
                border: 1px solid {theme['card_border']};
                border-radius: 12px;
            }}
        """)
        self.chart_title.setStyleSheet(f"color: {theme['text_secondary']}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        
        if PYQTGRAPH_AVAILABLE:
            self.plot_widget.setBackground(theme['chart_bg'])
        elif hasattr(self, "fallback_lbl"):
            self.fallback_lbl.setStyleSheet(f"color: {theme['text_secondary']}; font-size: 11px;")

    def update_ui(self, state):
        pm25 = state["pm2_5"]
        self.gauge.set_value(pm25, state.get("aqi_color", "#10b981"))
        
        self.pm1_card.set_value(state["pm1_0"])
        self.pm10_card.set_value(state["pm10"])
        
        mode_str = "MANUAL" if state["manual"] == 1 else "AUTO"
        self.mode_card.set_value(mode_str)
        
        motor_str = "ON ⚡" if state["motor"] == 1 else "OFF"
        self.motor_card.set_value(motor_str)
        
        self.aqi_badge.set_badge(state["aqi_label"], state["aqi_color"])
        self.precaution_lbl.setText(state["precaution"])
        
        if PYQTGRAPH_AVAILABLE and "history" in state:
            history = state["history"]
            if history:
                y_pm25 = [item["pm2_5"] for item in history]
                y_pm10 = [item["pm10"] for item in history]
                x = list(range(len(history)))
                self.pm25_curve.setData(x, y_pm25)
                self.pm10_curve.setData(x, y_pm10)
