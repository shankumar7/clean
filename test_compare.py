import qrcode
from core.qr_gen import generate_qr_matrix

url = "http://172.29.98.183:5000"

qr = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_L, border=0)
qr.add_data(url)
qr.make(fit=True)
matrix_qrcode = qr.modules

matrix_custom = generate_qr_matrix(url)

diff = 0
if len(matrix_qrcode) == len(matrix_custom):
    for i in range(len(matrix_qrcode)):
        for j in range(len(matrix_qrcode[0])):
            if matrix_qrcode[i][j] != matrix_custom[i][j]:
                diff += 1
print(f"Matrix size qrcode: {len(matrix_qrcode)}x{len(matrix_qrcode[0])}")
print(f"Matrix size custom: {len(matrix_custom)}x{len(matrix_custom[0])}")
print(f"Differences: {diff}")
