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
from core import util
from core.util import ImageManager  # Assuming ImageManager is implemented
import numpy as np


class ImageLabel(QLabel):
    """Logic only for crop

    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.start_point = None
        self.end_point = None
        # self.im = None
        # self.original_im = None
        self.im_name = None
        self.working_directory = ""
        self.fullname = None
        self.scale_factor = 1.0
        self.original_image = None
        # LinkedList to main oop // its not clean arthitecture cuz not isolated

        # Initialize with a default image or blank
        self.setPixmap(QPixmap())

    def load_image(self, path):
        try:
            # Load the image using PIL
            pil_image = Image.open(path)

            # Convert to RGB if necessary (if it has an alpha channel)
            if pil_image.mode in ("RGBA", "P"):
                pil_image = pil_image.convert("RGB")

            # Convert to numpy array and then to QPixmap
            data = np.array(pil_image)
            height, width, channel = data.shape
            bytes_per_line = 3 * width
            q_image = QImage(data.data, width, height,
                             bytes_per_line, QImage.Format_RGB888)

            self.original_image = QPixmap.fromImage(q_image)
            self.original_im = self.original_image.copy()  # save a copy of original
            self.setPixmap(self.original_image)
            self.scale_factor = 1.0
            self.adjustSize()
        except Exception as e:
            ...
            # path = self.__photoshop.im_manager.fullname
            # QMessageBox.critical(self, "Error", f"Failed to load image:\n{e}")

    def resizeEvent(self, event):
        if self.original_image:
            # Resize the pixmap to fit the label while maintaining aspect ratio
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

    def crop_image(self):
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

            # Perform the cropping using PIL
            try:
                pil_image = Image.open(self.fullname)
                crop_coords = (left, upper, right, lower)
                cropped_image = pil_image.crop(crop_coords)
                # Overwrite or save as needed
                self.__photoshop = MergedPhotoshopApp() # LinkedList // not clean arhitecture need isolation by class Name() __init__(self, <here name of oop>)
                self.__photoshop.im = cropped_image
                self.__photoshop.im_name = self.im_name
                self.__photoshop.fullname = self.__photoshop.im_manager.fullname
                self.__photoshop.save_and_show() # cuz fullname None
                # self.__photoshop.im_manager.save(self.im_name, cropped_image)
                self.__photoshop.show_image(
                    self.__photoshop.im_manager.fullname)  # cuz fullname None
                
                # Reload the cropped image
                # self.load_image(self.__photoshop.im_manager.fullname)

            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to crop image:\n{e}")
            finally:
                # Reset the selection points after cropping
                self.start_point = None
                self.end_point = None

                # Redraw the label with the new cropped image and no rectangle
                self.update()

    def paintEvent(self, event):
        super().paintEvent(event)  # Call the base class method to draw the image
        if self.start_point and self.end_point:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.green, 2, Qt.SolidLine))
            rect = QRect(self.start_point, self.end_point)
            painter.drawRect(rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.set_start_point(event.pos())
            self.set_end_point(event.pos())

    def mouseMoveEvent(self, event):
        if self.start_point:
            self.set_end_point(event.pos())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.set_end_point(event.pos())
            self.crop_image()


class MergedPhotoshopApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.im = None
        self.im_additional = None
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
        self.image_label = ImageLabel()
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
        
        path_to_image_label = os.path.join(
            self.working_directory, self.filename)
        self.image_label.fullname = path_to_image_label
        self.image_label.im_name = self.im_name
        self.image_label.load_image(path_to_image_label)

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
        self.im_additional = self.im.copy()

        if "icc_profile" in self.im.info:
            del self.im.info['icc_profile']

        self.im_name = os.path.splitext(os.path.basename(filename))[0]
       

    # def show_image(self, path, path_crop=None):
    def show_image(self, path):
        # связка между ооp here; ref. self.canvas (image_label) в отдельный widget; class ImageLabel;
        # crop/ other functions
        # self.image_label.fullname = path
        # self.image_label.im_name = self.im_name
        # self.image_label.load_image(path) # подотрет все inits values to None
        self.image_label.hide()
        # base logic
        im = QPixmap(path)
        if im.isNull():
            # log
            print(f"Failed to load image: {path}")
            return

        w, h = self.image_label.width(), self.image_label.height()
        im = im.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
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
        self.im = self.im_additional.convert("L")
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
