
from PyQt6.QtWidgets import QApplication
import sys

from MainWindow import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    
    sys.exit(app.exec())