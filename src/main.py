import os
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QLabel, QPushButton, QListWidget, QComboBox, \
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

master_layout.addLayout(left_layout, 20)
master_layout.addLayout(right_layout, 80)

root.setLayout(master_layout)


# All App Functionality
working_directory = ""
# allowed_extentions = '.jpg .jpeg .png .svg'.split() # debug > solution > local inside func; to not to be overwriting

# All App Functionality
working_directory = ""

# Filter files by allowed extensions
def filter_files_by_extension(files, extensions):
    return [file for file in files if any(file.lower().endswith(ext) for ext in extensions)]

# Choose current work directory
def getWorkDirectory():
    global working_directory
    working_directory = QFileDialog.getExistingDirectory(
        None, "Select Directory")
    # only local; cant be by args cuz will be `overwriting`
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.svg']
    all_files = os.listdir(working_directory)
    filtered_files = filter_files_by_extension(all_files, allowed_extensions)
    file_list.clear()  # reset
    # Add files to QListWidget
    for file in filtered_files:
        file_list.addItem(file)


btn_folder.clicked.connect(getWorkDirectory)













root.show()
app.exec_()
