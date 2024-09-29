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
import numpy as np
from core import util
from core.util import ImageManager


class MergedPhotoshopApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.im = None
        self.original_im = None
        self.im_name = None
        self.working_directory = "" 
        self.filename = None  # to load image from folder get filename
        self.fullname = None

        # crop
        self.start_point = None
        self.end_point = None
        self.scale_factor = 1.0




        self.im_manager = ImageManager()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Merged Photoshop App')
        self.setGeometry(100, 100, 900, 700)


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

        # Generate & Apply Filter buttons
        filters = [
            ("Folder", self.getWorkDirectory),
            ("B/W", self.gray),
        ]
        # decomposition
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
        # Initialaize with a default image or blank
        # self.image_label.setPixmap(QPixmap())

    def getWorkDirectory(self):
        self.working_directory = QFileDialog.getExistingDirectory(
            self, "Select Directory", "", QFileDialog.ShowDirsOnly)
        if not self.working_directory:
            print("No directory selected.") # log or message box
            return 
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.svg', '.bmp']
        all_files = os.listdir(self.working_directory)
        filtered_files = util.filter_files_by_extensions(
            all_files, allowed_extensions)
        self.file_list.clear()  # reset
        # add files to QListWidget
        for file in filtered_files:
            self.file_list.addItem(file)


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
        """Load t folder with images"""
        # if not self.working_directory:
        #     print("Working directory not set. Cannot load image.") # Optionally: log or message box

        # return
        self.filename = filename
        self.fullname = os.path.join(self.working_directory, self.filename)


        self.im = Image.open(self.fullname)
        self.original_im = self.im.copy()

        if "icc_profile" in self.im.info:
            del self.im.info['icc_profile']

        self.im_name = os.path.splitext(os.path.basename(filename))[0]

    def show_image(self, path):
        try:
            self.image_label.hide()
            im = Image.open(path)
            if im is None:
                # log
                print(f"Failed to load image: {path}")
                return

            if im.mode in ("RGBA", "P"):
                im = im.convert("RGB")
            data = np.array(im)

            # Validator of channels of image
            if len(data.shape) != 3 or data.shape[2] != 3:
                print(f"Unexpected image formatL {path}")
                return

            height, width, _ = data.shape # h, w, channels
            bytes_per_line = 3 * width
            q_im = QImage(data.data, width, height,
                        bytes_per_line, QImage.Format_RGB888)
            
            if q_im.isNull():
                print(f"Failed to convert image to QImage: {path}")
                return

            im = QPixmap.fromImage(q_im)
            self.original_im = self.im.copy()
            self.image_label.setPixmap(im)
            # reset
            self.scale_factor = 1.0
            self.image_label.adjustSize()
            self.image_label.show()
        except Exception as ex:
            ...

    def resizeEvent(self, event):
        if self.original_im and isinstance(self.original_im, QPixmap):
            self.scale_factor = min(
                self.image_label.width() / self.original_im.width(),
                self.image_label.height() / self.original_im.height()
            )
            scaled_pixmap = self.original_im.scaled(
                self.original_im.size() * self.scale_factor,
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
        super().resizeEvent(event)
            

    def gray(self):
        """Convert to grayscale"""
        if self.im is not None:
            self.im = self.im.convert("L")
            self.save_and_show()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MergedPhotoshopApp()
    window.show()
    sys.exit(app.exec_())
