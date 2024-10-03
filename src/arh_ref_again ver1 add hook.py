import sys
import os
import numpy as np
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMenuBar, QToolBar, QAction, QWidget,
    QFileDialog, QLabel, QPushButton, QLineEdit, QComboBox, QListWidget,
    QVBoxLayout, QHBoxLayout, QTextEdit, QMessageBox, QFrame, QSlider, QMenu
)
from PyQt5.QtGui import QPainter, QPen, QPixmap, QImage, QIcon
from PyQt5.QtCore import QRect, Qt, QPoint
from PIL import Image
from core.util import ImageManager


class Canvas(QLabel):
    """Widget for handling image display and cropping logic"""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.im_manager = ImageManager()
        self.current_image = None  # Store the current image being processed

        self.setAttribute(Qt.WA_StaticContents)
        self.setMouseTracking(True)
        self.setPixmap(QPixmap())  # Start with a blank pixmap
        self.drawing = False
        self.last_point = QPoint()
        self.pen_color = Qt.black
        self.pen_size = 5

    def load_image(self, path):
        """Load an image from the given path and handle any potential errors."""
        if not os.path.exists(path):
            QMessageBox.warning(self, "File Not Found",
                                f"Image path does not exist: {path}")
            return

        try:
            pil_image = Image.open(path)
            if pil_image.mode in ("RGBA", "P"):
                pil_image = pil_image.convert("RGB")

            q_image = self._pil_to_qimage(pil_image)

            self.current_image = pil_image  # Store the PIL image for further processing
            self.setPixmap(QPixmap.fromImage(q_image))
            self.adjustSize()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load image:\n{e}")

    def apply_gray(self):
        """Convert the loaded image to grayscale and update the display."""
        if self.current_image:
            gray_image = self.current_image.convert(
                "L")  # Convert to grayscale using PIL
            self.current_image = gray_image  # Update current image to the grayscale version
            q_image = self._pil_to_qimage(
                gray_image, qimage_format=QImage.Format_Grayscale8)
            self.setPixmap(QPixmap.fromImage(q_image))
            self.adjustSize()

    # utils
    def _pil_to_qimage(self, pil_image, qimage_format=QImage.Format_RGB888):
        """Convert a PIL image to QImage."""
        data = np.array(pil_image)
        if len(data.shape) == 2:  # to gray
            height, width = data.shape
            bytes_per_line = width
        elif len(data.shape) == 3:  # to rgb
            height, width, channel = data.shape
            bytes_per_line = 3 * width
        q_image = QImage(data.data, width, height,
                         bytes_per_line, qimage_format)
        return q_image


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

            self.image_label.load_image(fullname)

    def gray(self):
       """Hook gray"""
       self.image_label.apply_gray()
       self.txt_log.append("Applied grayscale filter.")
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
