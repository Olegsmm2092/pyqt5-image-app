# image_processor.py
from PIL import Image, ImageEnhance


class ImageProcessor:
    def __init__(self):
        self.image = None
        self.original_image = None

    def load_image(self, path):
        self.image = Image.open(path)
        self.original_image = self.image.copy()

    def save_image(self, path):
        if self.image:
            self.image.save(path)

    def reset_image(self):
        if self.original_image:
            self.image = self.original_image.copy()

    def adjust_brightness(self, value):
        enhancer = ImageEnhance.Brightness(self.image)
        self.image = enhancer.enhance(value)

    def adjust_contrast(self, value):
        enhancer = ImageEnhance.Contrast(self.image)
        self.image = enhancer.enhance(value)

    # Implement other image operations similarly...
