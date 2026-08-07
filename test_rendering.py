from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPixmap, QColor, QPainter, QBrush, QImage
from PyQt6.QtCore import Qt
import sys

app = QApplication(sys.argv)

size = 160
grid_size = 25
quiet_zone = 4
total_modules = grid_size + (quiet_zone * 2)

# Method A: Manual int(x)
pixmap_a = QPixmap(size, size)
pixmap_a.fill(QColor("#ffffff"))
painter = QPainter(pixmap_a)
painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
cell_size = float(size) / total_modules
painter.setBrush(QBrush(QColor("#000000")))
painter.setPen(Qt.PenStyle.NoPen)
for r in range(grid_size):
    for c in range(grid_size):
        if (r + c) % 2 == 0:  # Checkered pattern to see grid
            x = (c + quiet_zone) * cell_size
            y = (r + quiet_zone) * cell_size
            painter.drawRect(int(x), int(y), int(cell_size + 1.5), int(cell_size + 1.5))
painter.end()
pixmap_a.save("test_a_manual.png")

# Method B: QImage scaled
img = QImage(total_modules, total_modules, QImage.Format.Format_Mono)
img.fill(1) # 1 is usually white in Mono, let's use Format_RGB32 to be safe
img = QImage(total_modules, total_modules, QImage.Format.Format_RGB32)
img.fill(QColor("#ffffff"))
for r in range(grid_size):
    for c in range(grid_size):
        if (r + c) % 2 == 0:
            img.setPixelColor(c + quiet_zone, r + quiet_zone, QColor("#000000"))
pixmap_b = QPixmap.fromImage(img).scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
pixmap_b.save("test_b_scaled.png")
