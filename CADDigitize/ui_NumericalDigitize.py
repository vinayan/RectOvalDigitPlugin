# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_NumericalDigitize.ui'
#
# Created: Tue Nov 18 05:24:47 2014
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

class Ui_NumericalDigitize(object):
    def setupUi(self, NumericalDigitize):
        NumericalDigitize.setObjectName(_fromUtf8("NumericalDigitize"))
        NumericalDigitize.resize(483, 262)
        self.layoutWidget = QtGui.QWidget(NumericalDigitize)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 461, 242))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(self.layoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.tableWidget = QtGui.QTableWidget(self.layoutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableWidget.sizePolicy().hasHeightForWidth())
        self.tableWidget.setSizePolicy(sizePolicy)
        self.tableWidget.setInputMethodHints(QtCore.Qt.ImhNone)
        self.tableWidget.setFrameShape(QtGui.QFrame.StyledPanel)
        self.tableWidget.setFrameShadow(QtGui.QFrame.Sunken)
        self.tableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.tableWidget.setAutoScroll(True)
        self.tableWidget.setRowCount(2)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.verticalLayout.addWidget(self.tableWidget)
        self.buttonBox = QtGui.QDialogButtonBox(self.layoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(NumericalDigitize)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), NumericalDigitize.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), NumericalDigitize.reject)
        QtCore.QMetaObject.connectSlotsByName(NumericalDigitize)

    def retranslateUi(self, NumericalDigitize):
        NumericalDigitize.setWindowTitle(_translate("NumericalDigitize", "Numerical Digitize", None))
        self.label.setText(_translate("NumericalDigitize", "TextLabel", None))

