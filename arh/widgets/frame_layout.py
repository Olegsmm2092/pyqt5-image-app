from PyQt5.QtWidgets import (
    QVBoxLayout, QPushButton,
    QSlider, QFrame, QLabel)
from PyQt5.QtCore import Qt

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
