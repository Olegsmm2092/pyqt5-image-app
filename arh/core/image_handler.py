import os
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QPixmap, QPainter, QPen, QImage
from PyQt5.QtCore import Qt, QRect
from PIL import Image
from arh.utils.image_conversion import pil_to_qimage, qpixmap_to_pil


class ImageHandler:
    """ref. widgets.canvas выносим часть логики here // dont work wta
    Handles image-related operations such as loading, saving, cropping, and transformations."""

    def __init__(self, canvas):
        self.canvas = canvas

    def load_image(self, path):
        """Load an image from the given path."""
        if not os.path.exists(path):
            QMessageBox.warning(self.canvas, "File Not Found",
                                f"Image path does not exist: {path}")
            return None

        try:
            pil_image = Image.open(path)
            if "icc_profile" in pil_image.info:
                del pil_image.info['icc_profile']
            if pil_image.mode in ("RGBA", "P"):
                pil_image = pil_image.convert("RGB")
            return QPixmap.fromImage(pil_to_qimage(pil_image))
        except Exception as e:
            QMessageBox.critical(self.canvas, "Error",
                                 f"Failed to load image:\n{e}")
            return None

    def scale_image(self, pixmap, size):
        """Scale the image to fit the QLabel size while maintaining aspect ratio."""
        return pixmap.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def draw_rectangle(self, widget, start_point, end_point):
        """Draw a rectangle on the widget."""
        painter = QPainter(widget)
        painter.setPen(QPen(Qt.green, 2, Qt.SolidLine))
        rect = QRect(start_point, end_point)
        painter.drawRect(rect)

    def crop(self, start_point, end_point):
        """Crop the image based on start and end points."""
        pixmap = self.canvas.original_image
        if not pixmap:
            return None

        x1, y1 = start_point.x(), start_point.y()
        x2, y2 = end_point.x(), end_point.y()

        # Ensure valid coordinates
        if min(x1, x2) < 0 or min(y1, y2) < 0 or max(x1, x2) > pixmap.width() or max(y1, y2) > pixmap.height():
            QMessageBox.warning(self.canvas, "Invalid Crop",
                                "Coordinates out of bounds.")
            return None

        crop_coords = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
        pil_image = qpixmap_to_pil(pixmap)
        return pil_image.crop(crop_coords)

    def convert_to_pixmap(self, pil_image):
        """Convert a PIL image to QPixmap."""
        if pil_image.mode in ("RGBA", "P"):
            pil_image = pil_image.convert("RGB")
        q_image = pil_to_qimage(pil_image)
        return QPixmap.fromImage(q_image)

    def apply_grayscale(self, pixmap):
        """Convert the image to grayscale."""
        pil_image = qpixmap_to_pil(pixmap)
        gray_image = pil_image.convert("L")
        return gray_image

    def rotate(self, pixmap, degrees):
        """Rotate the image by the given degrees."""
        pil_image = qpixmap_to_pil(pixmap)
        return pil_image.rotate(degrees, expand=True)
