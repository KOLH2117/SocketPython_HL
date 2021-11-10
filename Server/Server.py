# Đồ án Socket Python 
# 20127459 - Lê Quốc Đạt
# 20127665 - Dương Quang Vinh
# Phần Server

from GUI.MainWindow import MainWindow
from PySide6.QtWidgets import QApplication
from SocketServer import SocketServer

class Server(SocketServer):
    def __init__(self):
        super().__init__()
        self.app = QApplication([])
        self.mainWindow = MainWindow("Server")
        self.mainWindow.show()

    def setGeometry(self,x,y,width,height):
        self.mainWindow.setGeometry(x,y,width,height)
    
    def run(self):
        self.app.exec()
        
if __name__ == "__main__":
    server = Server()
    server.setGeometry(100,100,200,200)
    server.run()

