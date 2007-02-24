#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2007 Troy Melhase <troy@gci.net>
# Distributed under the terms of the GNU General Public License v2

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QFrame, QIcon

from ib.ext.TickType import TickType

from profit.lib import ValueTableItem
from profit.widgets.ui_tickerdisplay import Ui_TickerDisplay


fieldColumns = {
    TickType.ASK_SIZE : 3,
    TickType.ASK : 4,
    TickType.BID_SIZE : 5,
    TickType.BID : 6,
    TickType.LAST_SIZE : 7,
    TickType.LAST : 8,
    }


class TickerDisplay(QFrame, Ui_TickerDisplay):
    def __init__(self, session, parent=None):
        QFrame.__init__(self, parent)
        self.setupUi(self)
        self.tickerItems = {}
        self.tickers = session['tickers']
        self.tickerTable.verticalHeader().hide()
        session.register(self.on_tickerPriceSize, 'TickPrice')
        session.register(self.on_tickerPriceSize, 'TickSize')

    def on_tickerPriceSize(self, message):
        tid = message.tickerId
        try:
            value = message.price
        except (AttributeError, ):
            value = message.size

        table = self.tickerTable
        table.setUpdatesEnabled(False)

        try:
            items = self.tickerItems[tid]
        except (KeyError, ):
            sym = dict([(b, a) for a, b in self.tickers.items()])[tid]
            columnCount = table.columnCount()
            row = table.rowCount()
            table.insertRow(row)
            items = self.tickerItems[tid] = \
                    [TickerTableItem() for i in range(columnCount)]
            items[0].setSymbol(sym)
            for item in items[1:]:
                item.setValueAlign()
            for col, item in enumerate(items):
                table.setItem(row, col, item)
            table.sortItems(0)
            table.resizeColumnToContents(0)
            table.resizeRowsToContents()
        try:
            index = fieldColumns[message.field]
        except (KeyError, ):
            pass
        else:
            items[index].setValue(value)
            table.resizeColumnToContents(index)

        table.setUpdatesEnabled(True)


class TickerTableItem(ValueTableItem):
    def setSymbol(self, value):
        icon = QIcon(':images/tickers/%s.png' % (value.lower(), ))
        if not icon.isNull():
            self.setIcon(icon)
        self.setText(value)

    def setValueAlign(self):
        self.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)