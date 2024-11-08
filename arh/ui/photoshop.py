import os
from pathlib import Path
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QAction, QToolBar,
    QFileDialog, QMessageBox, QTextEdit)
from PyQt5.QtCore import Qt
from arh.widgets.canvas import Canvas
from arh.widgets.toolbar import ToolbarWidget
from arh.widgets.side_panel import SidePanelWidget
from arh.widgets.frame_layout import FrameLayout
from arh.utils.image_manager import ImageManager

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
        # Frame Layout
        # self.frameLayout = FrameLayout(self)
        self.frame = FrameLayout(self.image_label)

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
            ("Brush", self.toggle_brush),
            ("Add Text", lambda value: self.image_label.activate_add_text(True)),
            ("Add Text Off", lambda value: self.image_label.activate_add_text(False)),
            ("Frame", self.toggle_frame),
        ]
        for text, handler in filters:
            btn = QPushButton(text)
            btn.clicked.connect(handler)
            self.left_layout.addWidget(btn)

        self.right_layout.addWidget(self.image_label)
        self.frame_layout.addWidget(self.frame)

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

    def toggle_brush(self):
        if self.image_label.brush_active:
            self.image_label.activate_brush(False)
            print("brush Off")
        else:
            self.image_label.activate_brush(True)
            print("brush On")

    def toggle_frame(self):
        if self.frame.isVisible():
            self.frame.hideFrame()
        else:
            self.frame.showFrame()