# coding=utf8
import sys
import os
from pathlib import Path
import requests

from PySide2 import QtCore, QtGui
from PySide2.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QListView
from PySide2.QtGui import QStandardItemModel, QStandardItem, QIcon
from twitch import Twitch, WebEngineUrlRequestInterceptor
from PySide2.QtWebEngineWidgets import QWebEngineProfile
from PySide2.QtCore import QUrl, Signal, QObject, Slot


def main():
    app = QApplication([])
    interceptor = WebEngineUrlRequestInterceptor()
    QWebEngineProfile.defaultProfile().setUrlRequestInterceptor(interceptor)

    class MainWindow(QMainWindow, QtCore.QObject):
        twitch = Twitch()
        list_widget = QListView()

        def __init__(self):

            super().__init__()
            stylesheet_path = os.path.join(os.path.dirname(__file__), 'styles/style.qss')
            with open(stylesheet_path, 'r') as f:
                self.setStyleSheet(f.read())
            self.setWindowTitle("Itchification")
            model = QStandardItemModel(self.list_widget)
            followed_list = self.twitch.followed
            for f in followed_list:
                display_name = f["display_name"]
                image_file = 'thumbnails/' + display_name + '.jpg'
                if not Path(image_file).is_file():
                    with open(image_file, 'wb') as g:
                        g.write(requests.get(f["profile_image_url"]).content)
                item = QStandardItem(display_name)
                item.setData("https://twitch.tv/" + display_name, 257)  # 257 refers to a custom user role enum
                item.setIcon(QIcon(image_file))
                item.setEditable(False)
                model.appendRow(item)

            self.twitch.get_live_streams()
            self.list_widget.activated.connect(self.on_item_changed)  # .activated is sent when doubleclicked or enter key pressed
            self.list_widget.setModel(model)
            layout = QVBoxLayout()
            layout.addWidget(self.list_widget)
            widget = QWidget()
            widget.setLayout(layout)
            self.setCentralWidget(widget)
            self.setMinimumSize(300, 800)

        @staticmethod
        def on_item_changed(index):
            # print(index.model().itemFromIndex(index).text())
            url = index.model().itemFromIndex(index).data()
            channel_link = QtCore.QUrl(url)
            if not QtGui.QDesktopServices.openUrl(channel_link):
                QtGui.QMessageBox.warning(None, 'Open Url', 'Could not open url')

        @Slot()
        def updated_followed():
            print("hello")

    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    sys.exit(main())
