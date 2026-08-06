"""
PyQt component for rendering dynamic QR codes (Optimized for 5" displays).
"""

import io
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap, QImage, QColor
from PyQt6.QtCore import Qt

try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False


class QRCodeWidget(QWidget):
    def __init__(self, url="http://127.0.0.1:5000", parent=None):
        super().__init__(parent)
        self.url = url
        
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
        pixmap = self._generate_qr_pixmap(self.url)
        self.image_label.setPixmap(pixmap)

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
                print(f"[QRCodeWidget] Failed to generate QR code: {e}")
        
        fallback_pixmap = QPixmap(size, size)
        fallback_pixmap.fill(QColor("#ffffff"))
        return fallback_pixmap
