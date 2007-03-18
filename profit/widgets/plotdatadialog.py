#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

from PyQt4.QtCore import QAbstractTableModel, QVariant, Qt, pyqtSignature
from PyQt4.QtGui import QApplication, QBrush, QColorDialog, QDialog
from PyQt4.QtGui import QFileDialog, QFont, QFontDialog, QListWidgetItem

from profit.lib import defaults
from profit.lib.core import Settings, Signals
from profit.lib.gui import colorIcon
from profit.widgets.ui_plotdatadialog import Ui_PlotDataDialog


class CurveDataTableModel(QAbstractTableModel):
    def __init__(self, parent):
        QAbstractTableModel.__init__(self, parent)
        self.tickerId = parent.tickerId
        self.items = []
        self.itemAlign = QVariant(Qt.AlignRight|Qt.AlignVCenter)
        self.setItemBackground(Qt.black)
        for item in parent.checkedItems():
            self.on_enableCurve(item, True)
        self.connect(parent, Signals.enableCurve, self.on_enableCurve)
        self.connect(parent, Signals.canvasColorChanged, self.on_canvasColor)
        parent.session.registerMeta(self)

    def data(self, index, role):
        row, col = index.row(), index.column()
        if not index.isValid():
            data = QVariant()
        elif role == Qt.TextAlignmentRole:
            data = self.itemAlign
        elif role == Qt.ForegroundRole:
            data = QVariant(QBrush(self.items[col].color))
        elif role == Qt.BackgroundRole:
            data = self.itemBackground
        elif not role == Qt.DisplayRole:
            data = QVariant()
        else:
            try:
                data = self.items[col].data[row]
                data = QVariant(data) if data is not None else QVariant()
            except (IndexError, ):
                data = QVariant()
        return data

    def rowCount(self, parent=None):
        try:
            count = max(len(item.data) for item in self.items)
        except (ValueError, ):
            count = 0
        return count

    def columnCount(self, parent=None):
        return len(self.items)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.items[section].text())
        return QVariant()

    def on_enableCurve(self, item, enable):
        if enable and item not in self.items:
            self.setItemBackground(item.curve.plot().canvasBackground())
            self.items.append(item)
        elif not enable and item in self.items:
            self.items.remove(item)
        self.reset()

    def on_session_TickPrice_TickSize(self, message):
        """ Signal handler for TickPrice and TickSize session messages.

        @param message Message instance
        @return None
        """
        if message.tickerId == self.tickerId:
            self.emit(Signals.layoutChanged)

    def on_canvasColor(self, color):
        self.setItemBackground(color)
        self.reset()

    def setItemBackground(self, color):
        self.itemBackground = QVariant(QBrush(color))


class PlotDataDialog(QDialog, Ui_PlotDataDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.model = CurveDataTableModel(parent)
        self.plotDataView.setModel(self.model)
        self.plotDataView.verticalHeader().hide()
        self.addAction(self.actionClose)
