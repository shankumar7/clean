from core.qr_gen import generate_qr_matrix
from PIL import Image

def matrix_to_image(matrix, filename):
    size = len(matrix)
    img = Image.new('1', (size, size), 1) # 1 is white
    pixels = img.load()
    for i in range(size):
        for j in range(size):
            if matrix[i][j]:
                pixels[j, i] = 0 # 0 is black
    img = img.resize((size*10, size*10), Image.NEAREST)
    img.save(filename)

url = "http://172.29.98.183:5000"
matrix = generate_qr_matrix(url)
matrix_to_image(matrix, "test_custom.png")
