"""
Custom QPainter AQI Arc & Progress Gauge Widget with Theme Support.
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtCore import Qt, QRectF
from gui.theme import ThemeManager


class AQIGaugeWidget(QWidget):
    """Arc gauge representing PM2.5 air quality level with theme-aware text contrast."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.max_value = 300
        self.gauge_color = QColor("#10b981")
        self.text_color = QColor("#ffffff")
        self.setMinimumSize(90, 90)
        
        self.apply_theme(ThemeManager.get_theme())

    def apply_theme(self, theme):
        self.text_color = QColor(theme["text_primary"])
        self.update()

    def set_value(self, val, color_hex="#10b981"):
        self.value = max(0, min(self.max_value, val))
        self.gauge_color = QColor(color_hex)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        side = min(width, height) - 10

        x = (width - side) / 2
        y = (height - side) / 2
        rect = QRectF(x, y, side, side)

        # Background track arc
        pen_bg = QPen(QColor(128, 128, 128, 60), 8)
        pen_bg.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_bg)

        # 240-degree arc starting from 210 degrees
        start_angle = 210 * 16
        span_angle = -240 * 16
        painter.drawArc(rect, start_angle, span_angle)

        # Active progress arc
        if self.value > 0:
            fill_fraction = min(1.0, self.value / float(self.max_value))
            active_span = int(-240 * 16 * fill_fraction)

            pen_active = QPen(self.gauge_color, 8)
            pen_active.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen_active)
            painter.drawArc(rect, start_angle, active_span)

        # Center text with theme-aware text color
        painter.setPen(self.text_color)
        
        font_label = QFont("Outfit", 10, QFont.Weight.Bold)
        painter.setFont(font_label)
        rect_label = QRectF(x, y + side * 0.25, side, side * 0.2)
        painter.drawText(rect_label, Qt.AlignmentFlag.AlignCenter, "PM 2.5")
        
        font_value = QFont("Outfit", 18, QFont.Weight.Bold)
        painter.setFont(font_value)
        rect_value = QRectF(x, y + side * 0.42, side, side * 0.2)
        painter.drawText(rect_value, Qt.AlignmentFlag.AlignCenter, str(self.value))
        
        font_unit = QFont("Outfit", 9, QFont.Weight.Normal)
        painter.setFont(font_unit)
        rect_unit = QRectF(x, y + side * 0.62, side, side * 0.2)
        painter.drawText(rect_unit, Qt.AlignmentFlag.AlignCenter, "µg/m³")

        painter.end()
