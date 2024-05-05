from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QMessageBox
import yacht_api, enum
from PyQt6.QtCore import Qt
import datetime, time


class RequestStatus(enum.Enum):
    new = 0
    allow = 1
    deny = 2


class RequestCreator:
    def __init__(self, ui: QtWidgets.QMainWindow) -> None:
        self.ui = ui
        self.current_yacht_id = None
        self.start_ui()


    def start_ui(self):
        uic.loadUi('request_creator.ui', self.ui)
        self.ui.setWindowTitle("Запросы")
        self.ui.update_products_table = self.update_products_table
        self.ui.updateButton.clicked.connect(self.ui.update_products_table)
        self.ui.add_balance = self.add_balance
        self.ui.addBalanceButton.clicked.connect(self.ui.add_balance)
        self.ui.create_return_request = self.create_return_request
        self.ui.returnYachtButton.clicked.connect(self.ui.create_return_request)
        self.ui.create_yacht_request = self.create_yacht_request
        self.ui.createReqButton.clicked.connect(self.ui.create_yacht_request)
        self.update_products_table()


    def create_yacht_request(self):
        try:
            period = int(self.ui.periodEdit.text())

        except:
            QMessageBox.about(self.ui, "Error", "Укажите число!")
            return
        
        yachtsBox: QtWidgets.QComboBox = self.ui.comboBox

        data = {
            'yacht':int(yachtsBox.currentData()),
            'from_time':time.time(),
            'to_time':time.time() + period*24*60*60
        }

        status, resp = yacht_api.api_method('create_yacht_request', data_json=data)

        if status == 200:
            self.update_products_table()
            QMessageBox.about(self.ui, "Готово", "Запрос создан!")

        else:
            QMessageBox.about(self.ui, "Error", resp['error'])


    def create_return_request(self):
        status, resp = yacht_api.api_method('create_back_request')

        if status == 200:
            self.update_products_table()
            QMessageBox.about(self.ui, "Готово", "Запрос на возврат создан!")

        else:
            QMessageBox.about(self.ui, "Error", resp['error'])


    def get_yachts(self):
        table: QtWidgets.QTableWidget = self.ui.tableWidget
        table.clear()
        table.setRowCount(0)
        table.setColumnCount(2)
        table.verticalHeader().setVisible(False)

        labels = ['Название', 'Цена за сутки']
        table.setHorizontalHeaderLabels(labels)

        status, resp = yacht_api.api_method('get_available_yachts')

        if status == 200:
            yachtsBox: QtWidgets.QComboBox = self.ui.comboBox
            yachtsBox.clear()

            for i, yacht in enumerate(resp['yachts']):
                yachtsBox.addItem(yacht['name'], yacht['id'])
                table.insertRow(i)

                item_name = QtWidgets.QTableWidgetItem(yacht['name'])
                item_name.setFlags(Qt.ItemFlag.ItemIsEnabled)
                table.setItem(i, 0, item_name)

                item_price = QtWidgets.QTableWidgetItem(str(yacht['price']))
                item_price.setFlags(Qt.ItemFlag.ItemIsEnabled)
                table.setItem(i, 1, item_price)

        table.resizeColumnsToContents()


    def add_balance(self):
        try:
            balance = int(self.ui.lineEdit.text())

        except:
            QMessageBox.about(self.ui, "Error", "Укажите число!")
            return
        
        status, _ = yacht_api.api_method("add_balance", {'balance':balance})

        if status == 200:
            self.get_user_info()
            QMessageBox.about(self.ui, "Готово", "Баланс успешно пополнен!")


    def get_requests(self):
        status, resp = yacht_api.api_method('get_user_requests')

        if status == 200:
            resp['requests'].sort(key=lambda x: x['id'], reverse=True)
            return resp['requests']
        
        QMessageBox.about(self.ui, "Error", resp['error'])
        return []
    

    def get_user_info(self):
        status, resp = yacht_api.api_method('get_user_info')

        if status == 200:
            self.ui.labelBalance.setText(str(resp['balance']))
            
            if resp['current_yacht'] is None:
                self.current_yacht_id = None
                self.ui.labelCurrentYacht.setText("отсутствует")

            else:
                self.current_yacht_id = resp['current_yacht']['id']
                self.ui.labelCurrentYacht.setText(resp['current_yacht']['name'])
    

    def update_products_table(self):
        self.get_yachts()
        self.get_user_info()

        table: QtWidgets.QTableWidget = self.ui.requestsTableWidget
        table.clear()
        table.setRowCount(0)
        table.setColumnCount(7)
        table.verticalHeader().setVisible(False)

        labels = ['ID', 'Тип', 'Статус', 'Яхта', 'Время', 'Время До', 'Ответ']

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

            item_time = QtWidgets.QTableWidgetItem(datetime.datetime.fromtimestamp(req['time_req']).isoformat())
            item_time.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 4, item_time)

            item_time_to = QtWidgets.QTableWidgetItem(to_time)
            item_time_to.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 5, item_time_to)

            item_answer = QtWidgets.QTableWidgetItem(req['answer'])
            item_answer.setFlags(Qt.ItemFlag.ItemIsEnabled)
            table.setItem(i, 6, item_answer)

            i += 1

        table.resizeColumnsToContents()