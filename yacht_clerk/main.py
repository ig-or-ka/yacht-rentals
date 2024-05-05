from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QMessageBox
import sys, yacht_api, request_viewer


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()        
        self.show()
        self.start_ui()


    def start_ui(self):
        uic.loadUi('start.ui', self)
        self.setWindowTitle("Вход")
        self.loginButton.clicked.connect(self.login_clicked)


    def login_clicked(self):
        data = {
            'username':self.loginEdit.text(),
            'password':self.passwordEdit.text()
        }
        status, resp = yacht_api.api_method('login', data_json=data)

        if status != 200:
            QMessageBox.about(self, "Error", resp['msg'])

        elif resp['post'] != 1:
            QMessageBox.about(self, "Error", "Пользователь не является клерком")

        else:
            yacht_api.VARS.token = resp['access_token']
            request_viewer.RequestViewer(self)


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec()