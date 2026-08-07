import sys
sys.path.insert(0, '.')

# Check what's available
try:
    import qrcode
    print("✅ qrcode library available")
except ImportError:
    print("❌ qrcode library NOT available")

try:
    from PIL import Image
    print("✅ Pillow available")
except ImportError:
    print("❌ Pillow NOT available")

# Generate QR with the qrcode library
import qrcode
url = "http://172.29.98.183:5000"
qr = qrcode.QRCode(
    version=2,
    error_correction=qrcode.constants.ERROR_CORRECT_M,
    box_size=10,
    border=4,
)
qr.add_data(url)
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="white")
img.save("qr_library_test.png")
print(f"✅ Saved qr_library_test.png ({img.size[0]}x{img.size[1]})")

# Decode it back with cv2
try:
    import cv2
    cv_img = cv2.imread('qr_library_test.png')
    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(cv_img)
    print(f"✅ cv2 decoded: '{data}'")
except Exception as e:
    print(f"❌ cv2 decode failed: {e}")

# Now test what the widget actually does - simulate the render pipeline
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPixmap, QImage, QColor
from PyQt6.QtCore import Qt

app = QApplication(sys.argv)

# Exactly replicate what qr_widget does now
qr2 = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_L, border=0)
qr2.add_data(url)
qr2.make(fit=True)
matrix = qr2.modules
grid_size = len(matrix)
quiet_zone = 4
total_modules = grid_size + (quiet_zone * 2)
size = 160

print(f"Grid: {grid_size}x{grid_size}, total_modules: {total_modules}, target size: {size}")

img2 = QImage(total_modules, total_modules, QImage.Format.Format_RGB32)
img2.fill(QColor("#ffffff"))
for r in range(grid_size):
    for c in range(len(matrix[r])):
        if matrix[r][c]:
            img2.setPixelColor(c + quiet_zone, r + quiet_zone, QColor("#000000"))

pixmap = QPixmap.fromImage(img2).scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
pixmap.save("qr_widget_simulated.png")
print(f"✅ Saved qr_widget_simulated.png ({pixmap.width()}x{pixmap.height()})")

# Decode the widget output
try:
    cv_img2 = cv2.imread('qr_widget_simulated.png')
    data2, bbox2, _ = detector.detectAndDecode(cv_img2)
    print(f"Widget QR cv2 decoded: '{data2}'")
except Exception as e:
    print(f"❌ Widget QR cv2 decode failed: {e}")

# Also test with larger size
pixmap_large = QPixmap.fromImage(img2).scaled(330, 330, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
pixmap_large.save("qr_widget_large.png")
try:
    cv_img3 = cv2.imread('qr_widget_large.png')
    data3, bbox3, _ = detector.detectAndDecode(cv_img3)
    print(f"Widget QR LARGE cv2 decoded: '{data3}'")
except Exception as e:
    print(f"❌ Widget QR LARGE cv2 decode failed: {e}")
