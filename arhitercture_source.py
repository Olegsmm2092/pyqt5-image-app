from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QMenuBar, QToolBar, QAction, QWidget,
    QFileDialog, QLabel, QPushButton, QLineEdit, QComboBox, QListWidget,
    QVBoxLayout, QHBoxLayout, QTextEdit, QMessageBox
)
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QPixmap
from src.core.image_processor import ImageProcessor
from src.core.side_panel_widget import SidePanelWidget


class MergedPhotoshopApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_processor = ImageProcessor()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Merged Photoshop App')
        self.setGeometry(100, 100, 900, 700)

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        # Main Layout
        self.main_layout = QHBoxLayout()
        self.left_layout = QVBoxLayout()
        self.right_layout = QVBoxLayout()

        # Image Display Area
        self.image_label = QLabel("Picture Display Area")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.right_layout.addWidget(self.image_label)

        # Side Panel Widget
        self.side_panel_widget = SidePanelWidget(self.image_processor, self)
        self.left_layout.addWidget(self.side_panel_widget)

        self.main_layout.addLayout(self.left_layout, 20)
        self.main_layout.addLayout(self.right_layout, 80)

        self.centralWidget.setLayout(self.main_layout)

    def load_image(self, path):
        self.image_processor.load_image(path)
        self.refresh_display()

    def refresh_display(self):
        if self.image_processor.image:
            qimage = self.convert_to_qimage(self.image_processor.image)
            pixmap = QPixmap.fromImage(qimage)
            self.image_label.setPixmap(pixmap)

    def convert_to_qimage(self, pil_image):
        pil_image = pil_image.convert("RGBA")
        data = pil_image.tobytes("raw", "RGBA")
        qimage = QImage(data, pil_image.width,
                        pil_image.height, QImage.Format_RGBA8888)
        return qimage


if __name__ == '__main__':
    app = QApplication([])
    window = MergedPhotoshopApp()
    window.show()
    app.exec_()
