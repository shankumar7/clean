import re
with open("core/qr_gen.py", "r") as f:
    content = f.read()

new_coords = """    format_coords = [
        (0,8), (1,8), (2,8), (3,8), (4,8), (5,8), (7,8), (8,8),
        (8,7), (8,5), (8,4), (8,3), (8,2), (8,1), (8,0)
    ]
    format_coords_2 = [
        (8,size-1), (8,size-2), (8,size-3), (8,size-4), (8,size-5), (8,size-6), (8,size-7),
        (size-7,8), (size-6,8), (size-5,8), (size-4,8), (size-3,8), (size-2,8), (size-1,8)
    ]"""

content = re.sub(r"    format_coords = \[.*?    \]\n    format_coords_2 = \[.*?    \]", new_coords, content, flags=re.DOTALL)

with open("core/qr_gen.py", "w") as f:
    f.write(content)
