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


class ToolbarWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent # its oop[main:PhotoShop App] editor functions;
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        # Editor buttons
        editors = [
            # ("Brush", self.parent.brushTool), 
            ("Eraser", self.parent.eraserTool),
            ("Crop", self.parent.cropTool), ("Zoom in", self.parent.zoomIn),
            ("Zoom out", self.parent.zoomOut), ("Left", self.parent.rotate_left),
            ("Right", self.parent.rotate_left), ("Filter", self.parent.filterTool), ("Frame", self.parent.toggleFrame)
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
        # Clear previous options
        for i in reversed(range(self.brushOptionsLayout.count())):
            self.brushOptionsLayout.itemAt(i).widget().setParent(None)

        # Add small brush option
        smallBrushButton = QPushButton(QIcon('small2.png'), "img/small2.png")
        smallBrushButton.clicked.connect(lambda: self.parent.brushTool("small"))
        self.brushOptionsLayout.addWidget(smallBrushButton)

        # Add medium brush option
        mediumBrushButton = QPushButton(QIcon('medium2.png'), "img/medium2.png")
        mediumBrushButton.clicked.connect(lambda: self.parent.brushTool("medium"))
        self.brushOptionsLayout.addWidget(mediumBrushButton)

        # Add large brush option
        largeBrushButton = QPushButton(QIcon('large2.png'), "img/large2.png")
        largeBrushButton.clicked.connect(lambda: self.parent.brushTool("large"))
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


class PhotoshopApp(QMainWindow):
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

        # Canvas Widget
        # self.canvasWidget = CanvasWidget()

        # Frame Layout
        self.frameLayout = FrameLayout(self)

        # Tool Bar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        toolbar.addWidget(self.toolbarWidget)


        # Main Layout Setup
        centralWidget = QWidget()
        # self.setCentralWidget(self.centralWidget)

        # GUI Widgets
        self.file_list = QListWidget()
        self.image_label = QLabel("Picture Display Area")
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


        # Drop-down buttons on click mainButton
        brushButton = QPushButton("Brush")
        brushMenu = QMenu()

        smallBrushAction = QAction(QIcon('img/small.png'), "Small", self)
        smallBrushAction.triggered.connect(lambda: self.brushTool("small"))
        brushMenu.addAction(smallBrushAction)

        mediumBrushAction = QAction(QIcon('img/medium.png'), "Medium", self)
        mediumBrushAction.triggered.connect(lambda: self.brushTool("medium"))
        brushMenu.addAction(mediumBrushAction)

        largeBrushAction = QAction(QIcon('img/large.png'), "Large", self)
        largeBrushAction.triggered.connect(lambda: self.brushTool("large"))
        brushMenu.addAction(largeBrushAction)

        brushButton.setMenu(brushMenu)
        self.left_layout.addWidget(brushButton)

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

    def toggleFrame(self):
        if self.frameLayout.isVisible():
            self.frameLayout.hideFrame()
        else:
            self.frameLayout.showFrame()

    # oop ImageEditor
    def rotate_left(self):
        print("Rotated Left")

    def rotate_right(self):
        print("Rotated Right")

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

    def brightnessSlider(self):
        """Apply Brightness"""
        # Implement logic

    def contrastSlider(self):
        """Apply Contrast"""
        # Implement logic

    def zoomIn(self):
        # Implement zoom in functionality
        print("Zoom in")

    def zoomOut(self):
        # Implement zoom out functionality
        print("Zoom out")

    def pan(self):
        # Implement pan functionality
        print("Pan")

    def brushTool(self, size):
    # Logic to handle different brush sizes
        if size == "small":
            print("Small brush tool selected")
            # Add logic specific to the small brush tool here
        elif size == "medium":
            print("Medium brush tool selected")
            # Add logic specific to the medium brush tool here
        elif size == "large":
            print("Large brush tool selected")
            # Add logic specific to the large brush tool here
        else:
            print("Invalid brush size selected")

    

    def eraserTool(self):
        print("Eraser tool selected")

    def cropTool(self):
        print("Crop tool selected")
    
    def filterTool(self):
        print("Filter tool selected")



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PhotoshopApp()
    window.show()
    sys.exit(app.exec_())
