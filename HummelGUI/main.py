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
