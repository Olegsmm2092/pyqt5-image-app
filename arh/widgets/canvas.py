import os
from PyQt5.QtWidgets import QLabel, QMessageBox
from PyQt5.QtCore import QPoint, Qt, QRect
from PyQt5.QtGui import QPixmap, QPainter, QPen, QImage
from PIL import Image
from arh.utils.image_conversion import pil_to_qimage, qpixmap_to_pil

from arh.core.image_manager import ImageManager

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

            q_image = pil_to_qimage(pil_image)

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
                pil_image = qpixmap_to_pil(self.original_image)
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

            q_image = pil_to_qimage(pillow_image)
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
            pil_image = qpixmap_to_pil(self.original_image)
            rotated_pil_image = pil_image.rotate(90, expand=True)
            self.show_edited_image(rotated_pil_image)

    def apply_rotate_right(self):
        if self.original_image:
            pil_image = qpixmap_to_pil(self.original_image)
            rotated_pil_image = pil_image.rotate(-90, expand=True)
            self.show_edited_image(rotated_pil_image)
