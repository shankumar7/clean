"""
PyQt component for rendering dynamic SCANNABLE QR codes with theme support.
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
                padding: 4px;
            }
        """)
        
        layout.addWidget(self.image_label)
        self.set_url(self.url)

    def set_url(self, url):
        self.url = url
        pixmap = self._generate_qr_pixmap(self.url)
        self.image_label.setPixmap(pixmap)

    def apply_theme(self, theme):
        border_color = theme["accent"]
        self.image_label.setStyleSheet(f"""
            QLabel {{
                background-color: #ffffff;
                border: 3px solid {border_color};
                padding: 4px;
            }}
        """)

    def _generate_qr_pixmap(self, text):
        """Generate QR code using the qrcode library's PIL renderer."""
        if QRCODE_AVAILABLE:
            try:
                qr = qrcode.QRCode(
                    version=2,
                    error_correction=qrcode.constants.ERROR_CORRECT_H,
                    box_size=6,
                    border=4,
                )
                qr.add_data(text)
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                
                qimg = QImage()
                qimg.loadFromData(buffer.getvalue())
                return QPixmap.fromImage(qimg)
            except Exception as e:
                print(f"[QRCodeWidget] qrcode library error: {e}")

        # Fallback: simple placeholder
        fallback = QPixmap(160, 160)
        fallback.fill(QColor("#ffffff"))
        return fallback
