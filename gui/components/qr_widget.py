"""
PyQt component for rendering dynamic SCANNABLE QR codes with pure Python fallback & theme support.
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
    def __init__(self, url="http://127.0.0.1:5000", size=200, parent=None):
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
                padding: 8px;
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
                padding: 8px;
            }}
        """)

    def _generate_qr_pixmap(self, text, size=200):
        """Generate QR code using the qrcode library's own PIL renderer (proven scannable)."""
        if QRCODE_AVAILABLE:
            try:
                qr = qrcode.QRCode(
                    version=2,
                    error_correction=qrcode.constants.ERROR_CORRECT_M,
                    box_size=10,
                    border=4,
                )
                qr.add_data(text)
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                
                qimg = QImage()
                qimg.loadFromData(buffer.getvalue())
                pixmap = QPixmap.fromImage(qimg)
                return pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
            except Exception as e:
                print(f"[QRCodeWidget] qrcode library error: {e}. Using fallback.")

        # Fallback: pure Python generator
        try:
            from core.qr_gen import generate_qr_matrix
            matrix = generate_qr_matrix(text)
            grid_size = len(matrix)
            quiet_zone = 4
            total_modules = grid_size + (quiet_zone * 2)
            
            img = QImage(total_modules, total_modules, QImage.Format.Format_RGB32)
            img.fill(QColor("#ffffff"))
            
            for r in range(grid_size):
                for c in range(len(matrix[r])):
                    if matrix[r][c]:
                        img.setPixelColor(c + quiet_zone, r + quiet_zone, QColor("#000000"))
                        
            return QPixmap.fromImage(img).scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
        except Exception as e:
            print(f"[QRCodeWidget] Fallback QR error: {e}")
            
        fallback = QPixmap(size, size)
        fallback.fill(QColor("#ffffff"))
        return fallback

