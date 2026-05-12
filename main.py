"""
Investigator X – Cyber Recon Toolkit
Entry point
"""

import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtCore import Qt
from gui.main_window import MainWindow
from gui.styles import GLOBAL_STYLESHEET


def main():
    # Enable High-DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("Investigator X")
    app.setOrganizationName("CyberRecon")

    # Apply global dark stylesheet
    app.setStyleSheet(GLOBAL_STYLESHEET)

    # Set application-wide font
    font = QFont("Consolas", 10)
    if not font.exactMatch():
        font = QFont("Courier New", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
