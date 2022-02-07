# coding=utf8
import sys
import os
from time import sleep
import requests

from PySide2 import QtCore, QtGui
from PySide2.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QListView, QAbstractItemView,QLabel
from PySide2.QtGui import QStandardItemModel
from twitch import Twitch, WebEngineUrlRequestInterceptor
from PySide2.QtWebEngineWidgets import QWebEngineProfile
from PySide2.QtCore import Slot, QTimer

from widgets.followed_item import FollowedItem
from widgets.styled_item_delegate import StyledItemDelegate


def main():
    app = QApplication([])
    interceptor = WebEngineUrlRequestInterceptor()
    QWebEngineProfile.defaultProfile().setUrlRequestInterceptor(interceptor)
    twitch = Twitch()
    timer = QTimer()
    timer.timeout.connect(twitch.get_followed)
    timer.start(10000)

    class MainWindow(QMainWindow, QtCore.QObject):
        global twitch
        list_view = QListView(
            editTriggers=QAbstractItemView.NoEditTriggers
        )

        def __init__(self):

            super().__init__()
            stylesheet_path = os.path.join(os.path.dirname(__file__), 'styles/style.qss')
            with open(stylesheet_path, 'r') as f:
                self.setStyleSheet(f.read())
            self.setWindowTitle("Itchification")
            
            twitch.get_followed()
            twitch.siggy.connect(self._my_slot)
            self.model = QStandardItemModel(self.list_view)
            # self.model.setData()
            followed_list = twitch.followed
            followed_list.sort(key=lambda l: (-l['live'],l['display_name'].casefold())) # sort by live status
            
            # needs to be in a callable function to run on signal from timer timeout
            for r in followed_list:
                image_file = 'thumbnails/' + r['display_name'] + '.jpg'
                print(QtCore.QFile.exists(image_file))
                if not QtCore.QFile.exists(image_file):
                    with open(image_file, 'wb') as g:
                        g.write(requests.get(r["profile_image_url"]).content)

                channel_url = 'https://twitch.tv/' + r['login']
                it = FollowedItem(title=r['display_name'], description=r['description'], icon=QtGui.QIcon(image_file),url=channel_url, live=r["live"])
                self.model.appendRow(it)

            self.list_view.setSpacing(1)
            self.list_view.activated.connect(self.on_item_changed)  # .activated is sent when doubleclicked or enter key pressed
            self.list_view.setItemDelegate(StyledItemDelegate(self.list_view))
            self.list_view.setModel(self.model)
        
            layout = QVBoxLayout()
            layout.addWidget(self.list_view)
            widget = QWidget()
            widget.setLayout(layout)
            self.setCentralWidget(widget)
            self.setMinimumSize(300, 800)

        @QtCore.Slot(QtCore.QModelIndex)
        def on_item_changed(self, index):
            it = index.model().itemFromIndex(index)
            if it is None:
                return
            channel_link = QtCore.QUrl(it.url)
            if not QtGui.QDesktopServices.openUrl(channel_link):
                QtGui.QMessageBox.warning(None, 'Open Url', 'Could not open url')
            print("clicked baby:", it.title, it.description,it.url)

        @QtCore.Slot()
        def _my_slot(self):
            print('updating the model hopefully')
            # self.list_view.setModel(self.model)

    if not twitch.check_auth():
        print('no auth')
        twitch.authenticate()
        sleep(5) # need to sort out the race condition
        print(twitch.twitch_token)
        # del twitch.browser
        # sleep(5)
        # window = MainWindow()
        # window.show()
    else:
        print('we have auth baby')
        window = MainWindow()
        window.show()

    app.exec_()


if __name__ == '__main__':
    sys.exit(main())
