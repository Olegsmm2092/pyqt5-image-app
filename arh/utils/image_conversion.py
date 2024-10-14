from PIL import Image
from PyQt5.QtGui import QImage
from PyQt5.QtCore import QBuffer, QIODevice
import numpy as np
import io

def qpixmap_to_pil(qpixmap):
        """Convert QPixmap to PIL Image."""
        q_image = qpixmap.toImage()
        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        q_image.save(buffer, "PNG")
        pil_image = Image.open(io.BytesIO(buffer.data()))
        return pil_image

def pil_to_qimage(pil_image, qimage_format=QImage.Format_RGB888):
    """Convert a PIL image to QImage."""
    data = np.array(pil_image)
    if len(data.shape) == 2:  # to gray
        height, width = data.shape
        bytes_per_line = width
    elif len(data.shape) == 3:  # to rgb
        height, width, channel = data.shape
        bytes_per_line = 3 * width
    q_image = QImage(data.data, width, height,
                        bytes_per_line, qimage_format)
    return q_image