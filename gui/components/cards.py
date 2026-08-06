"""
PyQt component widgets for touchscreen metric cards & status badges.
"""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt


class MetricCard(QFrame):
    """Card displaying a metric title, numeric value, and unit."""
    def __init__(self, title, unit="µg/m³", parent=None):
        super().__init__(parent)
        self.title_text = title
        self.unit_text = unit
        
        self.setStyleSheet("""
            MetricCard {
                background-color: rgba(30, 41, 59, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        
        self.title_lbl = QLabel(self.title_text.upper())
        self.title_lbl.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        
        self.value_lbl = QLabel("--")
        self.value_lbl.setStyleSheet("color: #ffffff; font-size: 26px; font-weight: bold;")
        
        self.unit_lbl = QLabel(self.unit_text)
        self.unit_lbl.setStyleSheet("color: #64748b; font-size: 11px;")
        
        layout.addWidget(self.title_lbl)
        
        val_layout = QHBoxLayout()
        val_layout.setContentsMargins(0, 0, 0, 0)
        val_layout.setSpacing(4)
        val_layout.addWidget(self.value_lbl)
        val_layout.addWidget(self.unit_lbl)
        val_layout.addStretch()
        
        layout.addLayout(val_layout)

    def set_value(self, val):
        self.value_lbl.setText(str(val))


class AQIBadge(QLabel):
    """Dynamic color-coded status badge."""
    def __init__(self, text="Good", color="#4CAF50", parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.set_badge(text, color)

    def set_badge(self, text, color="#4CAF50"):
        self.setText(text.upper())
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: #ffffff;
                font-size: 13px;
                font-weight: bold;
                padding: 6px 16px;
                border-radius: 14px;
                letter-spacing: 1px;
            }}
        """)
