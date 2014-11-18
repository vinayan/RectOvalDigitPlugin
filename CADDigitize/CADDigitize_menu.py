# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CADDigitize
                                 A QGIS plugin
 CAD like tools for QGis
 Fork of Rectangles Ovals Digitizing. Inspired by CadTools, LibreCAD/AutoCAD.
                              -------------------
        begin                : 2014-08-11
        git sha              : $Format:%H$
        copyright            : (C) 2014 by Loïc BARTOLETTI
        email                : l.bartoletti@free.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4 import QtCore, QtGui
from qgis.core import *
from qgis.gui import *
from CADDigitize_dialog import Ui_NumericalDigitize

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

class CADDigitize_Menu:

    def __init__(self, iface, menu):
        self.iface = iface
        self.menu = menu
    
        self.circleMenu = self.menu.addMenu(QtCore.QCoreApplication.translate( "Circle","Circle" ))
        self.circleBy2PointsMenu = self.circleMenu.addAction(QtCore.QCoreApplication.translate("Circle by 2 Points", "Circle by 2 Points" ))
        self.circleBy3PointsMenu = self.circleMenu.addAction(QtCore.QCoreApplication.translate("Circle by 3 Points", "Circle by 3 Points" ))
        self.circleByCenterRadiusMenu = self.circleMenu.addAction(QtCore.QCoreApplication.translate("Circle by Center and Radius", "Circle by Center and Radius" ))
        self.circleByCenterPointMenu = self.circleMenu.addAction(QtCore.QCoreApplication.translate("Circle by Center and a Point", "Circle by Center and a Point" ))
  
        self.rectMenu = self.menu.addMenu(QtCore.QCoreApplication.translate( "Rectangle","Rectangle" ))
        self.rectBy3PointsMenu = self.rectMenu.addAction(QtCore.QCoreApplication.translate("Rectangle by 3 Points", "Rectangle by 3 Points" ))
        self.rectByExtentMenu = self.rectMenu.addAction(QtCore.QCoreApplication.translate("Rectangle by extent", "Rectangle by extent" ))
        self.rectFromCenterMenu = self.rectMenu.addAction(QtCore.QCoreApplication.translate("Rectangle from Center", "Rectangle from Center" ))
        self.squareFromCenterMenu = self.rectMenu.addAction(QtCore.QCoreApplication.translate("Square from Center", "Square from Center" ))
        
        self.ellipseMenu = self.menu.addMenu(QtCore.QCoreApplication.translate( "Ellipse","Ellipse" ))
        self.ellipseByCenter2PointsMenu = self.ellipseMenu.addAction(QtCore.QCoreApplication.translate("Ellipse by center and 2 points", "Ellipse by center and 2 points" ))
        self.ellipseByFociPointMenu = self.ellipseMenu.addAction(QtCore.QCoreApplication.translate("Ellipse by Foci and a point", "Ellipse by Foci and a point" ))    
        self.ellipseByExtentMenu = self.ellipseMenu.addAction(QtCore.QCoreApplication.translate("Ellipse by extent", "Ellipse by extent" ))
        self.ellipseFromCenterMenu = self.ellipseMenu.addAction(QtCore.QCoreApplication.translate("Ellipse from Center", "Ellipse from Center" ))
        
        self.arcMenu = self.menu.addMenu(QtCore.QCoreApplication.translate( "Arc","Arc" ))
        self.arcByCenter2PointsMenu = self.arcMenu.addAction(QtCore.QCoreApplication.translate("Arc by center and 2 Points", "Arc by center and 2 Points" ))
        self.arcBy3PointsMenu = self.arcMenu.addAction(QtCore.QCoreApplication.translate("Arc by 3 Points", "Arc by 3 Points" ))
        self.arcByCenterPointAngleMenu = self.arcMenu.addAction(QtCore.QCoreApplication.translate("Arc by Center, a point and angle", "Arc by Center, a point and angle" ))
        
        self.rpolygonMenu = self.menu.addMenu(QtCore.QCoreApplication.translate( "Regular polygon","Regular polygon" ))
        self.rpolygonByCenterCornerMenu = self.rpolygonMenu.addAction(QtCore.QCoreApplication.translate("Regular polygon by center and a corner", "Regular polygon by center and a corner" ))
        self.rpolygonBy2CornersMenu = self.rpolygonMenu.addAction(QtCore.QCoreApplication.translate("Regular polygon by 2 corners", "Regular polygon by 2 corners" ))
        
        
                
        self.circleBy2PointsMenu.triggered.connect(self.doCircleBy2PointsMenu)
        self.circleBy3PointsMenu.triggered.connect(self.doCircleBy3PointsMenu)
        self.circleByCenterRadiusMenu.triggered.connect(self.doCircleByCenterRadiusMenu)
        self.circleByCenterPointMenu.triggered.connect(self.doCircleByCenterPointMenu)
        self.rectBy3PointsMenu.triggered.connect(self.doRectBy3PointsMenu)
        self.rectByExtentMenu.triggered.connect(self.doRectByExtentMenu)
        self.rectFromCenterMenu.triggered.connect(self.doRectFromCenterMenu)
        self.squareFromCenterMenu.triggered.connect(self.doSquareFromCenterMenu)
        self.ellipseByCenter2PointsMenu.triggered.connect(self.doEllipseByCenter2PointsMenu)
        self.ellipseByFociPointMenu.triggered.connect(self.doEllipseByFociPointMenu)
        self.ellipseByExtentMenu.triggered.connect(self.doEllipseByExtentMenu)
        self.ellipseFromCenterMenu.triggered.connect(self.doEllipseFromCenterMenu)
        self.arcByCenter2PointsMenu.triggered.connect(self.doArcByCenter2PointsMenu)
        self.arcBy3PointsMenu.triggered.connect(self.doArcBy3PointsMenu)
        self.arcByCenterPointAngleMenu.triggered.connect(self.doArcByCenterPointAngleMenu)
        self.rpolygonByCenterCornerMenu.triggered.connect(self.doRpolygonByCenterCornerMenu)
        self.rpolygonBy2CornersMenu.triggered.connect(self.doRpolygonBy2CornersMenu)
        
    def doCircleBy2PointsMenu(self):
        self.numericalDigitize = Ui_NumericalDigitize()
        self.numericalDigitize.tableWidget.setColumnCount(2)
        self.numericalDigitize.label.setText(_fromUtf8("Circle by 2 Points"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([_fromUtf8("First Point"), _fromUtf8("Second Point")])
        self.numericalDigitize.show()
        
    def doCircleBy3PointsMenu(self):
        self.numericalDigitize = Ui_NumericalDigitize()
        self.numericalDigitize.tableWidget.setColumnCount(3)
        self.numericalDigitize.label.setText(_fromUtf8("Circle by 3 Points"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([_fromUtf8("First Point"), _fromUtf8("Second Point"), _fromUtf8("Third Point")])
        self.numericalDigitize.show()
        
    def doCircleByCenterRadiusMenu(self):
        self.numericalDigitize = Ui_NumericalDigitize()
        self.numericalDigitize.tableWidget.setColumnCount(2)
        self.numericalDigitize.label.setText(_fromUtf8("Circle by Center and Radius"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([_fromUtf8("Center Point"), _fromUtf8("Radius")])
        self.numericalDigitize.show()
        
    def doCircleByCenterPointMenu(self):
        self.numericalDigitize = Ui_NumericalDigitize()
        self.numericalDigitize.tableWidget.setColumnCount(2)
        self.numericalDigitize.label.setText(_fromUtf8("Circle by Center and a Point"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([_fromUtf8("Center Point"), _fromUtf8("Point on Circle")])
        self.numericalDigitize.show()
        
    def doRectBy3PointsMenu(self):
        self.numericalDigitize = Ui_NumericalDigitize()
        self.numericalDigitize.tableWidget.setColumnCount(3)
        self.numericalDigitize.label.setText(_fromUtf8("Rectangle by 3 Points"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([_fromUtf8("First Point"), _fromUtf8("Second Point"), _fromUtf8("Third Point")])
        self.numericalDigitize.show()
        
    def doRectByExtentMenu(self):
        self.numericalDigitize = Ui_NumericalDigitize()
        self.numericalDigitize.tableWidget.setColumnCount(2)
        self.numericalDigitize.label.setText(_fromUtf8("Rectangle by extent"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([_fromUtf8("First Point"), _fromUtf8("Second Point")])
        self.numericalDigitize.show()
        
    def doRectFromCenterMenu(self):
        self.numericalDigitize = Ui_NumericalDigitize()
        self.numericalDigitize.tableWidget.setColumnCount(2)
        self.numericalDigitize.label.setText(_fromUtf8("Rectangle from Center"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([_fromUtf8("Center Point"), _fromUtf8("Point on Rectangle")])
        self.numericalDigitize.show()
        
    def doSquareFromCenterMenu(self):
        self.numericalDigitize = Ui_NumericalDigitize()
        self.numericalDigitize.tableWidget.setColumnCount(2)
        self.numericalDigitize.label.setText(_fromUtf8("Square from Center"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([_fromUtf8("Center Point"), _fromUtf8("Point on Square")])
        self.numericalDigitize.show()
        
    def doEllipseByCenter2PointsMenu(self):
        self.numericalDigitize = Ui_NumericalDigitize()
        self.numericalDigitize.tableWidget.setColumnCount(3)
        self.numericalDigitize.label.setText(_fromUtf8("Ellipse by center and 2 points"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([_fromUtf8("Center Point"), _fromUtf8("First Point"), _fromUtf8("Second Point")])
        self.numericalDigitize.show()
        
    def doEllipseByFociPointMenu(self):
        self.numericalDigitize = Ui_NumericalDigitize()
        self.numericalDigitize.tableWidget.setColumnCount(3)
        self.numericalDigitize.label.setText(_fromUtf8("Ellipse by Foci and a point"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([_fromUtf8("First Focus Point"), _fromUtf8("Second Focus Point"), _fromUtf8("Point on Ellipse")])
        self.numericalDigitize.show()
        
    def doEllipseByExtentMenu(self):
        self.numericalDigitize = Ui_NumericalDigitize()
        self.numericalDigitize.tableWidget.setColumnCount(2)
        self.numericalDigitize.label.setText(_fromUtf8("Ellipse by extent"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([_fromUtf8("First Point"), _fromUtf8("Second Point")])
        self.numericalDigitize.show()
        
    def doEllipseFromCenterMenu(self):
        self.numericalDigitize = Ui_NumericalDigitize()
        self.numericalDigitize.tableWidget.setColumnCount(2)
        self.numericalDigitize.label.setText(_fromUtf8("Ellipse from Center"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([_fromUtf8("Center Point"), _fromUtf8("Extent Point")])
        self.numericalDigitize.show()
        
    def doArcByCenter2PointsMenu(self):
        self.numericalDigitize = Ui_NumericalDigitize()
        self.numericalDigitize.tableWidget.setColumnCount(3)
        self.numericalDigitize.label.setText(_fromUtf8("Arc by center and 2 Points"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([_fromUtf8("Center Point"),_fromUtf8("First Point"), _fromUtf8("Second Point")])
        self.numericalDigitize.show()
        
    def doArcBy3PointsMenu(self):
        self.numericalDigitize = Ui_NumericalDigitize()
        self.numericalDigitize.tableWidget.setColumnCount(3)
        self.numericalDigitize.label.setText(_fromUtf8("Arc by 3 Points"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([_fromUtf8("First Point"), _fromUtf8("Second Point"), _fromUtf8("Third Point")])
        self.numericalDigitize.show()
        
    def doArcByCenterPointAngleMenu(self):
        self.numericalDigitize = Ui_NumericalDigitize()
        self.numericalDigitize.tableWidget.setColumnCount(3)
        self.numericalDigitize.label.setText(_fromUtf8("Arc by Center, a point and angle"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([_fromUtf8("Center Point"), _fromUtf8("Point on Arc"), _fromUtf8("Angle")])
        self.numericalDigitize.show()
        
    def doRpolygonByCenterCornerMenu(self):
        self.numericalDigitize = Ui_NumericalDigitize()
        self.numericalDigitize.tableWidget.setColumnCount(2)
        self.numericalDigitize.label.setText(_fromUtf8("Regular polygon by center and a corner"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([_fromUtf8("Center Point"), _fromUtf8("Corner")])
        self.numericalDigitize.show()
         
    def doRpolygonBy2CornersMenu(self):
        self.numericalDigitize = Ui_NumericalDigitize()
        self.numericalDigitize.tableWidget.setColumnCount(2)
        self.numericalDigitize.label.setText(_fromUtf8("Regular polygon by 2 corners"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([_fromUtf8("First Corner"), _fromUtf8("Second Corner")])
        self.numericalDigitize.show()           
