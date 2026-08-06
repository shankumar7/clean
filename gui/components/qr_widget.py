"""
PyQt component for rendering dynamic SCANNABLE QR codes with pure Python fallback & theme support.
"""

import io
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap, QImage, QColor, QPainter, QBrush, QPen
from PyQt6.QtCore import Qt
from core.qr_gen import generate_qr_matrix

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
        # Method 1: Try qrcode + Pillow package
        if QRCODE_AVAILABLE:
            try:
                qr = qrcode.QRCode(
                    version=2,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
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
                print(f"[QRCodeWidget] Standard qrcode package error: {e}. Switching to pure Python generator.")

        # Method 2: Pure Python Built-in Matrix Generator (Zero Dependencies)
        try:
            matrix = generate_qr_matrix(text)
            grid_size = len(matrix)  # 25x25
            
            # Render QR matrix directly onto QPixmap using QPainter
            pixmap = QPixmap(size, size)
            pixmap.fill(QColor("#ffffff"))
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            
            quiet_zone = 2  # 2 modules quiet zone margin
            total_modules = grid_size + (quiet_zone * 2)
            cell_size = float(size) / total_modules
            
            painter.setBrush(QBrush(QColor("#000000")))
            painter.setPen(Qt.PenStyle.NoPen)
            
            for r in range(grid_size):
                for c in range(grid_size):
                    if matrix[r][c]:
                        x = (c + quiet_zone) * cell_size
                        y = (r + quiet_zone) * cell_size
                        # Draw module square with slight overlap to prevent gaps
                        painter.drawRect(int(x), int(y), int(cell_size + 1), int(cell_size + 1))
                        
            painter.end()
            return pixmap
        except Exception as e:
            print(f"[QRCodeWidget] Pure Python QR rendering error: {e}")
            
        fallback = QPixmap(size, size)
        fallback.fill(QColor("#ffffff"))
        return fallback
