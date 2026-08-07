import qrcode
import pyzbar.pyzbar as pyzbar
from PIL import Image

def test_qr(url):
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=6,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("test.png")
    
    decoded = pyzbar.decode(Image.open("test.png"))
    print(f"qrcode package decoded: {[d.data.decode() for d in decoded]}")

test_qr("http://172.29.98.183:5000")
