import os
from PyQt5.QtWidgets import QLabel, QMessageBox
from PyQt5.QtGui import QPixmap, QPainter, QPen, QImage, QFont
from PyQt5.QtCore import QPoint, Qt, QRect, QPointF
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
        self.brush_active = False
        self.last_point = QPoint()
        self.pen_color = Qt.black
        self.pen_size = 5

        # Add Text attributes
        self.add_text_active = False
        self.text_position = QPoint(10, 10)
        self.text = "Add Me"
        self.text_size = 14
        # self.text_font = QFont("Arial", self.text_size) # bug need to be insider func draw text on image to updated on event by slider moving
        self.text_font_name = "Arial"
        self.text_alignment = "top"
        # dinamically rotate before applying t final ver.
        self.rotation_text_angle = 0

        self.im = None
        self.original_image = None
        self.fullname = None
        self.im_name = None
        self.im_format = None
        self.crop_im = None
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

            self.drawing = False
            self.brush_active = False
            self.add_text_active = False
            self.last_point = None
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
            self.original_image = scaled_pixmap.copy()
            self.setPixmap(self.original_image)
        super().resizeEvent(event)

    def set_start_point(self, point):
        self.start_point = point
        self.update()  # Request a repaint

    def set_end_point(self, point):
        self.end_point = point
        self.update()  # Request a repaint

    def activate_brush(self, activate=True):
        """Activate or deactivate the brush tool."""
        self.brush_active = activate

    def set_pen_color(self, color):
        """Set the color of the brush"""
        self.pen_color = color

    def set_pen_size(self, size):
        self.pen_size = size

    def activate_add_text(self, activate=True):
        self.add_text_active = activate

    def set_text_on_image(self, text):
        self.text = text

    def set_text_font(self, font_name):
        self.text_font_name = font_name
        # self.text_font.setFamily(font_name)

    def set_text_size(self, size):
        self.text_size = size

    def set_text_rotation_angle(self, angle):
        self.rotation_text_angle = angle

    def set_text_position(self, position):
        self.text_alignment = position


    # заглушки
    def set_filter_brightness(self, value):
        value = None
        print(f'setted brightness to {value}')

    def set_filter_contrast(self, value):
        value = None
        print(f'setted contrast to {value}')

    def paintEvent(self, event):
        """Draw a rectangle when cropping"""
        super().paintEvent(event)
        if self.start_point and self.end_point:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.green, 2, Qt.SolidLine))
            rect = QRect(self.start_point, self.end_point)
            painter.drawRect(rect)

    def mousePressEvent(self, event):
        """Append Elif for other events by type operation"""
        if event.button() == Qt.LeftButton:
            if self.brush_active:
                self.drawing = True
                self.last_point = event.pos()
            else:
                self.start_point = event.pos()
                self.end_point = event.pos()
            self.update()

    def mouseMoveEvent(self, event):
        """Handle drawing or cropping based on mode"""
        if self.drawing and self.brush_active:
            if self.last_point is not None:
                self.draw_line_on_image(self.last_point, event.pos())
                self.last_point = event.pos()
        elif self.add_text_active and self.start_point:
            self.end_point = event.pos()
            self.update()
        elif self.start_point:
            self.end_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        """Handle mouse release for brush or cropping"""
        if event.button() == Qt.LeftButton:
            if self.brush_active:
                self.drawing = False
            elif self.add_text_active:
                self.end_point = event.pos()
                self.draw_text_on_image(self.text)
            else:
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

    def draw_line_on_image(self, start_point, end_point):
        """Draw a line on the image between two points adjusted for scaling."""
        self.scale_factor = min(
            self.width() / self.original_image.width(),
            self.height() / self.original_image.height()
        )

        x1, y1 = start_point.x(), start_point.y()
        x2, y2 = end_point.x(), end_point.y()

        left = int(min(x1, x2) / self.scale_factor)
        upper = int(min(y1, y2) / self.scale_factor)
        right = int(max(x1, x2) / self.scale_factor)
        lower = int(max(y1, y2) / self.scale_factor)

        painter = QPainter(self.original_image)
        pen = QPen(self.pen_color, self.pen_size,
                   Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)

        painter.drawLine(right, lower, left, upper)
        painter.end()

        self.setPixmap(self.original_image)
        self.update()

    def draw_text_on_image(self, text):
        """Draw a text on the image between two points adjusted for scaling."""
        if self.start_point and self.end_point:
            self.scale_factor = min(
                self.width() / self.original_image.width(),
                self.height() / self.original_image.height()
            )

            x1, y1 = self.start_point.x(), self.start_point.y()
            x2, y2 = self.end_point.x(), self.end_point.y()

            # need only first QPointF(left, upper)
            left = int(min(x1, x2) / self.scale_factor)
            upper = int(min(y1, y2) / self.scale_factor)
            right = int(max(x1, x2) / self.scale_factor)
            lower = int(max(y1, y2) / self.scale_factor)

            painter = QPainter(self.original_image)
            pen = QPen(self.pen_color)
            painter.setPen(pen)

            font = QFont("Arial", self.text_size)
            if self.text_font_name is not None:
                # else raise cant set family for font
                font.setFamily(self.text_font_name)
            painter.setFont(font)

            if self.text_alignment == "top":
                text_position = QPointF(left, upper)  # Example position
                painter.save()
                painter.translate(text_position)
                painter.rotate(self.rotation_text_angle)
                painter.translate(-text_position)  # Move back
                painter.drawText(text_position, self.text)
            elif self.text_alignment == 'center':
                painter.save()
                painter.rotate(self.rotation_text_angle)
                painter.drawText(left, upper, right - left, lower -
                                 upper, Qt.AlignCenter, text)
            else:
                raise Exception("Invalid position %s", self.alignment)

            # Restore the painter's original state
            painter.restore()

            painter.end()

            self.setPixmap(self.original_image)
            self.update()

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
