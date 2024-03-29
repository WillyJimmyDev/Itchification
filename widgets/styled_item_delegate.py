from PySide2 import QtCore, QtGui, QtWidgets, os
from config.config import LIVE_ROLE, TITLE_ROLE, DESCRIPTION_ROLE, ICON_ROLE, URL_ROLE


class StyledItemDelegate(QtWidgets.QStyledItemDelegate):
    def sizeHint(self, option, index):
        return QtCore.QSize(60, 60)

    def paint(self, painter, option, index):
        super(StyledItemDelegate, self).paint(painter, option, index)
        title = index.data(TITLE_ROLE)
        description = index.data(DESCRIPTION_ROLE)
        icon = index.data(ICON_ROLE)
        live_status = index.data(LIVE_ROLE)

        mode = QtGui.QIcon.Normal

        # if not (option.state & QtWidgets.QStyle.State_Enabled):
        #     mode = QtGui.QIcon.Disabled
        # elif option.state & QtWidgets.QStyle.State_Selected:
        #     mode = QtGui.QIcon.Selected

        state = (
            QtGui.QIcon.On
            if option.state & QtWidgets.QStyle.State_Open
            else QtGui.QIcon.Off
        )

        # the icon
        iconRect = QtCore.QRect(option.rect)
        iconRect.setSize(QtCore.QSize(60, 60))
        icon.paint(
            painter, iconRect, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, mode, state
        )

        # color of the font
        color = (
            option.palette.color(QtGui.QPalette.BrightText)
            if option.state & QtWidgets.QStyle.State_Selected
            else option.palette.color(QtGui.QPalette.WindowText)
        )

        # title font
        titleFont = QtGui.QFont(option.font)
        titleFont.setPixelSize(16)
        fm = QtGui.QFontMetrics(titleFont)
        titleRect = QtCore.QRect(option.rect)
        titleRect.setLeft(iconRect.right() + 10)
        titleRect.setHeight(fm.height())

        painter.save()
        painter.setFont(titleFont)
        pen = painter.pen()
        pen.setColor(color)
        painter.setPen(pen)
        painter.drawText(titleRect, title)
        painter.restore()

        if live_status == 1:
            self._draw_live_indicator(option, titleRect, painter)

        # description font
        descriptionFont = QtGui.QFont(option.font)
        descriptionFont.setPixelSize(14)
        fm = QtGui.QFontMetrics(descriptionFont)
        descriptionRect = QtCore.QRect(option.rect)
        descriptionRect.setTopLeft(titleRect.bottomLeft())
        descriptionRect.setHeight(fm.height())

        painter.save()
        painter.setFont(descriptionFont)
        pen = painter.pen()
        pen.setColor(color)
        painter.setPen(pen)
        painter.drawText(
            descriptionRect,
            fm.elidedText(description, QtCore.Qt.ElideRight, descriptionRect.width()),
        )
        painter.restore()

    def _draw_live_indicator(self, option, titleRect, painter):
        live_icon = QtCore.QRect(option.rect.right() - 12, titleRect.top() + 3, 10, 10)

        painter.save()
        result = painter.pen()
        painter.setBrush(QtCore.Qt.red)
        result.setColor(QtCore.Qt.red)
        painter.setPen(result)
        painter.drawEllipse(live_icon)
        painter.restore()

        return result
