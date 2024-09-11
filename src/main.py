from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QListWidget, QComboBox, \
    QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt

# App Settings
app = QApplication([])
root = QWidget()
root.setWindowTitle("Lens")
root.resize(901, 701)


# All app widgets/objects
btn_folder = QPushButton("Folder")
file_list = QListWidget()

# rotation
btn_left = QPushButton("Rotate Left")
btn_right = QPushButton("Rotate Right")
mirror = QPushButton("Mirror")
sharpness = QPushButton("Adjust Sharpen")
gray = QPushButton("B/W")
saturation = QPushButton("Adj Saturation")
contrast = QPushButton("Adj Contrast")
blur = QPushButton("Apply Blur")


# Dropdown box
filter_box = QComboBox()
filter_box.addItems("""Rotate Left
Rotate Right
Mirror
Adjust Sharpen
B/W
Adj Saturation
Adj Contrast
Apply Blur""".split("\n"))

picture_box = QLabel("Picture Display Area")  # im will appear here
picture_box.setAlignment(Qt.AlignHCenter)
picture_box.setStyleSheet("background-color: deepskyblue;")

# App Design
master_layout = QHBoxLayout()

left_layout = QVBoxLayout()
right_layout = QVBoxLayout()

left_layout.addWidget(btn_folder)
left_layout.addWidget(file_list)
left_layout.addWidget(filter_box)
left_layout.addWidget(btn_left)
left_layout.addWidget(btn_right)
left_layout.addWidget(mirror)
left_layout.addWidget(sharpness)
left_layout.addWidget(gray)
left_layout.addWidget(saturation)
left_layout.addWidget(contrast)
left_layout.addWidget(blur)
right_layout.addWidget(picture_box)

master_layout.addLayout(left_layout, 1)
master_layout.addLayout(right_layout, 4)

root.setLayout(master_layout)


root.show()
app.exec_()
