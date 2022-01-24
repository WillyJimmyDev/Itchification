import os
import sys

from PySide2 import QtCore, QtGui, QtWidgets
from widgets.followed_item import FollowedItem
from widgets.styled_item_delegate import StyledItemDelegate
from fake_model import model_data

# CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


# def get_icon_path(name):
#     return os.path.join(CURRENT_DIR, "thumbnails", name)


class LauncherWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(LauncherWidget, self).__init__(parent)
        self.setWindowTitle("Test Window")

        self.model = QtGui.QStandardItemModel(self)
        self.listview = QtWidgets.QListView(
            editTriggers=QtWidgets.QAbstractItemView.NoEditTriggers
        )
        self.listview.setItemDelegate(StyledItemDelegate(self.listview))
        self.listview.setModel(self.model)
        self.listview.clicked.connect(self.onClicked)

        lay = QtWidgets.QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.listview, strecth=0)
        self.fill_model()

    def fill_model(self):
        for r in model_data:
            # print(r['icon'])
            print(QtCore.QFile.exists(r['icon']))
            it = FollowedItem(
                title=r['title'], description=r['description'], icon=QtGui.QIcon('/home/wjdev/PycharmProjects/Itchification/thumbnails/hero_dev.jpg'),
            )
            print(it.icon)
            self.model.appendRow(it)

    @QtCore.Slot(QtCore.QModelIndex)
    def onClicked(self, index):
        it = self.model.itemFromIndex(index)
        if it is None:
            return
        print("clicked:", it.title, it.description)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    # app.setWindowIcon(QtGui.QIcon('/home/wjdev/PycharmProjects/Itchification/thumbnails/hero_dev.jpg'))
    w = LauncherWidget()
    w.show()
    sys.exit(app.exec_())