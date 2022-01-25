# coding=utf8
import sys
import os
import requests

from PySide2 import QtCore, QtGui
from PySide2.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QListView, QAbstractItemView
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
            self.twitch.siggy.connect(self._my_slot)
            model = QStandardItemModel(self.list_view)
            followed_list = self.twitch.followed
            for r in followed_list:
                image_file = 'thumbnails/' + r['display_name'] + '.jpg'
                print(QtCore.QFile.exists(image_file))
                if not QtCore.QFile.exists(image_file):
                    with open(image_file, 'wb') as g:
                        g.write(requests.get(r["profile_image_url"]).content)

                # TODO add url parameter in function call
                it = FollowedItem(title=r['display_name'], description=r['description'], icon=QtGui.QIcon(image_file),)
                model.appendRow(it)

            self.twitch.get_live_streams()
            self.list_view.setSpacing(5)
            self.list_view.activated.connect(self.on_clicky)  # .activated is sent when doubleclicked or enter key pressed
            self.list_view.setItemDelegate(StyledItemDelegate(self.list_view))
            self.list_view.setModel(model)
        
            layout = QVBoxLayout()
            layout.addWidget(self.list_view)
            widget = QWidget()
            widget.setLayout(layout)
            self.setCentralWidget(widget)
            self.setMinimumSize(300, 800)

        @staticmethod
        def on_item_changed(index):
            # url = index.model().itemFromIndex(index).data()
            # channel_link = QtCore.QUrl(url)
            # if not QtGui.QDesktopServices.openUrl(channel_link):
            #     QtGui.QMessageBox.warning(None, 'Open Url', 'Could not open url')
            it = index.model.itemFromIndex(index)
            if it is None:
                return
            print("clicked:", it.title, it.description)
    
        @QtCore.Slot(QtCore.QModelIndex)
        def on_clicky(self, index):
            it = index.model().itemFromIndex(index)
            if it is None:
                return
            print("clicked:", it.title, it.description)

        @Slot()
        def _my_slot(self):
            print('new live streamer from main.py')

    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    sys.exit(main())
