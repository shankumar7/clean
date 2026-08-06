"""
PyQt component widgets for touchscreen metric cards & status badges with icons & theme support.
"""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from gui.theme import ThemeManager

ICONS = {
    "PM 1.0": "🌬️",
    "PM 10": "💨",
    "System Mode": "⚙️",
    "Motor Relay": "⚡",
    "PMS5003 UART": "🔌",
    "GPIO Relay Pin": "📌",
    "Web Server Port": "🌐",
    "System Engine": "🚀"
}


class MetricCard(QFrame):
    """Compact glassmorphism card displaying metric icon, title, numeric value, and unit."""
    def __init__(self, title, unit="µg/m³", parent=None):
        super().__init__(parent)
        self.title_text = title
        self.unit_text = unit
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(2)
        
        icon_symbol = ICONS.get(self.title_text, "📊")
        self.title_lbl = QLabel(f"{icon_symbol} {self.title_text.upper()}")
        self.value_lbl = QLabel("--")
        self.unit_lbl = QLabel(self.unit_text)
        
        layout.addWidget(self.title_lbl)
        
        val_layout = QHBoxLayout()
        val_layout.setContentsMargins(0, 0, 0, 0)
        val_layout.setSpacing(4)
        val_layout.addWidget(self.value_lbl)
        val_layout.addWidget(self.unit_lbl)
        val_layout.addStretch()
        
        layout.addLayout(val_layout)
        
        self.apply_theme(ThemeManager.get_theme())

    def set_value(self, val):
        self.value_lbl.setText(str(val))

    def apply_theme(self, theme):
        self.setStyleSheet(f"""
            MetricCard {{
                background-color: {theme['card_bg']};
                border: 1px solid {theme['card_border']};
                border-radius: 12px;
            }}
        """)
        self.title_lbl.setStyleSheet(f"color: {theme['accent']}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        self.value_lbl.setStyleSheet(f"color: {theme['text_primary']}; font-size: 20px; font-weight: bold;")
        self.unit_lbl.setStyleSheet(f"color: {theme['text_secondary']}; font-size: 10px;")


class AQIBadge(QLabel):
    """Dynamic color-coded status badge with glow for 5" screens."""
    def __init__(self, text="Good", color="#10b981", parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.set_badge(text, color)

    def set_badge(self, text, color="#10b981"):
        self.setText(text.upper())
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: #ffffff;
                font-size: 11px;
                font-weight: bold;
                padding: 4px 14px;
                border-radius: 12px;
                letter-spacing: 0.5px;
            }}
        """)
