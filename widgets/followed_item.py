from PySide2 import QtGui
from config.config import TITLE_ROLE, DESCRIPTION_ROLE, ICON_ROLE

class FollowedItem(QtGui.QStandardItem):
    def __init__(self, title="", description="", icon=QtGui.QIcon()):
        super(FollowedItem, self).__init__()
        self.title = title
        self.description = description
        self.icon = icon
        # TOD add url property setters and getters and parameter in __init__ method

    @property
    def title(self):
        return self.data(TITLE_ROLE)

    @title.setter
    def title(self, title):
        self.setData(title, TITLE_ROLE)

    @property
    def description(self):
        return self.data(DESCRIPTION_ROLE)

    @description.setter
    def description(self, description):
        self.setData(description, DESCRIPTION_ROLE)

    @property
    def icon(self):
        return self.data(ICON_ROLE)

    @icon.setter
    def icon(self, icon):
        self.setData(icon, ICON_ROLE)