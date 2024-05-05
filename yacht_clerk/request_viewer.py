from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QMessageBox
import yacht_api, enum
from PyQt6.QtCore import Qt
import datetime


class RequestStatus(enum.Enum):
    new = 0
    allow = 1
    deny = 2


class RequestViewer:
    def __init__(self, ui: QtWidgets.QMainWindow) -> None:
        self.ui = ui
        self.start_ui()
        self.selectedReq = None


    def start_ui(self):
        uic.loadUi('request_viewer.ui', self.ui)
        self.ui.setWindowTitle("Запросы")
        self.ui.update_products_table = self.update_products_table
        self.ui.table_selection = self.table_selection
        self.ui.updateButton.clicked.connect(self.ui.update_products_table)
        self.ui.allow_request = self.allow_request
        self.ui.deny_request = self.deny_request
        self.ui.allowButton.clicked.connect(self.ui.allow_request)
        self.ui.denyButton.clicked.connect(self.ui.deny_request)
        self.update_products_table()


    def get_requests(self):
        status, resp = yacht_api.api_method('get_user_requests', {'all':'1'})

        if status == 200:
            resp['requests'].sort(key=lambda x: x['id'], reverse=True)
            return resp['requests']
        
        QMessageBox.about(self, "Error", resp['error'])
        return []
    

    def table_selection(self, row, _):
        table: QtWidgets.QTableWidget = self.ui.requestsTableWidget
        self.selectedReq = int(table.item(row, 0).text())
        self.ui.labelSelected.setText(f"Выбран запрос: {self.selectedReq}")


    def allow_request(self):
        self.change_status('allow_request')


    def deny_request(self):
        self.change_status('deny_request')


    def change_status(self, method):
        if self.selectedReq is None:
            QMessageBox.about(self.ui, "Error", "Запрос не выбран!")
            return
        
        data = {
            'request_id':self.selectedReq,
            'answer':self.ui.answerEdit.text()
        }

        status, resp = yacht_api.api_method(method, data_json=data)

        if status == 200:
            QMessageBox.about(self.ui, "Статус", "Статус изменен!")
            self.update_products_table()
            self.ui.answerEdit.setText("")

        else:
            QMessageBox.about(self.ui, "Error", resp['error'])


    def update_products_table(self):
        self.selectedReq = None
        self.ui.labelSelected.setText("")
        table: QtWidgets.QTableWidget = self.ui.requestsTableWidget
        table.clear()
        table.cellClicked.connect(self.ui.table_selection)
        table.setRowCount(0)
        table.setColumnCount(8)
        table.verticalHeader().setVisible(False)

        labels = ['ID', 'Тип', 'Статус', 'Яхта', 'Пользователь', 'Время', 'Время До', 'Ответ']

        table.setHorizontalHeaderLabels(labels)

        reqs = self.get_requests()
        i = 0
        for req in reqs:
            status = RequestStatus(req['status'])

            if status == RequestStatus.new:
                status = 'Новый'
                if not self.ui.newCheckBox.isChecked():
                    continue

            elif status == RequestStatus.allow:
                status = 'Принят'
                if not self.ui.allowCheckBox.isChecked():
                    continue

            elif status == RequestStatus.deny:
                status = 'Отклонен'
                if not self.ui.denyCheckBox.isChecked():
                    continue

            table.insertRow(i)

            item_id = QtWidgets.QTableWidgetItem(str(req['id']))
            item_id.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 0, item_id)

            if req['get']:
                to_time = datetime.datetime.fromtimestamp(req['to_time']).isoformat()
                type_req = 'Аренда'

            else:
                to_time = ""
                type_req = 'Сдача'

            item_get = QtWidgets.QTableWidgetItem(type_req)
            item_get.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 1, item_get)

            item_status = QtWidgets.QTableWidgetItem(status)
            item_status.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 2, item_status)

            item_yacht = QtWidgets.QTableWidgetItem(req['yacht']['name'])
            item_yacht.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 3, item_yacht)

            item_yacht = QtWidgets.QTableWidgetItem(req['user'])
            item_yacht.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 4, item_yacht)

            item_time = QtWidgets.QTableWidgetItem(datetime.datetime.fromtimestamp(req['time_req']).isoformat())
            item_time.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 5, item_time)

            item_time_to = QtWidgets.QTableWidgetItem(to_time)
            item_time_to.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 6, item_time_to)

            item_answer = QtWidgets.QTableWidgetItem(req['answer'])
            item_answer.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 7, item_answer)

            i += 1

        table.resizeColumnsToContents()