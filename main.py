import sys
import os

from PySide2 import QtCore, QtGui
from PySide2.QtCore import QUrl
from PySide2.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PySide2.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QListView, QMessageBox
from db.database import ItchificationDB
from PySide2.QtGui import QStandardItemModel, QStandardItem, QIcon, QPixmap
from twitch import Twitch, WebEngineUrlRequestInterceptor
from PySide2.QtWebEngineWidgets import QWebEngineProfile

if __name__ == '__main__':
    app = QApplication([])
    interceptor = WebEngineUrlRequestInterceptor()
    QWebEngineProfile.defaultProfile().setUrlRequestInterceptor(interceptor)

    class MainWindow(QMainWindow):

        def __init__(self):
            self.nam = QNetworkAccessManager()
            self.item_icon = QIcon()

            self.twitch = Twitch()
            self.dbconn = ItchificationDB()
            super().__init__()
            stylesheet_path = os.path.join(os.path.dirname(__file__), 'styles/style.qss')
            with open(stylesheet_path, 'r') as f:
                self.setStyleSheet(f.read())
            self.setWindowTitle("Itchification")
            self.list_widget = QListView()
            model = QStandardItemModel(self.list_widget)
            followed_list = self.twitch.get_followed_list()
            for f in followed_list:
                display_name = f["display_name"]
                icon = QtCore.QUrl(f["profile_image_url"])

                item = QStandardItem(display_name)
                self.nam.finished.connect(self.set_item_icon)
                self.nam.get(QNetworkRequest(icon))
                item.setData("https://twitch.tv/" + display_name, 257)  # 257 refers to a custom user role enum
                print(self.item_icon)  # null
                item.setIcon(self.item_icon)
                model.appendRow(item)

            self.list_widget.clicked.connect(self.on_item_changed)
            self.list_widget.setModel(model)
            layout = QVBoxLayout()
            layout.addWidget(self.list_widget)
            widget = QWidget()
            widget.setLayout(layout)
            self.setCentralWidget(widget)
            self.setMinimumSize(300, 800)

        @staticmethod
        def on_item_changed(index):
            print(index.model().itemFromIndex(index).text())
            url = index.model().itemFromIndex(index).data()
            channel_link = QtCore.QUrl(url)
            if not QtGui.QDesktopServices.openUrl(channel_link):
                QtGui.QMessageBox.warning(None, 'Open Url', 'Could not open url')

        def set_item_icon(self, http_response):
            pixmap = QPixmap()
            pixmap.loadFromData(http_response.readAll())
            self.item_icon = QIcon(pixmap)


    window = MainWindow()
    followers = window.twitch.get_followed_list()
    window.show()

    sys.exit(app.exec_())
