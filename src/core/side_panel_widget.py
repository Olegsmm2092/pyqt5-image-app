# side_panel_widget.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSlider
from PyQt5.QtCore import Qt


class SidePanelWidget(QWidget):
    """взять отсюда в main но все еще хочется разделить чтобы работало
     и наполняло filters, here
     other in the other part
     для каждой категории свой oop widget;
       """
    def __init__(self, image_processor, parent=None):
        super().__init__(parent)
        self.image_processor = image_processor
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Brightness Slider
        self.brightnessSlider = QSlider(Qt.Horizontal)
        self.brightnessSlider.setRange(0, 200)
        self.brightnessSlider.setValue(100)  # 100% = no change
        self.brightnessSlider.valueChanged.connect(self.update_brightness)

        layout.addWidget(QLabel('Brightness'))
        layout.addWidget(self.brightnessSlider)

        # Contrast Slider
        self.contrastSlider = QSlider(Qt.Horizontal)
        self.contrastSlider.setRange(0, 200)
        self.contrastSlider.setValue(100)  # 100% = no change
        self.contrastSlider.valueChanged.connect(self.update_contrast)

        layout.addWidget(QLabel('Contrast'))
        layout.addWidget(self.contrastSlider)

        # Reset Button
        resetButton = QPushButton('Reset')
        resetButton.clicked.connect(self.reset_image)
        layout.addWidget(resetButton)

        self.setLayout(layout)

    def update_brightness(self, value):
        self.image_processor.adjust_brightness(value / 100)
        self.parent().refresh_display()

    def update_contrast(self, value):
        self.image_processor.adjust_contrast(value / 100)
        self.parent().refresh_display()

    def reset_image(self):
        self.image_processor.reset_image()
        self.parent().refresh_display()
