from PySide6.QtWidgets import QApplication,QPushButton, QLabel,QWidget, QMainWindow
from PySide6.QtCore import Slot

class MainWindow(QMainWindow):
    def __init__(self, title = "MainWindow"):
        super().__init__()
        self.setWindowTitle(title)
        self.button = QPushButton("Click me")
        self.button.show()
        self.setCentralWidget(self.button)
    
    def set_clicked(self, func):
        self.button.clicked.connect(func)   
    
    def show_window(self):
        self.show()
    
     