import sys
import os

# Get the root directory of your project (two levels up from this file)
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the root directory to sys.path
sys.path.append(root_dir)

from arh.ui.photoshop import PhotoshopApp
from PyQt5.QtWidgets import QApplication


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = PhotoshopApp()
    ex.show()
    sys.exit(app.exec_())