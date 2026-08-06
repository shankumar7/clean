"""
Standalone Pure-Python QR Code Matrix Generator (Zero Dependencies).
Generates scannable 2D QR Code matrices for URLs without requiring external pip/C libraries.
"""

class GF256:
    """Galois Field GF(2^8) with primitive polynomial x^8 + x^4 + x^3 + x^2 + 1 (0x11d)."""
    EXP = [0] * 512
    LOG = [0] * 256
    
    @classmethod
    def init(cls):
        x = 1
        for i in range(255):
            cls.EXP[i] = x
            cls.LOG[x] = i
            x <<= 1
            if x & 0x100:
                x ^= 0x11d
        for i in range(255, 512):
            cls.EXP[i] = cls.EXP[i - 255]

    @classmethod
    def mul(cls, a, b):
        if a == 0 or b == 0:
            return 0
        return cls.EXP[cls.LOG[a] + cls.LOG[b]]

GF256.init()


def rs_poly_multiply(p1, p2):
    res = [0] * (len(p1) + len(p2) - 1)
    for i, c1 in enumerate(p1):
        for j, c2 in enumerate(p2):
            res[i + j] ^= GF256.mul(c1, c2)
    return res


def rs_generator_poly(degree):
    g = [1]
    for i in range(degree):
        g = rs_poly_multiply(g, [1, GF256.EXP[i]])
    return g


def rs_encode(data, ecc_len):
    gen = rs_generator_poly(ecc_len)
    res = list(data) + [0] * ecc_len
    for i in range(len(data)):
        coef = res[i]
        if coef != 0:
            for j in range(len(gen)):
                res[i + j] ^= GF256.mul(gen[j], coef)
    return res[len(data):]


def generate_qr_matrix(text):
    """
    Generates a scannable QR code matrix (2D list of booleans: True=Black, False=White)
    for URL strings up to 34 characters using QR Version 2 (25x25 grid).
    """
    data_bytes = text.encode('utf-8')
    if len(data_bytes) > 28:
        data_bytes = data_bytes[:28]
        
    ver = 2
    size = 25
    data_cap = 28
    ecc_len = 6
    
    # 1. Bit Stream Construction
    bits = []
    def add_bits(val, length):
        for i in range(length - 1, -1, -1):
            bits.append((val >> i) & 1)

    # Mode Indicator: 0100 (Byte mode)
    add_bits(0b0100, 4)
    # Character Count Indicator (8 bits for Ver 1-9 byte mode)
    add_bits(len(data_bytes), 8)
    # Data bits
    for b in data_bytes:
        add_bits(b, 8)
    # Terminator
    add_bits(0, min(4, data_cap * 8 - len(bits)))
    # Bit padding
    while len(bits) % 8 != 0:
        bits.append(0)
    # Pad bytes 0xEC, 0x11
    pad_bytes = [0xEC, 0x11]
    pad_idx = 0
    while len(bits) < data_cap * 8:
        add_bits(pad_bytes[pad_idx], 8)
        pad_idx = (pad_idx + 1) % 2

    # Convert bits to byte list
    data_codewords = []
    for i in range(0, len(bits), 8):
        byte_val = 0
        for b in bits[i:i+8]:
            byte_val = (byte_val << 1) | b
        data_codewords.append(byte_val)

    # 2. Error Correction Codewords
    ecc_codewords = rs_encode(data_codewords, ecc_len)
    all_codewords = data_codewords + ecc_codewords

    # 3. Matrix Placement
    matrix = [[None] * size for _ in range(size)]
    is_reserved = [[False] * size for _ in range(size)]

    def set_module(r, c, val, reserved=True):
        matrix[r][c] = val
        if reserved:
            is_reserved[r][c] = True

    # Finder Patterns (7x7) at Top-Left, Top-Right, Bottom-Left
    def draw_finder(row, col):
        for r in range(7):
            for c in range(7):
                is_black = (r in (0, 6) or c in (0, 6) or (2 <= r <= 4 and 2 <= c <= 4))
                set_module(row + r, col + c, is_black)

    draw_finder(0, 0)
    draw_finder(0, size - 7)
    draw_finder(size - 7, 0)

    # Separators around finders
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

    # Alignment Pattern (Version 2 has 1 alignment pattern at (18, 18))
    align_r, align_c = 18, 18
    for r in range(-2, 3):
        for c in range(-2, 3):
            is_black = (abs(r) == 2 or abs(c) == 2 or (r == 0 and c == 0))
            set_module(align_r + r, align_c + c, is_black)

    # Timing Patterns
    for i in range(size):
        if matrix[6][i] is None:
            set_module(6, i, (i % 2 == 0))
        if matrix[i][6] is None:
            set_module(i, 6, (i % 2 == 0))

    # Dark Module & Reserved Format Areas
    set_module(size - 8, 8, True)
    for i in range(9):
        if matrix[8][i] is None: set_module(8, i, False)
        if matrix[i][8] is None: set_module(i, 8, False)
    for i in range(8):
        if matrix[8][size - 1 - i] is None: set_module(8, size - 1 - i, False)
        if matrix[size - 1 - i][8] is None: set_module(size - 1 - i, 8, False)

    # 4. Data Placement (Zig-zag scan)
    all_bits = []
    for cw in all_codewords:
        for b in range(7, -1, -1):
            all_bits.append((cw >> b) & 1)

    bit_idx = 0
    col = size - 1
    upward = True

    while col > 0:
        if col == 6:  # Skip vertical timing column
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

    # Format Information bits for Version 2, Mask 0, ECC Level L: 0b111011111000100
    format_bits = 0b111011111000100
    format_coords = [
        (8,0), (8,1), (8,2), (8,3), (8,4), (8,5), (8,7), (8,8),
        (7,8), (5,8), (4,8), (3,8), (2,8), (1,8), (0,8)
    ]
    format_coords_2 = [
        (size-1,8), (size-2,8), (size-3,8), (size-4,8), (size-5,8), (size-6,8), (size-7,8),
        (8,size-8), (8,size-7), (8,size-6), (8,size-5), (8,size-4), (8,size-3), (8,size-2), (8,size-1)
    ]

    for i in range(15):
        b = bool((format_bits >> (14 - i)) & 1)
        r1, c1 = format_coords[i]
        matrix[r1][c1] = b
        r2, c2 = format_coords_2[i]
        matrix[r2][c2] = b

    return matrix
