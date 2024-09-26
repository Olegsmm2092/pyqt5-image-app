import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMenuBar, QToolBar, QAction, QWidget,
    QFileDialog, QLabel, QPushButton, QLineEdit, QComboBox, QListWidget,
    QVBoxLayout, QHBoxLayout, QTextEdit, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PIL import Image
from core import util
from core.util import ImageManager  # Assuming ImageManager is implemented


class MergedPhotoshopApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.im = None
        self.original_im = None
        self.im_name = None
        self.working_directory = ""  # or str None ""
        self.filename = None  # to load image from folder get filename

        self.im_manager = ImageManager()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Merged Photoshop App')
        self.setGeometry(100, 100, 900, 700)

        # Menu Bar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')

        openAction = QAction('Open', self)
        openAction.triggered.connect(self.openFile)
        fileMenu.addAction(openAction)

        saveAction = QAction('Save', self)
        saveAction.triggered.connect(self.saveFile)
        fileMenu.addAction(saveAction)

        # Add the Folder action to the File menu
        folderAction = QAction('Folder', self)
        folderAction.triggered.connect(self.getWorkDirectory)
        fileMenu.addAction(folderAction)

        # Tool Bar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        brushButton = QPushButton('Brush')
        toolbar.addWidget(brushButton)

        eraserButton = QPushButton('Eraser')
        toolbar.addWidget(eraserButton)

        # Main Layout Setup
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        # GUI Widgets
        self.file_list = QListWidget()
        self.image_label = QLabel("Picture Display Area")
        self.image_label.setAlignment(Qt.AlignHCenter)
        self.image_label.setStyleSheet("background-color: deepskyblue;")

        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setPlaceholderText(
            "Applied filters will be listed here...")

        # Adding widgets to layouts
        self.master_layout = QHBoxLayout()
        self.left_layout = QVBoxLayout()
        self.right_layout = QVBoxLayout()

        self.left_layout.addWidget(self.file_list)
        self.left_layout.addWidget(QLabel("Filters:"))

        # Filter buttons
        filters = [
            ("Left", self.rotate_left), ("Right", self.rotate_right),
            ("Mirror", self.mirror), ("Sharpen", self.sharpen),
            ("B/W", self.gray), ("Saturation", self.saturate),
            ("Contrast", self.adjust_contrast), ("Blur", self.blur)
        ]
        for text, handler in filters:
            btn = QPushButton(text)
            btn.clicked.connect(handler)
            self.left_layout.addWidget(btn)

        self.right_layout.addWidget(self.image_label)

        self.master_layout.addLayout(self.left_layout, 20)
        self.master_layout.addLayout(self.right_layout, 80)

        # Set the layout to the central widget
        self.centralWidget.setLayout(self.master_layout)

        # Connection setup
        self.file_list.currentRowChanged.connect(self.displayImage)

    def openFile(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image File", "", "Image Files (*.png *.jpg *.bmp)")
        if file_path:
            self.load_image(file_path)
            self.show_image(file_path)

    def getWorkDirectory(self):
        self.working_directory = QFileDialog.getExistingDirectory(
            self, None, "Select Directory")
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.svg', '.bmp']
        all_files = os.listdir(self.working_directory)
        filtered_files = util.filter_files_by_extensions(
            all_files, allowed_extensions)
        self.file_list.clear()  # reset
        # add files to QListWidget
        for file in filtered_files:
            self.file_list.addItem(file)

    def saveFile2(self):
        """Save the current image using ImageManager"""
        if self.im is not None:
            filename = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)")[0]
            if filename:
                base_name = os.path.splitext(os.path.basename(filename))[0]
                self.im_manager.save(base_name, self.im)

    def saveFile(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(
            self, "Save File", "", "Images (*.png *.jpg *.bmp)", options=options)
        if fileName:
            self.im.save(fileName)

    def displayImage(self):
        """Main func to get x2 utils to load n show on the display area image chosen from folder"""
        if self.file_list.currentRow() >= 0:
            filename = self.file_list.currentItem().text()
            self.load_image(filename)
            self.show_image(os.path.join(
                self.working_directory, self.filename))
            
    def save_and_show(self):
        """Helper to avoid copypast inside methods of ImageEditor"""
        self.im_manager.save(self.im_name, self.im)
        self.show_image(self.im_manager.fullname)

     # oop ImageEditor
    def load_image(self, filename):
        # its other one oop - ImageEditor
        # from ai give to this oop methods - load, save, ...
        """Load t folder with images"""
        self.filename = filename
        fullname = os.path.join(self.working_directory, self.filename)
        self.im = Image.open(fullname)
        self.original_im = self.im.copy()

        if "icc_profile" in self.im.info:
            del self.im.info['icc_profile']

        self.im_name = os.path.splitext(os.path.basename(filename))[0]

    def show_image(self, path):
        self.image_label.hide()
        im = QPixmap(path)
        if im.isNull():
            # log
            print(f"Failed to load image: {path}")
            return

        w, h = self.image_label.width(), self.image_label.height()
        im = im.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.im_to_crop = im
        self.image_label.setPixmap(im)
        self.image_label.show()

    # oop ImageEditor
    def rotate_left(self):
        self.im = self.im.rotate(90, expand=True)
        self.save_and_show()

    def rotate_right(self):
        self.im = self.im.rotate(-90, expand=True)
        self.save_and_show()

    def mirror(self):
        """Mirror the image"""
        # Implement logic

    def sharpen(self):
        """Sharpen the image"""
        # Implement logic

    def gray(self):
        """Convert to grayscale"""
        self.im = self.im.convert("L")
        self.save_and_show()

    def saturate(self):
        """Increase saturation"""
        # Implement logic

    def adjust_contrast(self):
        """Adjust contrast"""
        # Implement logic

    def blur(self):
        """Apply blur effect"""
        # Implement logic


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MergedPhotoshopApp()
    window.show()
    sys.exit(app.exec_())
