import io
import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QListWidget, QMenuBar,
    QToolBar, QAction, QLineEdit, QComboBox,
    QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QMessageBox, QTextEdit,
    QToolBar, QMenu, QAction, QSlider, QFrame
)
from PyQt5.QtGui import QIcon, QPainter, QPen, QPixmap, QImage
from PyQt5.QtCore import QRect, Qt, QPoint, QBuffer, QIODevice
from PIL import Image
import numpy as np
from core import util
from core.util import ImageManager

# class ImageManager:
#     # Placeholder for ImageManager class
#     pass


class Canvas(QLabel):
    """Widget for handling image display and cropping logic"""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.im_manager = ImageManager()

        # self.setAttribute(Qt.WA_StaticContents)
        # self.setMouseTracking(True)
        self.drawing = False
        self.last_point = QPoint()
        self.pen_color = Qt.black
        self.pen_size = 5

        self.original_image = None
        self.start_point = None
        self.end_point = None
        self.scale_factor = 1.0

        self.setPixmap(QPixmap())  # Start with a blank pixmap

    def load_image(self, path):
        """Load an image from the given path and handle any potential errors."""
        if not os.path.exists(path):
            QMessageBox.warning(self, "File Not Found",
                                f"Image path does not exist: {path}")
            return

        try:
            pil_image = Image.open(path)

            if "icc_profile" in pil_image.info:
                del pil_image.info['icc_profile']

            if pil_image.mode in ("RGBA", "P"):
                pil_image = pil_image.convert("RGB")

            q_image = self._pil_to_qimage(pil_image)

            self.parent.im = pil_image  # Store the PIL image for further processing
            self.original_image = QPixmap.fromImage(q_image)
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
                pil_image = self._qpixmap_to_pil(self.original_image)
                crop_coords = (left, upper, right, lower)
                cropped_image = pil_image.crop(crop_coords)
                self.show_edited_image(cropped_image)

            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to crop image:\n{e}")
    
    def show_edited_image(self, pillow_image):
        """Converted to Pixmap Image from Pil > bytes > Pixmap
            n show on the Canvas
        """
        if isinstance(pillow_image, QPixmap):
            self.original_image = pillow_image
        else:
            if pillow_image.mode in ("RGBA", "P"):
                pillow_image = pillow_image.convert("RGB")

            q_image = self._pil_to_qimage(pillow_image)
            # save to /edits; auto saved all changes with choisen image
            self.im_manager.save(self.parent.im_name, pillow_image)
            self.original_image = QPixmap.fromImage(q_image)

        self.setPixmap(self.original_image)

        # Reset
        self.scale_factor = 1.0
        self.adjustSize()

        self.start_point = None
        self.end_point = None

        # Redraw the label with the new cropped image and no rectangle
        self.update()

    def apply_gray(self):
        """Fix if gray n crop cropped n back color
        Convert the loaded image to grayscale and update the display."""
        if self.original_image:
            image = self.original_image.toImage(
            ).convertToFormat(QImage.Format_Grayscale8)
            self.setPixmap(QPixmap.fromImage(image))
            self.show_edited_image(QPixmap.fromImage(image))

    def apply_rotate_left(self):
        if self.original_image:
            pil_image = self._qpixmap_to_pil(self.original_image)
            rotated_pil_image = pil_image.rotate(90, expand=True)
            self.show_edited_image(rotated_pil_image)

    def apply_rotate_right(self):
        if self.original_image:
            pil_image = self._qpixmap_to_pil(self.original_image)
            rotated_pil_image = pil_image.rotate(-90, expand=True)
            self.show_edited_image(rotated_pil_image)
        
    # utils

    def _qpixmap_to_pil(self, qpixmap):
        """Convert QPixmap to PIL Image."""
        q_image = qpixmap.toImage()
        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        q_image.save(buffer, "PNG")
        pil_image = Image.open(io.BytesIO(buffer.data()))
        return pil_image

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
        self.im = None
        self.original_im = None
        self.working_directory = ""  # or str None ""
        self.filename = None  # to load image from folder get filename
        self.fullname = None
        self.im_name = None
        self.im_format = None

        self.im_manager = ImageManager()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Photoshop App')
        self.setGeometry(100, 100, 900, 700)

        # Menu Bar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')
        editMenu = menubar.addMenu('Edit')

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

        brightnessAction = QAction("Brightness", self)
        brightnessAction.triggered.connect(self.brightnessSlider)
        editMenu.addAction(brightnessAction)

        contrastAction = QAction("Contrast", self)
        contrastAction.triggered.connect(self.contrastSlider)
        editMenu.addAction(contrastAction)

        # Toolbar Widget
        self.toolbarWidget = ToolbarWidget(self)

        # Side Panel Widget
        self.sidePanelWidget = SidePanelWidget()

        # Frame Layout
        self.frameLayout = FrameLayout(self)

        # Tool Bar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        toolbar.addWidget(self.toolbarWidget)

        # Main Layout Setup
        centralWidget = QWidget()
        # self.setCentralWidget(centralWidget)

        # GUI Widgets
        self.file_list = QListWidget()
        self.image_label = Canvas(self)
        self.image_label.setAlignment(Qt.AlignHCenter)
        self.image_label.setStyleSheet("background-color: deepskyblue;")

        # Log area (in the Frame)
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setPlaceholderText(
            "Applied filters will be listed here...")

        # Adding widgets to layouts
        self.master_layout = QHBoxLayout()
        self.left_layout = QVBoxLayout()
        self.right_layout = QVBoxLayout()
        self.frame_layout = QHBoxLayout()

        self.left_layout.addWidget(self.file_list)
        self.left_layout.addWidget(QLabel("Filters:"))

        # Filter buttons
        filters = [
            ("Left", self.rotate_left), ("Right", self.rotate_right),
            ("Mirror", self.mirror), ("Sharpen", self.sharpen),
            ("B/W", self.gray), ("Saturation", self.saturate),
            ("Contrast", self.adjust_contrast), ("Blur", self.blur),
            ("Frame", self.toggleFrame)
        ]
        for text, handler in filters:
            btn = QPushButton(text)
            btn.clicked.connect(handler)
            self.left_layout.addWidget(btn)

        self.right_layout.addWidget(self.image_label)
        self.frame_layout.addWidget(self.frameLayout)

        self.master_layout.addLayout(self.left_layout, 20)
        self.master_layout.addLayout(self.right_layout, 60)
        self.master_layout.addLayout(self.frame_layout, 20)

        # Set the layout to the central widget
        centralWidget.setLayout(self.master_layout)
        self.setCentralWidget(centralWidget)

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
        filtered_files = [f for f in all_files if Path(
            f).suffix in allowed_extensions]
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
        if self.file_list.currentRow() >= 0:
            filename = self.file_list.currentItem().text()
            if not filename:
                QMessageBox.warning(self, "Error", "Filename is empty.")
                return

            self.fullname = os.path.join(self.working_directory, filename)
            if not os.path.exists(self.fullname):
                QMessageBox.warning(
                    self, "Error", f"Image path does not exist: {self.fullname}")
                return
            self.im_name = os.path.splitext(
                os.path.basename(filename))[0]
            self.im_format = os.path.splitext(
                os.path.basename(filename))[1]
            self.image_label.load_image(self.fullname)

    def toggleFrame(self):
        if self.frameLayout.isVisible():
            self.frameLayout.hideFrame()
        else:
            self.frameLayout.showFrame()

    def gray(self):
        """Hook gray"""
        self.image_label.apply_gray()
        self.txt_log.append("Applied grayscale filter.")
        print("gray")

    def rotate_left(self):
        """Hook rotate left"""
        self.image_label.apply_rotate_left()
        self.txt_log.append("Applied rotate left.")
        print("rotate left")

    def rotate_right(self):
        self.image_label.apply_rotate_right()
        self.txt_log.append("Applied rotate left.")
        print("rotate right")

    def brushTool(self, size):
        print(f"Brush tool selected: {size}")

    def eraserTool(self):
        print("Eraser tool selected")

    def zoomIn(self):
        print("Zoom in")

    def zoomOut(self):
        print("Zoom out")

    def filterTool(self):
        print("Filter tool selected")

    def mirror(self):
        print("Mirror")

    def sharpen(self):
        print("Sharpen")

    def saturate(self):
        print("Saturate")

    def adjust_contrast(self):
        print("Adjust contrast")

    def blur(self):
        print("Blur")

    def brightnessSlider(self):
        print("Brightness slider")

    def contrastSlider(self):
        print("Contrast slider")


class ToolbarWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent  # its oop[main:PhotoShop App] editor functions;
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        # Editor buttons
        editors = [
            # ("Brush", self.parent.brushTool),
            ("Eraser", self.parent.eraserTool),
            ("Zoom in", self.parent.zoomIn),
            ("Zoom out", self.parent.zoomOut), ("Left", self.parent.rotate_left),
            ("Right", self.parent.rotate_left), ("Filter",
                                                 self.parent.filterTool), ("Frame", self.parent.toggleFrame)
        ]
        for text, handler in editors:
            btn = QPushButton(text)
            btn.clicked.connect(handler)
            layout.addWidget(btn)

       # Brush button with sub-buttons
        self.brushButton = QPushButton("Brush2")
        self.brushButton.clicked.connect(self.showBrushOptions)
        layout.addWidget(self.brushButton)

        # Container for brush options
        self.brushOptionsContainer = QWidget()
        self.brushOptionsLayout = QHBoxLayout()
        self.brushOptionsContainer.setLayout(self.brushOptionsLayout)
        layout.addWidget(self.brushOptionsContainer)

        self.setLayout(layout)

    def showBrushOptions(self):
        """Logic in the brush.py laptop
            plus has x2 utils.py to resize n other.
        """
        # Clear previous options
        for i in reversed(range(self.brushOptionsLayout.count())):
            self.brushOptionsLayout.itemAt(i).widget().setParent(None)

        # Add small brush option
        smallBrushButton = QPushButton(QIcon('small2.png'), "img/small2.png")
        smallBrushButton.clicked.connect(
            lambda: self.parent.brushTool("small"))
        self.brushOptionsLayout.addWidget(smallBrushButton)

        # Add medium brush option
        mediumBrushButton = QPushButton(
            QIcon('medium2.png'), "img/medium2.png")
        mediumBrushButton.clicked.connect(
            lambda: self.parent.brushTool("medium"))
        self.brushOptionsLayout.addWidget(mediumBrushButton)

        # Add large brush option
        largeBrushButton = QPushButton(QIcon('large2.png'), "img/large2.png")
        largeBrushButton.clicked.connect(
            lambda: self.parent.brushTool("large"))
        self.brushOptionsLayout.addWidget(largeBrushButton)

        # Show the brush options container
        self.brushOptionsContainer.show()


class FrameLayout(QFrame):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(2)

        layout = QVBoxLayout()

        brightnessSlider = QSlider(Qt.Horizontal)
        brightnessSlider.setRange(-100, 100)
        layout.addWidget(QLabel('Brightness'))
        layout.addWidget(brightnessSlider)

        contrastSlider = QSlider(Qt.Horizontal)
        contrastSlider.setRange(-100, 100)
        layout.addWidget(QLabel('Contrast'))
        layout.addWidget(contrastSlider)

        colorAdjustButton = QPushButton('Apply')
        layout.addWidget(colorAdjustButton)

        self.setLayout(layout)

        self.hide()

    def showFrame(self):
        self.show()

    def hideFrame(self):
        self.hide()


class SidePanelWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        colorAdjustButton = QPushButton('Color Adjust')
        layout.addWidget(colorAdjustButton)

        layerButton = QPushButton('Layers')
        layout.addWidget(layerButton)

        self.setLayout(layout)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    ex = PhotoshopApp()
    ex.show()
    sys.exit(app.exec_())
