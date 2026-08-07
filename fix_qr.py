with open("gui/components/qr_widget.py", "r") as f:
    content = f.read()

content = content.replace("border=2,", "border=4,")
content = content.replace("Qt.TransformationMode.SmoothTransformation", "Qt.TransformationMode.FastTransformation")

with open("gui/components/qr_widget.py", "w") as f:
    f.write(content)
