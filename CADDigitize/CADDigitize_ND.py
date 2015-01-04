#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore
from ui_CADDigitize_ND import Ui_CADDigitize_ND
from CADDigitize_functions import *

class CADDigitize_ND(QtGui.QDialog, Ui_CADDigitize_ND):
    def __init__(self):

        self.list_functions = CADDigitize_functions
        self.list_input = CADDigitize_functions_points

        QtGui.QDialog.__init__(self)

        self.setupUi(self)

        self.signalMapper = QtCore.QSignalMapper(self)
        self.signalMapper.mapped[QtGui.QWidget].connect(self.on_signalMapper_mapped)

        QtCore.QObject.connect(self.tableWidget, QtCore.SIGNAL("cellChanged(int, int)"), self.cellChange)
#        self.tableWidget.cellChanged.connect(self.cellChange, int, int)
        # Combobox
        self.add_row()

        self.tableWidget.resizeColumnToContents(0)
        # Add
        self.add_btn.clicked.connect(self.add_row)
        # Remove
        self.remove_btn.clicked.connect(self.remove_row)

        self.show()

    def cellChange(self, currentRow, currentColumn):
        if currentColumn == 0: # function
            return True
        elif currentColumn == 4 and self.tableWidget.item(currentRow, currentColumn).flags() & QtCore.Qt.ItemIsEditable: # double and not spinbox for angle
            if self.is_numeric(self.tableWidget.item(currentRow, currentColumn).text()):
                return True
        elif self.mon_validateur(self.tableWidget.item(currentRow, currentColumn).text()) != False:
            return True

        self.tableWidget.item(currentRow, currentColumn).setText("")
        return False

    def is_numeric(self, str):
        try:
            float(str)
        except (ValueError, TypeError):
            return False

        return True

    def mon_validateur(self, str):
        list_s = str.split(',')
        if len(list_s) != 2:
            return False

        if self.is_numeric(list_s[0]) == False or self.is_numeric(list_s[1]) == False:
            return False

        return True

    @QtCore.pyqtSlot(QtGui.QDialog)
    def on_signalMapper_mapped(self, combobox):
        for index, i in enumerate(self.list_input[combobox.currentIndex()]):
            item = QtGui.QTableWidgetItem()

            if i == False:
                item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsDragEnabled|QtCore.Qt.ItemIsUserCheckable)
                item.setBackground(QtGui.QColor(150,150,150))
                item.setText("None")
                self.tableWidget.setItem(combobox.row, index+1, item)
            elif i == "angle":
                SpinBox_Angle = QtGui.QDoubleSpinBox(self.tableWidget)
                SpinBox_Angle.setDecimals(2)
                SpinBox_Angle.setMaximum(360.0)
                SpinBox_Angle.setProperty("value", 0.00)
                self.tableWidget.setCellWidget(combobox.row, index+1, SpinBox_Angle)
            else:
                item.setText("")
                self.tableWidget.setItem(combobox.row, index+1, item)

    def accept(self):
        for i in range(1, self.tableWidget.columnCount()):
            l = self.mon_validateur(self.tableWidget.item(0,i).text())
            if l:
                print l[0], l[1]

        self.close()

    def add_row(self):

        self.tableWidget.insertRow(self.tableWidget.rowCount())
        combobox = QtGui.QComboBox()
        combobox.addItems(self.list_functions)
        combobox.currentIndexChanged.connect(self.signalMapper.map)
        combobox.row = self.tableWidget.rowCount()-1
        combobox.column = 0

        self.tableWidget.setCellWidget(combobox.row,combobox.column, combobox)

        self.on_signalMapper_mapped(combobox)
        self.signalMapper.setMapping(combobox, combobox)

        # Add

    def remove_row(self):
        self.tableWidget.removeRow(self.tableWidget.currentRow())
        j = 0
        for i in range(self.tableWidget.rowCount()):
            self.tableWidget.cellWidget(i, 0).row = j
            j += 1



def main():
    app = QtGui.QApplication(sys.argv)
    ex = CADDigitize_ND()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

