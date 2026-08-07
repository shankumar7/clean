import sys
sys.path.append('.')
import qrcode
from PIL import Image

# Re-implement generate_qr_matrix with corrected parameters
def generate_qr_matrix_fixed(text):
    data_bytes = text.encode('utf-8')
    if len(data_bytes) > 32:
        data_bytes = data_bytes[:32]
        
    ver = 2
    size = 25
    data_cap = 34
    ecc_len = 10
    
    bits = []
    def add_bits(val, length):
        for i in range(length - 1, -1, -1):
            bits.append((val >> i) & 1)

    add_bits(0b0100, 4)
    add_bits(len(data_bytes), 8)
    for b in data_bytes:
        add_bits(b, 8)
    add_bits(0, min(4, data_cap * 8 - len(bits)))
    while len(bits) % 8 != 0:
        bits.append(0)
    pad_bytes = [0xEC, 0x11]
    pad_idx = 0
    while len(bits) < data_cap * 8:
        add_bits(pad_bytes[pad_idx], 8)
        pad_idx = (pad_idx + 1) % 2

    data_codewords = []
    for i in range(0, len(bits), 8):
        byte_val = 0
        for b in bits[i:i+8]:
            byte_val = (byte_val << 1) | b
        data_codewords.append(byte_val)

    from core.qr_gen import rs_encode
    ecc_codewords = rs_encode(data_codewords, ecc_len)
    all_codewords = data_codewords + ecc_codewords

    matrix = [[None] * size for _ in range(size)]
    is_reserved = [[False] * size for _ in range(size)]

    def set_module(r, c, val, reserved=True):
        matrix[r][c] = val
        if reserved:
            is_reserved[r][c] = True

    def draw_finder(row, col):
        for r in range(7):
            for c in range(7):
                is_black = (r in (0, 6) or c in (0, 6) or (2 <= r <= 4 and 2 <= c <= 4))
                set_module(row + r, col + c, is_black)

    draw_finder(0, 0)
    draw_finder(0, size - 7)
    draw_finder(size - 7, 0)

    def draw_separator(r, c):
        if 0 <= r < size and 0 <= c < size and matrix[r][c] is None:
            set_module(r, c, False)

    for i in range(8):
        draw_separator(7, i)
        draw_separator(i, 7)
        draw_separator(7, size - 1 - i)
        draw_separator(i, size - 8)
        draw_separator(size - 8, i)
        draw_separator(size - 1 - i, 7)

    align_r, align_c = 18, 18
    for r in range(-2, 3):
        for c in range(-2, 3):
            is_black = (abs(r) == 2 or abs(c) == 2 or (r == 0 and c == 0))
            set_module(align_r + r, align_c + c, is_black)

    for i in range(size):
        if matrix[6][i] is None:
            set_module(6, i, (i % 2 == 0))
        if matrix[i][6] is None:
            set_module(i, 6, (i % 2 == 0))

    set_module(size - 8, 8, True)
    for i in range(9):
        if matrix[8][i] is None: set_module(8, i, False)
        if matrix[i][8] is None: set_module(i, 8, False)
    for i in range(8):
        if matrix[8][size - 1 - i] is None: set_module(8, size - 1 - i, False)
        if matrix[size - 1 - i][8] is None: set_module(size - 1 - i, 8, False)

    all_bits = []
    for cw in all_codewords:
        for b in range(7, -1, -1):
            all_bits.append((cw >> b) & 1)

    bit_idx = 0
    col = size - 1
    upward = True

    while col > 0:
        if col == 6:
            col -= 1
        rows = range(size - 1, -1, -1) if upward else range(size)
        for row in rows:
            for c in (col, col - 1):
                if not is_reserved[row][c]:
                    bit_val = all_bits[bit_idx] if bit_idx < len(all_bits) else 0
                    bit_idx += 1
                    mask = ((row + c) % 2 == 0)
                    matrix[row][c] = bool(bit_val ^ mask)
        col -= 2
        upward = not upward

    format_bits = 0b111011111000100
    format_coords = [
        (0,8), (1,8), (2,8), (3,8), (4,8), (5,8), (7,8), (8,8),
        (8,7), (8,5), (8,4), (8,3), (8,2), (8,1), (8,0)
    ]
    format_coords_2 = [
        (8,size-1), (8,size-2), (8,size-3), (8,size-4), (8,size-5), (8,size-6), (8,size-7),
        (size-7,8), (size-6,8), (size-5,8), (size-4,8), (size-3,8), (size-2,8), (size-1,8), (size-1,8)
    ]

    for i in range(15):
        b = bool((format_bits >> (14 - i)) & 1)
        r1, c1 = format_coords[i]
        matrix[r1][c1] = b
        r2, c2 = format_coords_2[i]
        matrix[r2][c2] = b

    return matrix

url = "http://172.29.98.183:5000/"
m_custom = generate_qr_matrix_fixed(url)

qr = qrcode.QRCode(version=2, error_correction=qrcode.constants.ERROR_CORRECT_L, border=0)
qr.add_data(url)
qr.make(fit=True)
m_qrcode = qr.modules

diff = 0
for i in range(25):
    for j in range(25):
        if m_custom[i][j] != m_qrcode[i][j]:
            diff += 1

print("Differences:", diff)
import cv2
from PIL import Image

def matrix_to_image(matrix, filename):
    size = len(matrix)
    # create a PIL image from matrix
    img = Image.new('1', (size + 8, size + 8), 1) # include border=4 quiet zone
    pixels = img.load()
    for r in range(size):
        for c in range(size):
            if matrix[r][c]:
                pixels[c + 4, r + 4] = 0
    img = img.resize(((size+8)*10, (size+8)*10), Image.NEAREST)
    img.save(filename)

matrix_to_image(m_custom, "test_custom_fixed.png")

img_cv = cv2.imread('test_custom_fixed.png')
detector = cv2.QRCodeDetector()
data, bbox, _ = detector.detectAndDecode(img_cv)
print('Decoded data:', data)
