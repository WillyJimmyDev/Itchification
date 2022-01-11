import sys
import os
from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QListView, QMessageBox
from db.database import ItchificationDB
from PySide2.QtGui import QStandardItemModel, QStandardItem
from twitch import Twitch, WebEngineUrlRequestInterceptor
from PySide2.QtWebEngineWidgets import QWebEngineProfile

if __name__ == '__main__':
    app = QApplication([])
    interceptor = WebEngineUrlRequestInterceptor()
    QWebEngineProfile.defaultProfile().setUrlRequestInterceptor(interceptor)

    class MainWindow(QMainWindow):

        def __init__(self):
            self.twitch = Twitch()
            self.dbconn = ItchificationDB()
            super().__init__()
            stylesheet_path = os.path.join(os.path.dirname(__file__), 'styles/style.qss')
            with open(stylesheet_path, 'r') as f:
                self.setStyleSheet(f.read())
            self.setWindowTitle("Itchification")
            list_widget = QListView()
            model = QStandardItemModel(list_widget)
            followed_list = self.twitch.get_followed_list()
            for f in followed_list:
                item = QStandardItem(f["display_name"])
                model.appendRow(item)

            list_widget.clicked.connect(self.on_item_changed)
            list_widget.setModel(model)
            layout = QVBoxLayout()
            layout.addWidget(list_widget)
            widget = QWidget()
            widget.setLayout(layout)
            self.setCentralWidget(widget)
            self.setMinimumSize(300, 800)

        def on_item_changed(x):
            print(str(x.list_widget))


    window = MainWindow()
    followers = window.twitch.get_followed_list()
    window.show()

    sys.exit(app.exec_())
