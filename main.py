# coding=utf8
import sys
import os
import requests

from PySide2 import QtCore, QtGui
from PySide2.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QListView, QAbstractItemView,QLabel
from PySide2.QtGui import QStandardItemModel
from twitch import Twitch, WebEngineUrlRequestInterceptor
from PySide2.QtWebEngineWidgets import QWebEngineProfile
from PySide2.QtCore import Slot

from widgets.followed_item import FollowedItem
from widgets.styled_item_delegate import StyledItemDelegate


def main():
    app = QApplication([])
    interceptor = WebEngineUrlRequestInterceptor()
    QWebEngineProfile.defaultProfile().setUrlRequestInterceptor(interceptor)

    twitch = Twitch()
    if not twitch.check_auth():
        print('no auth')
        twitch.authenticate()
    else:
        print('auth babby')

    class Authenticator(QWidget):
        def __init__(self):
            super().__init__()
            layout = QVBoxLayout()
            self.label = QLabel("Another Window")
            layout.addWidget(self.label)
            self.setLayout(layout)
            twitch = Twitch() 
            if not twitch.check_auth():
                print('no auth')
                twitch.authenticate()
            else:
                print('auth babby')
        


    class MainWindow(QMainWindow, QtCore.QObject):
        twitch = Twitch()
        list_view = QListView(
            editTriggers=QAbstractItemView.NoEditTriggers
        )

        def __init__(self):

            super().__init__()
            stylesheet_path = os.path.join(os.path.dirname(__file__), 'styles/style.qss')
            with open(stylesheet_path, 'r') as f:
                self.setStyleSheet(f.read())
            self.setWindowTitle("Itchification")
            if self.twitch.check_auth(): # need to reverse this logic
                self.twitch.get_followed()
                self.twitch.siggy.connect(self._my_slot)
                model = QStandardItemModel(self.list_view)
                followed_list = self.twitch.followed
                for r in followed_list:
                    image_file = 'thumbnails/' + r['display_name'] + '.jpg'
                    print(QtCore.QFile.exists(image_file))
                    if not QtCore.QFile.exists(image_file):
                        with open(image_file, 'wb') as g:
                            g.write(requests.get(r["profile_image_url"]).content)

                    channel_url = 'https://twitch.tv/' + r['login']
                    it = FollowedItem(title=r['display_name'], description=r['description'], icon=QtGui.QIcon(image_file),url=channel_url)
                    model.appendRow(it)

                self.twitch.get_live_streams()
                self.list_view.setSpacing(5)
                self.list_view.activated.connect(self.on_item_changed)  # .activated is sent when doubleclicked or enter key pressed
                self.list_view.setItemDelegate(StyledItemDelegate(self.list_view))
                self.list_view.setModel(model)
            
                layout = QVBoxLayout()
                layout.addWidget(self.list_view)
                widget = QWidget()
                widget.setLayout(layout)
                self.setCentralWidget(widget)
                self.setMinimumSize(300, 800)
            else:
                self.twitch.authenticate()

        @QtCore.Slot(QtCore.QModelIndex)
        def on_item_changed(self, index):
            it = index.model().itemFromIndex(index)
            if it is None:
                return
            channel_link = QtCore.QUrl(it.url)
            if not QtGui.QDesktopServices.openUrl(channel_link):
                QtGui.QMessageBox.warning(None, 'Open Url', 'Could not open url')
            print("clicked baby:", it.title, it.description,it.url)

        @Slot()
        def _my_slot(self):
            print('new live streamer from main.py')

    # window = MainWindow()
    # window.show()
    # starter = Authenticator()
    # starter.show()
    app.exec_()


if __name__ == '__main__':
    sys.exit(main())
