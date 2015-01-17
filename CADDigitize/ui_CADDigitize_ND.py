# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_CADDigitize_ND.ui'
#
# Created: Tue Jan 13 18:29:59 2015
#      by: PyQt4 UI code generator 4.11.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_CADDigitize_ND(object):
    def setupUi(self, CADDigitize_ND):
        CADDigitize_ND.setObjectName(_fromUtf8("CADDigitize_ND"))
        CADDigitize_ND.setWindowModality(QtCore.Qt.ApplicationModal)
        CADDigitize_ND.resize(752, 291)
        self.layoutWidget = QtGui.QWidget(CADDigitize_ND)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 731, 271))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.tableWidget = QtGui.QTableWidget(self.layoutWidget)
        self.tableWidget.setInputMethodHints(QtCore.Qt.ImhFormattedNumbersOnly)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(5)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, item)
        self.horizontalLayout.addWidget(self.tableWidget)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.add_btn = QtGui.QPushButton(self.layoutWidget)
        self.add_btn.setObjectName(_fromUtf8("add_btn"))
        self.verticalLayout.addWidget(self.add_btn)
        self.remove_btn = QtGui.QPushButton(self.layoutWidget)
        self.remove_btn.setObjectName(_fromUtf8("remove_btn"))
        self.verticalLayout.addWidget(self.remove_btn)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.buttonBox = QtGui.QDialogButtonBox(self.layoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(CADDigitize_ND)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), CADDigitize_ND.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), CADDigitize_ND.reject)
        QtCore.QMetaObject.connectSlotsByName(CADDigitize_ND)

    def retranslateUi(self, CADDigitize_ND):
        CADDigitize_ND.setWindowTitle(_translate("CADDigitize_ND", "CADDigitize - Numercial Digitize", None))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("CADDigitize_ND", "Function", None))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("CADDigitize_ND", "Point 1", None))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("CADDigitize_ND", "Point 2", None))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("CADDigitize_ND", "Point 3", None))
        item = self.tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("CADDigitize_ND", "Option", None))
        self.add_btn.setText(_translate("CADDigitize_ND", "Add", None))
        self.remove_btn.setText(_translate("CADDigitize_ND", "Remove", None))

