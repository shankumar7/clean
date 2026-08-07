import qrcode
qr = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_L, border=2)
qr.add_data("http://172.29.98.183:5000")
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="white")
img.save("test_qr_standard.png")

import cv2
img2 = cv2.imread('test_qr_standard.png')
detector = cv2.QRCodeDetector()
data, bbox, straight_qrcode = detector.detectAndDecode(img2)
print('Standard Decoded data:', data)
