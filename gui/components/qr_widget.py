"""
PyQt component for rendering dynamic QR codes with theme support & robust fallbacks.
"""

import io
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap, QImage, QColor, QPainter, QFont, QPen, QBrush
from PyQt6.QtCore import Qt

try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False


class QRCodeWidget(QWidget):
    def __init__(self, url="http://127.0.0.1:5000", size=160, parent=None):
        super().__init__(parent)
        self.url = url
        self.qr_size = size
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(4, 4, 4, 4)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #ffffff;
                border: 3px solid #38bdf8;
                border-radius: 12px;
                padding: 6px;
            }
        """)
        
        layout.addWidget(self.image_label)
        self.set_url(self.url)

    def set_url(self, url):
        self.url = url
        pixmap = self._generate_qr_pixmap(self.url, size=self.qr_size)
        self.image_label.setPixmap(pixmap)

    def apply_theme(self, theme):
        border_color = theme["accent"]
        self.image_label.setStyleSheet(f"""
            QLabel {{
                background-color: #ffffff;
                border: 3px solid {border_color};
                border-radius: 12px;
                padding: 6px;
            }}
        """)

    def _generate_qr_pixmap(self, text, size=160):
        if QRCODE_AVAILABLE:
            try:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_M,
                    box_size=6,
                    border=2,
                )
                qr.add_data(text)
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                
                qimg = QImage()
                qimg.loadFromData(buffer.getvalue())
                pixmap = QPixmap.fromImage(qimg)
                return pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            except Exception as e:
                print(f"[QRCodeWidget] Error building QR code: {e}")
        
        # Robust QPainter fallback if qrcode package is missing or fails
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor("#ffffff"))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw decorative simulated QR position markers
        painter.setBrush(QBrush(QColor("#0f172a")))
        painter.setPen(Qt.PenStyle.NoPen)
        
        cell = size // 6
        # Top-Left finder pattern
        painter.drawRect(cell, cell, cell*2, cell*2)
        # Top-Right finder pattern
        painter.drawRect(cell*4, cell, cell*2, cell*2)
        # Bottom-Left finder pattern
        painter.drawRect(cell, cell*4, cell*2, cell*2)
        
        # Inner white cutouts
        painter.setBrush(QBrush(QColor("#ffffff")))
        painter.drawRect(cell + cell//2, cell + cell//2, cell, cell)
        painter.drawRect(cell*4 + cell//2, cell + cell//2, cell, cell)
        painter.drawRect(cell + cell//2, cell*4 + cell//2, cell, cell)
        
        # Draw URL text at center
        painter.setPen(QPen(QColor("#0284c7"), 1))
        font = QFont("Arial", 8, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "\n\nSCAN ME")
        
        painter.end()
        return pixmap
