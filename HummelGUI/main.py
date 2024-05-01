"""
Description
-----------
Runs the applications, showing the TI Interface

Author
------
Gregor Dederichs, EPFL School of Life Sciences
"""

import sys
from PyQt6.QtWidgets import QApplication
import GUI

def main():
    # RUN APPLICATION
    app = QApplication(sys.argv)
    window = GUI.MainWindow()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
