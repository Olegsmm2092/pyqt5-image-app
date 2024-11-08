from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtGui import QIcon

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
                                                 self.parent.filterTool), ("Frame", self.parent.toggle_frame)
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
