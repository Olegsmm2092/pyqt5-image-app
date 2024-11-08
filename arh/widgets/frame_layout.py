from PyQt5.QtWidgets import (
    QVBoxLayout, QPushButton,
    QSlider, QFrame, QLabel,
    QColorDialog, QLineEdit, QFontComboBox,
    QRadioButton, QButtonGroup)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class FrameLayout(QFrame):
    def __init__(self, canvas, parent=None):
        super().__init__(parent)
        self.canvas = canvas
        self.top_radio = None
        self._initialize_ui()

    def _initialize_ui(self):
        self._setup_frame_style()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Sliders:"))

        # Add text size slider
        self._add_text_size_slider(layout)
        # Add radio buttons for text position
        self._add_text_position_options(layout)
        # Add text input and text options
        self._add_text_input(layout)
        # Add color picker button
        self._add_color_picker(layout)

        # Add brush size slider
        self._add_brush_size_slider(layout)

        # Finalize layout setup
        self.setLayout(layout)
        self.hide()  # Initially hide the fram

    def _setup_frame_style(self):
        """Sets up the frame's visual style."""
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(2)

    def _add_brightness_filter_slider(self, layout):
        """Adds a slider to control text size."""
        self.filter_brightness_slider = self._create_slider(
            min_val=-100, max_val=100, default_val=20, tick_intverval=5)
        self.filter_brightness_slider.valueChanged.connect(
            lambda value: self.canvas.set_filter_brightness(value)
        )
        layout.addWidget(self.filter_brightness_slider)

    def _add_contrast_filter_slider(self, layout):
        """Adds a slider to control text size."""
        self.filter_contrast_slider = self._create_slider(
            min_val=-100, max_val=100, default_val=20, tick_interval=5)
        self.filter_contrast_slider.valueChanged.connect(
            lambda value: self.canvas.set_filter_contrast(value)
        )
        layout.addWidget(self.filter_contrast_slider)

        colorAdjustButton = QPushButton('Apply')
        layout.addWidget(colorAdjustButton)

    def _add_brush_size_slider(self, layout):
        """Adds a slider to control brush size."""
        self.brush_size_slider = self._create_slider(
            min_val=1, max_val=20, default_val=5)
        self.brush_size_slider.valueChanged.connect(
            lambda value: self.canvas.set_pen_size(value)
        )
        layout.addWidget(QLabel("Pen Size"))
        layout.addWidget(self.brush_size_slider)

    def _add_color_picker(self, layout):
        """Adds a button for picking the pen color."""
        color_button = QPushButton("Pick Color")
        color_button.clicked.connect(
            lambda: self.canvas.set_pen_color(QColorDialog.getColor())
        )
        layout.addWidget(color_button)

    def _add_text_input(self, layout):
        """Adds text input field, font selection, and text addition button."""
        self.text_input = QLineEdit()
        text_button = QPushButton("Add Text")
        text_button.clicked.connect(self._apply_text_to_canvas)

        font_input = QFontComboBox()
        font_input.setCurrentFont(QFont("Arial"))
        font_input.currentFontChanged.connect(
            lambda font: self.canvas.set_text_font(font.family())
        )

        layout.addWidget(self.text_input)
        layout.addWidget(text_button)
        layout.addWidget(font_input)

    def _add_text_size_slider(self, layout):
        """Adds a slider to control text size."""
        self.text_size_slider = self._create_slider(
            min_val=10, max_val=100, default_val=20, tick_interval=5)
        self.text_size_slider.valueChanged.connect(
            lambda value: self.canvas.set_text_size(value)
        )
        layout.addWidget(self.text_size_slider)

    def _add_text_position_options(self, layout):
        """Adds radio buttons for selecting text position."""
        self.top_radio = QRadioButton("Top")
        self.center_radio = QRadioButton("Center")
        self.top_radio.setChecked(True)

        # Connect radio buttons to the handler to update text position dynamically
        self.top_radio.toggled.connect(self._update_text_position)
        self.center_radio.toggled.connect(self._update_text_position)

        radio_group = QButtonGroup(self)
        radio_group.addButton(self.top_radio)
        radio_group.addButton(self.center_radio)

        layout.addWidget(self.top_radio)
        layout.addWidget(self.center_radio)

    def _create_slider(self, min_val, max_val, default_val, tick_interval=1):
        """Helper method to create a standardized slider."""
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default_val)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setTickInterval(tick_interval)
        return slider

    def _apply_text_to_canvas(self):
        text = self.text_input.text()
        self.canvas.set_text_on_image(text)
        # position = "top" if self.top_radio.isChecked() else "center"
        # self.canvas.set_text_position(position) # fix to do dinamically like font, size
        self.canvas.activate_add_text(True)

    def _update_text_position(self):
        """Updates the text position dynamically based on the selected radio button."""
        position = "top" if self.top_radio.isChecked() else "center"
        self.canvas.set_text_position(position)

    def showFrame(self):
        """Displays the frame."""
        self.show()

    def hideFrame(self):
        """Hides the frame."""
        self.hide()
