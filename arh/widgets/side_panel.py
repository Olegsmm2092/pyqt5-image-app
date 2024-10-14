from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton)

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
