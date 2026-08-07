import qrcode
qr = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_L, border=0)
qr.add_data("http://172.29.98.183:5000")
qr.make(fit=True)
print(len(qr.modules))
