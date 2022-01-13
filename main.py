import sys
import os
from pathlib import Path

import requests

from PySide2 import QtCore, QtGui
from PySide2.QtNetwork import QNetworkAccessManager
from PySide2.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QListView
from db.database import ItchificationDB
from PySide2.QtGui import QStandardItemModel, QStandardItem, QIcon
from twitch import Twitch, WebEngineUrlRequestInterceptor
from PySide2.QtWebEngineWidgets import QWebEngineProfile

if __name__ == '__main__':
    app = QApplication([])
    interceptor = WebEngineUrlRequestInterceptor()
    QWebEngineProfile.defaultProfile().setUrlRequestInterceptor(interceptor)

    class MainWindow(QMainWindow):

        def __init__(self):
            self.nam = QNetworkAccessManager()

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
                image_file = 'thumbnails/' + display_name + '.jpg'

                item = QStandardItem(display_name)
                if not Path(image_file).is_file():
                    g = open(image_file, 'wb')
                    g.write(requests.get(f["profile_image_url"]).content)
                    g.close()

                item.setData("https://twitch.tv/" + display_name, 257)  # 257 refers to a custom user role enum
                item.setIcon(QIcon(image_file))
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


    window = MainWindow()
    followers = window.twitch.get_followed_list()
    window.show()

    sys.exit(app.exec_())
