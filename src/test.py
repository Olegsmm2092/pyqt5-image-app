import os
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QLabel, QPushButton, QListWidget, QComboBox, \
    QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PIL import Image, ImageFilter, ImageEnhance


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


# Get All Files Recursively
def getAllFiles(output_dir, max_depth=2):
    """get files inside deeper folders with adaptive max depth"""
    all_files = []
    base_depth = output_dir.rstrip(os.path.sep).count(os.path.sep)
    for root, dirs, files in os.walk(output_dir):
        cur_depth = root.count(os.path.sep) - base_depth
        if cur_depth < max_depth:
            for file in files:
                all_files.append(os.path.join(root, file))
        dirs[:] = [i for i in dirs if cur_depth + 1 < max_depth]
    return all_files


# Filter files by allowed extensions
def filter_files_by_extension(files, extensions):
    """Util to func getWrokDirectory"""
    return [file for file in files if any(file.lower().endswith(ext) for ext in extensions)]


# Choose current work directory
def getWorkDirectory():
    global working_directory
    working_directory = QFileDialog.getExistingDirectory(
        None, "Select Directory")
    # only local; cant be by args cuz will be `overwriting`
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.svg']
    # all_files = os.listdir(working_directory) # modify using ds googleColab; for deep folder
    all_files = getAllFiles(working_directory)
    filtered_files = filter_files_by_extension(all_files, allowed_extensions)
    file_list.clear()  # reset
    # Add files to QListWidget
    for file in filtered_files:
        # file_list.addItem(os.path.basename(file)) # extract only filename;
        file_list.addItem(file)


# from core.utils import ImageEditor
class imageEditor:
    def __init__(self):
        self.im = None
        self.original_im = None
        self.filename = None
        self.folder = 'edits/'

    def load_image(self, filename):
        """принимает подгруженный image"""
        self.filename = filename
        fullname = os.path.join(working_directory, self.filename)
        self.im = Image.open(fullname)
        self.original_im = self.im.copy()

    def save_image(self):
        path = os.path.join(working_directory, self.folder)
        # cuz need work_dir too
        if not os.path.exists(self.folder) or os.path.isdir(self.folder):
            os.makedirs (path)

        fullname = os.path.join(path, self.filename)  # get name
        print(path)
        print(fullname)
        print("save:", path + self.filename)
        self.im.save(fullname)

    def show_image(self, path):
        """show im based on the box coords"""
        picture_box.hide()
        im = QPixmap(path)
        w, h = picture_box.width(), picture_box.height()
        im = im.scaled(w, h, Qt.KeepAspectRatio)
        picture_box.setPixmap(im)
        picture_box.show()

    def gray(self):
        self.im = self.im.convert("L")
        self.save_image()
        im_path = os.path.join(working_directory, self.folder, self.filename)
        self.show_image(im_path)


def displayImage():
    if file_list.currentRow() >= 0:
        filename = file_list.currentItem().text()
        editor_im.load_image(filename)
        editor_im.show_image(os.path.join(
            working_directory, editor_im.filename))


editor_im = imageEditor()

btn_folder.clicked.connect(getWorkDirectory)
file_list.currentRowChanged.connect(displayImage)
gray.clicked.connect(editor_im.gray)
root.show()
app.exec_()
