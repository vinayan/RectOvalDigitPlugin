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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from CADDigitize_dialog import Ui_NumericalDigitize

class CADDigitize_Menu:

    def __init__(self, iface, menu):
        self.iface = iface
        self.menu = menu
    
        self.circleMenu = self.menu.addMenu(QCoreApplication.translate( "CADDigitize","Circle", None, QApplication.UnicodeUTF8))
        self.circleBy2PointsMenu = self.circleMenu.addAction(QCoreApplication.translate( "CADDigitize","Circle by 2 points", None, QApplication.UnicodeUTF8))
        self.circleBy3PointsMenu = self.circleMenu.addAction(QCoreApplication.translate( "CADDigitize","Circle by 3 points", None, QApplication.UnicodeUTF8))
        self.circleByCenterRadiusMenu = self.circleMenu.addAction(QCoreApplication.translate( "CADDigitize","Circle by center and radius", None, QApplication.UnicodeUTF8))
        self.circleByCenterPointMenu = self.circleMenu.addAction(QCoreApplication.translate( "CADDigitize","Circle by center and a point", None, QApplication.UnicodeUTF8))
  
        self.rectMenu = self.menu.addMenu(QCoreApplication.translate( "CADDigitize","Rectangle", None, QApplication.UnicodeUTF8))
        self.rectBy3PointsMenu = self.rectMenu.addAction(QCoreApplication.translate( "CADDigitize","Rectangle by 3 points", None, QApplication.UnicodeUTF8))
        self.rectByExtentMenu = self.rectMenu.addAction(QCoreApplication.translate( "CADDigitize","Rectangle by extent", None, QApplication.UnicodeUTF8))
        self.rectFromCenterMenu = self.rectMenu.addAction(QCoreApplication.translate( "CADDigitize","Rectangle from center", None, QApplication.UnicodeUTF8))
        self.squareFromCenterMenu = self.rectMenu.addAction(QCoreApplication.translate( "CADDigitize","Square from center", None, QApplication.UnicodeUTF8))
        
        self.ellipseMenu = self.menu.addMenu(QCoreApplication.translate( "CADDigitize","Ellipse", None, QApplication.UnicodeUTF8))
        self.ellipseByCenter2PointsMenu = self.ellipseMenu.addAction(QCoreApplication.translate( "CADDigitize","Ellipse by center and 2 points", None, QApplication.UnicodeUTF8))
        self.ellipseByFociPointMenu = self.ellipseMenu.addAction(QCoreApplication.translate( "CADDigitize","Ellipse by center and 3 points", None, QApplication.UnicodeUTF8))    
        self.ellipseByExtentMenu = self.ellipseMenu.addAction(QCoreApplication.translate( "CADDigitize","Ellipse by extent", None, QApplication.UnicodeUTF8))
        self.ellipseFromCenterMenu = self.ellipseMenu.addAction(QCoreApplication.translate( "CADDigitize","Ellipse from center", None, QApplication.UnicodeUTF8))
        
        self.arcMenu = self.menu.addMenu(QCoreApplication.translate( "CADDigitize","Arc", None, QApplication.UnicodeUTF8))
        self.arcByCenter2PointsMenu = self.arcMenu.addAction(QCoreApplication.translate( "CADDigitize","Arc by center and 2 points", None, QApplication.UnicodeUTF8))
        self.arcBy3PointsMenu = self.arcMenu.addAction(QCoreApplication.translate( "CADDigitize","Arc by 3 points", None, QApplication.UnicodeUTF8))
        self.arcByCenterPointAngleMenu = self.arcMenu.addAction(QCoreApplication.translate( "CADDigitize","Arc by center, point and angle", None, QApplication.UnicodeUTF8))
        
        self.rpolygonMenu = self.menu.addMenu(QCoreApplication.translate( "CADDigitize","Regular polygon", None, QApplication.UnicodeUTF8))
        self.rpolygonByCenterCornerMenu = self.rpolygonMenu.addAction(QCoreApplication.translate( "CADDigitize","Regular polygon by center and point", None, QApplication.UnicodeUTF8))
        self.rpolygonBy2CornersMenu = self.rpolygonMenu.addAction(QCoreApplication.translate( "CADDigitize","Regular polygon by 2 corners", None, QApplication.UnicodeUTF8))
        
        
                
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
        self.numericalDigitize.tableWidget.setColumnCount(4)
        self.numericalDigitize.tableWidget.setInputMethodHints(QtCore.Qt.ImhFormattedNumbersOnly)
        self.numericalDigitize.label.setText(QCoreApplication.translate( "CADDigitize","Circle by 2 Points"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([QCoreApplication.translate( "CADDigitize","X 1", None, QApplication.UnicodeUTF8), QCoreApplication.translate( "CADDigitize","Y 1", None, QApplication.UnicodeUTF8), QCoreApplication.translate( "CADDigitize","X 2", None, QApplication.UnicodeUTF8), QCoreApplication.translate( "CADDigitize","Y 2", None, QApplication.UnicodeUTF8)])
        self.numericalDigitize.show()
        
    def doCircleBy3PointsMenu(self):
        self.numericalDigitize = Ui_NumericalDigitize()
        self.numericalDigitize.tableWidget.setColumnCount(3)
        self.numericalDigitize.label.setText(QCoreApplication.translate( "CADDigitize","Circle by 3 Points"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([QCoreApplication.translate( "CADDigitize","First Point", None, QApplication.UnicodeUTF8), QCoreApplication.translate( "CADDigitize","Second Point", None, QApplication.UnicodeUTF8), QCoreApplication.translate( "CADDigitize","Third Point", None, QApplication.UnicodeUTF8)])
        self.numericalDigitize.show()
        
    def doCircleByCenterRadiusMenu(self):
        self.numericalDigitize = Ui_NumericalDigitize()
        self.numericalDigitize.tableWidget.setColumnCount(2)
        self.numericalDigitize.label.setText(QCoreApplication.translate( "CADDigitize","Circle by Center and Radius"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([QCoreApplication.translate( "CADDigitize","Center Point", None, QApplication.UnicodeUTF8), QCoreApplication.translate( "CADDigitize","Radius", None, QApplication.UnicodeUTF8)])
        self.numericalDigitize.show()
        
    def doCircleByCenterPointMenu(self):
        self.numericalDigitize = Ui_NumericalDigitize()
        self.numericalDigitize.tableWidget.setColumnCount(2)
        self.numericalDigitize.label.setText(QCoreApplication.translate( "CADDigitize","Circle by Center and a Point"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([QCoreApplication.translate( "CADDigitize","Center Point", None, QApplication.UnicodeUTF8), QCoreApplication.translate( "CADDigitize","Point on Circle", None, QApplication.UnicodeUTF8)])
        self.numericalDigitize.show()
        
    def doRectBy3PointsMenu(self):
        self.numericalDigitize = Ui_NumericalDigitize()
        self.numericalDigitize.tableWidget.setColumnCount(3)
        self.numericalDigitize.label.setText(QCoreApplication.translate( "CADDigitize","Rectangle by 3 Points"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([QCoreApplication.translate( "CADDigitize","First Point", None, QApplication.UnicodeUTF8), QCoreApplication.translate( "CADDigitize","Second Point", None, QApplication.UnicodeUTF8), QCoreApplication.translate( "CADDigitize","Third Point", None, QApplication.UnicodeUTF8)])
        self.numericalDigitize.show()
        
    def doRectByExtentMenu(self):
        self.numericalDigitize = Ui_NumericalDigitize()
        self.numericalDigitize.tableWidget.setColumnCount(2)
        self.numericalDigitize.label.setText(QCoreApplication.translate( "CADDigitize","Rectangle by extent"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([QCoreApplication.translate( "CADDigitize","First Point", None, QApplication.UnicodeUTF8), QCoreApplication.translate( "CADDigitize","Second Point", None, QApplication.UnicodeUTF8)])
        self.numericalDigitize.show()
        
    def doRectFromCenterMenu(self):
        self.numericalDigitize = Ui_NumericalDigitize()
        self.numericalDigitize.tableWidget.setColumnCount(2)
        self.numericalDigitize.label.setText(QCoreApplication.translate( "CADDigitize","Rectangle from Center"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([QCoreApplication.translate( "CADDigitize","Center Point", None, QApplication.UnicodeUTF8), QCoreApplication.translate( "CADDigitize","Point on Rectangle", None, QApplication.UnicodeUTF8)])
        self.numericalDigitize.show()
        
    def doSquareFromCenterMenu(self):
        self.numericalDigitize = Ui_NumericalDigitize()
        self.numericalDigitize.tableWidget.setColumnCount(2)
        self.numericalDigitize.label.setText(QCoreApplication.translate( "CADDigitize","Square from Center"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([QCoreApplication.translate( "CADDigitize","Center Point", None, QApplication.UnicodeUTF8), QCoreApplication.translate( "CADDigitize","Point on Square", None, QApplication.UnicodeUTF8)])
        self.numericalDigitize.show()
        
    def doEllipseByCenter2PointsMenu(self):
        self.numericalDigitize = Ui_NumericalDigitize()
        self.numericalDigitize.tableWidget.setColumnCount(3)
        self.numericalDigitize.label.setText(QCoreApplication.translate( "CADDigitize","Ellipse by center and 2 points"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([QCoreApplication.translate( "CADDigitize","Center Point", None, QApplication.UnicodeUTF8), QCoreApplication.translate( "CADDigitize","First Point", None, QApplication.UnicodeUTF8), QCoreApplication.translate( "CADDigitize","Second Point", None, QApplication.UnicodeUTF8)])
        self.numericalDigitize.show()
        
    def doEllipseByFociPointMenu(self):
        self.numericalDigitize = Ui_NumericalDigitize()
        self.numericalDigitize.tableWidget.setColumnCount(3)
        self.numericalDigitize.label.setText(QCoreApplication.translate( "CADDigitize","Ellipse by Foci and a point"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([QCoreApplication.translate( "CADDigitize","First Focus Point", None, QApplication.UnicodeUTF8), QCoreApplication.translate( "CADDigitize","Second Focus Point", None, QApplication.UnicodeUTF8), QCoreApplication.translate( "CADDigitize","Point on Ellipse", None, QApplication.UnicodeUTF8)])
        self.numericalDigitize.show()
        
    def doEllipseByExtentMenu(self):
        self.numericalDigitize = Ui_NumericalDigitize()
        self.numericalDigitize.tableWidget.setColumnCount(2)
        self.numericalDigitize.label.setText(QCoreApplication.translate( "CADDigitize","Ellipse by extent"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([QCoreApplication.translate( "CADDigitize","First Point", None, QApplication.UnicodeUTF8), QCoreApplication.translate( "CADDigitize","Second Point", None, QApplication.UnicodeUTF8)])
        self.numericalDigitize.show()
        
    def doEllipseFromCenterMenu(self):
        self.numericalDigitize = Ui_NumericalDigitize()
        self.numericalDigitize.tableWidget.setColumnCount(2)
        self.numericalDigitize.label.setText(QCoreApplication.translate( "CADDigitize","Ellipse from Center"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([QCoreApplication.translate( "CADDigitize","Center Point", None, QApplication.UnicodeUTF8), QCoreApplication.translate( "CADDigitize","Extent Point", None, QApplication.UnicodeUTF8)])
        self.numericalDigitize.show()
        
    def doArcByCenter2PointsMenu(self):
        self.numericalDigitize = Ui_NumericalDigitize()
        self.numericalDigitize.tableWidget.setColumnCount(3)
        self.numericalDigitize.label.setText(QCoreApplication.translate( "CADDigitize","Arc by center and 2 Points"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([QCoreApplication.translate( "CADDigitize","Center Point"),QCoreApplication.translate( "CADDigitize","First Point", None, QApplication.UnicodeUTF8), QCoreApplication.translate( "CADDigitize","Second Point", None, QApplication.UnicodeUTF8)])
        self.numericalDigitize.show()
        
    def doArcBy3PointsMenu(self):
        self.numericalDigitize = Ui_NumericalDigitize()
        self.numericalDigitize.tableWidget.setColumnCount(3)
        self.numericalDigitize.label.setText(QCoreApplication.translate( "CADDigitize","Arc by 3 Points"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([QCoreApplication.translate( "CADDigitize","First Point", None, QApplication.UnicodeUTF8), QCoreApplication.translate( "CADDigitize","Second Point", None, QApplication.UnicodeUTF8), QCoreApplication.translate( "CADDigitize","Third Point", None, QApplication.UnicodeUTF8)])
        self.numericalDigitize.show()
        
    def doArcByCenterPointAngleMenu(self):
        self.numericalDigitize = Ui_NumericalDigitize()
        self.numericalDigitize.tableWidget.setColumnCount(3)
        self.numericalDigitize.label.setText(QCoreApplication.translate( "CADDigitize","Arc by Center, a point and angle"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([QCoreApplication.translate( "CADDigitize","Center Point", None, QApplication.UnicodeUTF8), QCoreApplication.translate( "CADDigitize","Point on Arc", None, QApplication.UnicodeUTF8), QCoreApplication.translate( "CADDigitize","Angle", None, QApplication.UnicodeUTF8)])
        self.numericalDigitize.show()
        
    def doRpolygonByCenterCornerMenu(self):
        self.numericalDigitize = Ui_NumericalDigitize()
        self.numericalDigitize.tableWidget.setColumnCount(2)
        self.numericalDigitize.label.setText(QCoreApplication.translate( "CADDigitize","Regular polygon by center and a corner"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([QCoreApplication.translate( "CADDigitize","Center Point", None, QApplication.UnicodeUTF8), QCoreApplication.translate( "CADDigitize","Corner", None, QApplication.UnicodeUTF8)])
        self.numericalDigitize.show()
         
    def doRpolygonBy2CornersMenu(self):
        self.numericalDigitize = Ui_NumericalDigitize()
        self.numericalDigitize.tableWidget.setColumnCount(2)
        self.numericalDigitize.label.setText(QCoreApplication.translate( "CADDigitize","Regular polygon by 2 corners"))
        self.numericalDigitize.tableWidget.setHorizontalHeaderLabels([QCoreApplication.translate( "CADDigitize","First Corner", None, QApplication.UnicodeUTF8), QCoreApplication.translate( "CADDigitize","Second Corner", None, QApplication.UnicodeUTF8)])
        self.numericalDigitize.show()           
