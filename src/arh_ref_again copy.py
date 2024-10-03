
# not working

# but interesting _gray method

# how to call from image_label to them

import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMenuBar, QToolBar, QAction, QWidget,
    QFileDialog, QLabel, QPushButton, QLineEdit, QComboBox, QListWidget,
    QVBoxLayout, QHBoxLayout, QTextEdit, QMessageBox
)
from PyQt5.QtGui import QPainter, QPen, QPixmap, QImage
from PyQt5.QtCore import QRect, Qt, QPoint
from PIL import Image
from core.util import ImageManager  # Assuming ImageManager is implemented
import numpy as np


class Canvas(QLabel):
    """Widget for handling image display and cropping logic"""

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setPixmap(QPixmap())  # Start with a blank pixmap
        self.im_manager = ImageManager()

    def load_image(self, path):
        """Load an image from the given path and handle any potential errors"""
        if not os.path.exists(path):
            QMessageBox.warning(self, "File Not Found",
                                f"Image path does not exist: {path}")
            return

        try:
            pil_image = Image.open(path)

            if pil_image.mode in ("RGBA", "P"):
                pil_image = pil_image.convert("RGB")

            data = np.array(pil_image)
            height, width, channel = data.shape
            bytes_per_line = 3 * width
            q_image = QImage(data.data, width, height,
                             bytes_per_line, QImage.Format_RGB888)

            self.parent.original_image = QPixmap.fromImage(q_image) # self.im; copy to self.original_image
            self.setPixmap(self.parent.original_image)
            # self.scale_factor = 1.0
            self.adjustSize()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load image:\n{e}")

    
    

    

class PhotoshopApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.im_manager = ImageManager()
        self.im = None
        self.fullname = None
        self.im_name = None
        self.im_format = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Merged Photoshop App')
        self.setGeometry(100, 100, 900, 700)

        # Main Layout Setup
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        self.file_list = QListWidget()
        self.image_label = Canvas(self)
        self.image_label.setAlignment(Qt.AlignHCenter)
        self.image_label.setStyleSheet("background-color: deepskyblue;")
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setPlaceholderText(
            "Applied filters will be listed here...")

        # Layouts
        self.master_layout = QHBoxLayout()
        self.left_layout = QVBoxLayout()
        self.right_layout = QVBoxLayout()

        self.left_layout.addWidget(self.file_list)
        self.left_layout.addWidget(QLabel("Filters:"))

        filters = [
            ("Folder", self.getWorkDirectory),
            ("Left", self.rotate_left),
            ("Right", self.rotate_right),
            ("B/W", self.gray),
            ("crop", self.crop_image),
        ]
        for text, handler in filters:
            btn = QPushButton(text)
            btn.clicked.connect(handler)
            self.left_layout.addWidget(btn)

        self.right_layout.addWidget(self.image_label)
        self.master_layout.addLayout(self.left_layout, 20)
        self.master_layout.addLayout(self.right_layout, 80)
        self.centralWidget.setLayout(self.master_layout)

        self.file_list.currentRowChanged.connect(self.displayImage)

    def getWorkDirectory(self):
        self.working_directory = QFileDialog.getExistingDirectory(
            self, "Select Directory")
        if self.working_directory:
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
            all_files = os.listdir(self.working_directory)
            filtered_files = [f for f in all_files if Path(
                f).suffix in allowed_extensions]
            self.file_list.clear()
            self.file_list.addItems(filtered_files)
        else:
            QMessageBox.warning(self, "Warning", "No directory selected.")

    def displayImage(self):
        if self.file_list.currentRow() >= 0:
            filename = self.file_list.currentItem().text()
            if not filename:
                QMessageBox.warning(self, "Error", "Filename is empty.")
                return

            fullname = os.path.join(self.working_directory, filename)
            if not os.path.exists(fullname):
                QMessageBox.warning(
                    self, "Error", f"Image path does not exist: {fullname}")
                return
            # self.image_label.im_name = filename
            # self.image_label.im_name = os.path.splitext(
            #     os.path.basename(filename))[0] # with this need self.format = None
            # self.image_label.im_format = os.path.splitext(
            #     os.path.basename(filename))[1] # with this need self.format = None
            # self.image_label.fullname = fullname
            self.image_label.load_image(fullname)

    def gray(self):
       print("gray")

    def rotate_left(self):
        print("rotate left")

    def rotate_right(self):
        print("rotate right")

    def crop_image(self):
       print("Cropeed Image")

        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PhotoshopApp()
    window.show()
    sys.exit(app.exec_())
