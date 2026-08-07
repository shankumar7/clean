import qrcode
qr = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_L, border=0)
qr.add_data("http://172.29.98.183:5000")
qr.make(fit=True)
m = qr.modules
print("qrcode module:")
print("(0,8) =", m[0][8])
print("(8,0) =", m[8][0])

from core.qr_gen import generate_qr_matrix
m2 = generate_qr_matrix("http://172.29.98.183:5000")
print("custom module:")
print("(0,8) =", m2[0][8])
print("(8,0) =", m2[8][0])
