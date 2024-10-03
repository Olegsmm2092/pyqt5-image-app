
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


class ImageLabel(QLabel):
    """Widget for handling image display and cropping logic"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.start_point = None
        self.end_point = None
        self.scale_factor = 1.0
        self.im = None
        self.original_image = None
        self.fullname = None
        self.im_name = None
        self.im_format = None
        self.crop_im = None

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

            self.original_image = QPixmap.fromImage(q_image) # self.im; copy to self.original_image
            self.setPixmap(self.original_image)
            self.scale_factor = 1.0
            self.adjustSize()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load image:\n{e}")

    def resizeEvent(self, event):
        """Resize the displayed image to fit the QLabel while maintaining aspect ratio"""
        if self.original_image:
            self.scale_factor = min(
                self.width() / self.original_image.width(),
                self.height() / self.original_image.height()
            )
            scaled_pixmap = self.original_image.scaled(
                self.original_image.size() * self.scale_factor,
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)
        super().resizeEvent(event)

    def set_start_point(self, point):
        self.start_point = point
        self.update()  # Request a repaint

    def set_end_point(self, point):
        self.end_point = point
        self.update()  # Request a repaint

    def paintEvent(self, event):
        """Draw a rectangle when cropping"""
        super().paintEvent(event)
        if self.start_point and self.end_point:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.green, 2, Qt.SolidLine))
            rect = QRect(self.start_point, self.end_point)
            painter.drawRect(rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_point = event.pos()
            self.end_point = event.pos()
            self.update()

    def mouseMoveEvent(self, event):
        if self.start_point:
            self.end_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.end_point = event.pos()
            self.crop_image()

    def crop_image(self):
        """Crop the image using the selected coordinates"""
        if self.start_point and self.end_point:
            x1, y1 = self.start_point.x(), self.start_point.y()
            x2, y2 = self.end_point.x(), self.end_point.y()

            # Determine the cropping rectangle
            left = min(x1, x2)
            upper = min(y1, y2)
            right = max(x1, x2)
            lower = max(y1, y2)

            # Convert the scaled coordinates to original image coordinates
            original_width = self.original_image.width()
            original_height = self.original_image.height()
            left = int(left / self.scale_factor)
            upper = int(upper / self.scale_factor)
            right = int(right / self.scale_factor)
            lower = int(lower / self.scale_factor)

            # Check if the coordinates are within bounds
            if (left < 0 or upper < 0 or right > original_width or
                    lower > original_height or left >= right or upper >= lower):
                QMessageBox.warning(
                    self, "Invalid Crop", "Crop coordinates are invalid or out of bounds."
                )
                return
            try:
                pil_image = Image.open(self.fullname)
                crop_coords = (left, upper, right, lower)
                cropped_image = pil_image.crop(crop_coords)
                self.show_cropped_image(cropped_image)
                # just save using utils oop n get her path n load
                # self.crop_im = cropped_image
                # # to check loading cropped without save to /edits/
                # pil_image = cropped_image.copy()
                # if pil_image.mode in ("RGBA", "P"):
                #     pil_image = pil_image.convert("RGB")

                # data = np.array(pil_image)
                # height, width, channel = data.shape
                # bytes_per_line = 3 * width
                # q_image = QImage(data.data, width, height,
                #                 bytes_per_line, QImage.Format_RGB888)
                # self.im_manager.save(self.im_name, q_image, self.im_format)
                # # self.im; copy to self.original_image
                # self.original_image = QPixmap.fromImage(q_image)
                # self.setPixmap(self.original_image)
                # self.scale_factor = 1.0
                # self.adjustSize()
                
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to crop image:\n{e}")
            # finally:
            #     # Reset the selection points after cropping
            #     self.start_point = None
            #     self.end_point = None

            #     # Redraw the label with the new cropped image and no rectangle
            #     self.update()

    def show_cropped_image(self, pillow_image):
        """Converted to Pixmap Image from Pil > bytes > Pixmap
            n show on the Canvas
        """
        # copypast self.load_image(); but not from path; from file; if get from saved cant cuz save on the стадии изменения формата
        if isinstance(pillow_image, QPixmap):
            self.original_image = pillow_image
        else:

            if pillow_image.mode in ("RGBA", "P"):
                pillow_image = pillow_image.convert("RGB")

            data = np.array(pillow_image)
            height, width, channel = data.shape
            bytes_per_line = 3 * width
            q_image = QImage(data.data, width, height,
                                bytes_per_line, QImage.Format_RGB888)
            # save to /edits; auto saved all changes with choisen image
            self.im_manager.save(self.im_name, pillow_image)
            # self.im_manager.save(self.im_name, q_image, self.im_format)
            # self.im; copy to self.original_image
            self.original_image = QPixmap.fromImage(q_image)
            
        self.setPixmap(self.original_image)
        
        # Reset
        self.scale_factor = 1.0
        self.adjustSize()

        self.start_point = None
        self.end_point = None

        # Redraw the label with the new cropped image and no rectangle
        self.update()

class MergedPhotoshopApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.im_manager = ImageManager()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Merged Photoshop App')
        self.setGeometry(100, 100, 900, 700)

        # Main Layout Setup
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        self.file_list = QListWidget()
        self.image_label = ImageLabel()
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
            self.image_label.im_name = os.path.splitext(
                os.path.basename(filename))[0] # with this need self.format = None
            self.image_label.im_format = os.path.splitext(
                os.path.basename(filename))[1] # with this need self.format = None
            self.image_label.fullname = fullname
            self.image_label.load_image(fullname)

    def gray(self):
        """fix to working with cur displayed image before crop
            or all work with canvas by class Canvas(ImageLabel);
            n gray logic to canvas too
        """
        if self.image_label.original_image:
            image = self.image_label.original_image.toImage(
            ).convertToFormat(QImage.Format_Grayscale8)
            self.image_label.setPixmap(QPixmap.fromImage(image))
            self.image_label.im_manager.save(
                self.image_label.im_name, QPixmap.fromImage(image))
            self.image_label.show_cropped_image(QPixmap.fromImage(image))

    def rotate_left(self):
        print("rotate left")

    def rotate_right(self):
        print("rotate right")

        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MergedPhotoshopApp()
    window.show()
    sys.exit(app.exec_())
