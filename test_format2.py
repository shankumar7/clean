import qrcode
qr = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_L, border=0)
qr.add_data("http://172.29.98.183:5000")
qr.make(fit=True)
m = qr.modules
size = len(m)
# Let's dump the format bits for the first 15 bits
# Top-left copy
coords1 = [
    (0,8), (1,8), (2,8), (3,8), (4,8), (5,8), (7,8), (8,8),
    (8,7), (8,5), (8,4), (8,3), (8,2), (8,1), (8,0)
]
print("qrcode top-left format bits:")
for r, c in coords1:
    print(int(m[r][c]), end="")
print()

coords2 = [
    (8,size-1), (8,size-2), (8,size-3), (8,size-4), (8,size-5), (8,size-6), (8,size-7),
    (size-7,8), (size-6,8), (size-5,8), (size-4,8), (size-3,8), (size-2,8), (size-1,8), (size-1, 8) # wait, what is the last one?
]
# Let's just find the last 7 bits in the bottom-left
print("qrcode bottom-left (last 7 bits):")
for r in range(size-7, size):
    print(int(m[r][8]), end="")
print()
print("qrcode top-right (first 8 bits):")
for c in range(size-8, size):
    print(int(m[8][c]), end="")
print()
