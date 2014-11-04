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

# List comprehensions in canvasMoveEvent functions are
# adapted from Benjamin Bohard`s part of rectovaldiams plugin.

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from math import *
from tools.calc import *
from tools.circle import *
from tools.circulararc import *
from CADDigitize_dialog import Ui_CADDigitizeDialogAngle


class ArcBy3PointsTool(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self,canvas)
        self.settings = QSettings()
        self.canvas = canvas
        self.nbPoints = 0
        self.rb = None
        self.x_p1, self.y_p1, self.x_p2, self.y_p2, self.x_p3, self.y_p3 = None, None, None, None, None, None
        self.circ_center, self.circ_rayon = None, None
        self.mCtrl = None
        #our own fancy cursor
        self.cursor = QCursor(QPixmap(["16 16 3 1",
                                      "      c None",
                                      ".     c #FF0000",
                                      "+     c #1210f3",
                                      "                ",
                                      "       +.+      ",
                                      "      ++.++     ",
                                      "     +.....+    ",
                                      "    +.     .+   ",
                                      "   +.   .   .+  ",
                                      "  +.    .    .+ ",
                                      " ++.    .    .++",
                                      " ... ...+... ...",
                                      " ++.    .    .++",
                                      "  +.    .    .+ ",
                                      "   +.   .   .+  ",
                                      "   ++.     .+   ",
                                      "    ++.....+    ",
                                      "      ++.++     ",
                                      "       +.+      "]))


    def keyPressEvent(self,  event):
        if event.key() == Qt.Key_Control:
            self.mCtrl = True


    def keyReleaseEvent(self,  event):
        if event.key() == Qt.Key_Control:
            self.mCtrl = False
        if event.key() == Qt.Key_Escape:
            self.nbPoints = 0
            self.x_p1, self.y_p1, self.x_p2, self.y_p2, self.x_p3, self.y_p3 = None, None, None, None, None, None
            self.circ_center, self.circ_rayon = None, None
            self.rb.reset(True)
            self.rb=None

            self.canvas.refresh()
            return

    def canvasPressEvent(self,event):
        layer = self.canvas.currentLayer()
        if self.nbPoints == 0:
            color = QColor(255,0,0)
            self.rb = QgsRubberBand(self.canvas, True)
            self.rb.setColor(color)
            self.rb.setWidth(1)
        elif self.nbPoints == 2:
            self.rb.reset(True)
            self.rb=None

            self.canvas.refresh()

        x = event.pos().x()
        y = event.pos().y()
        if self.mCtrl:
            startingPoint = QPoint(x,y)
            snapper = QgsMapCanvasSnapper(self.canvas)
            (retval,result) = snapper.snapToCurrentLayer (startingPoint, QgsSnapper.SnapToVertex)
            if result <> []:
                point = result[0].snappedVertex
            else:
                (retval,result) = snapper.snapToBackgroundLayers(startingPoint)
                if result <> []:
                    point = result[0].snappedVertex
                else:
                    point = self.toLayerCoordinates(layer,event.pos())
        else:
            point = self.toLayerCoordinates(layer,event.pos())
        pointMap = self.toMapCoordinates(layer, point)

        if self.nbPoints == 0:
            self.x_p1 = pointMap.x()
            self.y_p1 = pointMap.y()
        elif self.nbPoints == 1:
            self.x_p2 = pointMap.x()
            self.y_p2 = pointMap.y()
        else:
            self.x_p3 = pointMap.x()
            self.y_p3 = pointMap.y()

        self.nbPoints += 1

        if self.nbPoints == 3:
            segments = self.settings.value("/CADDigitize/arc/segments",36,type=int)
            method = self.settings.value("/CADDigitize/arc/method",  "pitch")
            
            geom = CircularArc.getArcBy3Points(QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.x_p2, self.y_p2), QgsPoint(self.x_p3, self.y_p3), method, segments)

            self.nbPoints = 0
            center = CircularArc.getArcCenter(QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.x_p2, self.y_p2), QgsPoint(self.x_p3, self.y_p3))
            self.x_p1, self.y_p1, self.x_p2, self.y_p2, self.x_p3, self.y_p3 = None, None, None, None, None, None

            self.emit(SIGNAL("rbFinished(PyQt_PyObject)"), [geom, center])

        if self.rb:return


    def canvasMoveEvent(self,event):

        if not self.rb:return
        currpoint = self.toMapCoordinates(event.pos())
        currx = currpoint.x()
        curry = currpoint.y()
        if self.nbPoints == 1:
            self.rb.setToGeometry(QgsGeometry.fromPolyline([QgsPoint(self.x_p1, self.y_p1), QgsPoint(currx, curry)]), None)

        if self.nbPoints >= 2 and calc_isCollinear(QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.x_p2, self.y_p2), QgsPoint(currx, curry)) != 0:
            segments = self.settings.value("/CADDigitize/arc/segments",36,type=int)
            method = self.settings.value("/CADDigitize/arc/method",  "pitch")
            self.rb.setToGeometry(CircularArc.getArcBy3Points(QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.x_p2, self.y_p2), QgsPoint(currx, curry), method, segments), None)

    def showSettingsWarning(self):
        pass

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def deactivate(self):
        self.nbPoints = 0
        self.x_p1, self.y_p1, self.x_p2, self.y_p2, self.x_p3, self.y_p3 = None, None, None, None, None, None
        self.circ_center, self.circ_rayon = None, None
        if self.rb:
            self.rb.reset(True)
        self.rb=None

        self.canvas.refresh()
        
    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True



class ArcByCenter2PointsTool(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self,canvas)
        self.settings = QSettings()
        self.canvas = canvas
        self.nbPoints = 0
        self.rb = None
        self.rb_arcs = None
        self.x_p1, self.y_p1, self.x_p2, self.y_p2, self.x_p3, self.y_p3 = None, None, None, None, None, None
        self.mCtrl = None
        #our own fancy cursor
        self.cursor = QCursor(QPixmap(["16 16 3 1",
                                      "      c None",
                                      ".     c #FF0000",
                                      "+     c #1210f3",
                                      "                ",
                                      "       +.+      ",
                                      "      ++.++     ",
                                      "     +.....+    ",
                                      "    +.     .+   ",
                                      "   +.   .   .+  ",
                                      "  +.    .    .+ ",
                                      " ++.    .    .++",
                                      " ... ...+... ...",
                                      " ++.    .    .++",
                                      "  +.    .    .+ ",
                                      "   +.   .   .+  ",
                                      "   ++.     .+   ",
                                      "    ++.....+    ",
                                      "      ++.++     ",
                                      "       +.+      "]))


    def keyPressEvent(self,  event):
        if event.key() == Qt.Key_Control:
            self.mCtrl = True


    def keyReleaseEvent(self,  event):
        if event.key() == Qt.Key_Control:
            self.mCtrl = False
        if event.key() == Qt.Key_Escape:
            self.nbPoints = 0
            self.x_p1, self.y_p1, self.x_p2, self.y_p2, self.x_p3, self.y_p3 = None, None, None, None, None, None
            self.rb.reset(True)
            self.rb_arcs.reset(True)
            self.rb=None
            self.rb_arcs=None

            self.canvas.refresh()
            return
            
            
    def canvasPressEvent(self,event):
        layer = self.canvas.currentLayer()
        if self.nbPoints == 0:
            color = QColor(255,0,0)
            self.rb = QgsRubberBand(self.canvas, True)
            self.rb_arcs = QgsRubberBand(self.canvas, True)
            self.rb.setColor(color)
            self.rb_arcs.setColor(QColor(0,0,255))
            self.rb.setWidth(1)
            self.rb_arcs.setWidth(1)
        elif self.nbPoints == 2:
            self.rb.reset(True)
            self.rb_arcs.reset(True)
            self.rb=None
            self.rb_arcs=None

            self.canvas.refresh()

        x = event.pos().x()
        y = event.pos().y()
        if self.mCtrl:
            startingPoint = QPoint(x,y)
            snapper = QgsMapCanvasSnapper(self.canvas)
            (retval,result) = snapper.snapToCurrentLayer (startingPoint, QgsSnapper.SnapToVertex)
            if result <> []:
                point = result[0].snappedVertex
            else:
                (retval,result) = snapper.snapToBackgroundLayers(startingPoint)
                if result <> []:
                    point = result[0].snappedVertex
                else:
                    point = self.toLayerCoordinates(layer,event.pos())
        else:
            point = self.toLayerCoordinates(layer,event.pos())
        pointMap = self.toMapCoordinates(layer, point)

        if self.nbPoints == 0:
            self.x_p1 = pointMap.x()
            self.y_p1 = pointMap.y()
        elif self.nbPoints == 1:
            self.x_p2 = pointMap.x()
            self.y_p2 = pointMap.y()
        else:
            self.x_p3 = pointMap.x()
            self.y_p3 = pointMap.y()

        self.nbPoints += 1

        if self.nbPoints == 3:
            segments = self.settings.value("/CADDigitize/arc/segments",36,type=int)
            clock = self.settings.value("/CADDigitize/arc/direction",  "ClockWise")
            method = self.settings.value("/CADDigitize/arc/method",  "pitch")
            geom = CircularArc.getArcByCenter2Points(QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.x_p2, self.y_p2), QgsPoint(self.x_p3, self.y_p3), method, segments, clock)
            center, start = QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.x_p2, self.y_p2)

            self.nbPoints = 0
            self.x_p1, self.y_p1, self.x_p2, self.y_p2, self.x_p3, self.y_p3 = None, None, None, None, None, None

            self.emit(SIGNAL("rbFinished(PyQt_PyObject)"), [geom, center])

        if self.rb:return


    def canvasMoveEvent(self,event):

        if not self.rb:return
        currpoint = self.toMapCoordinates(event.pos())
        currx = currpoint.x()
        curry = currpoint.y()
        if self.nbPoints == 1:
            self.rb_arcs.setToGeometry(QgsGeometry.fromPolyline([QgsPoint(self.x_p1, self.y_p1), QgsPoint(currx, curry)]), None)

        if self.nbPoints >= 2 and calc_isCollinear(QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.x_p2, self.y_p2), QgsPoint(currx, curry)) != 0:
            segments = self.settings.value("/CADDigitize/arc/segments",36,type=int)
            clock = self.settings.value("/CADDigitize/arc/direction",  "ClockWise")
            method = self.settings.value("/CADDigitize/arc/method",  "pitch")
            geom = CircularArc.getArcByCenter2Points(QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.x_p2, self.y_p2), QgsPoint(currx, curry), method, segments, clock)
            
            self.rb_arcs.setToGeometry(QgsGeometry.fromPolyline([QgsPoint(self.x_p2, self.y_p2), QgsPoint(self.x_p1, self.y_p1), QgsPoint(currx, curry)]), None)
            self.rb.setToGeometry(geom, None)

    def showSettingsWarning(self):
        pass

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def deactivate(self):
        self.nbPoints = 0
        self.x_p1, self.y_p1, self.x_p2, self.y_p2, self.x_p3, self.y_p3 = None, None, None, None, None, None
        if self.rb:
            self.rb.reset(True)
        if self.rb_arcs:
            self.rb_arcs.reset(True)
        self.rb=None
        self.rb_arcs=None

        self.canvas.refresh()

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True


class ArcByCenterPointAngleTool(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self,canvas)
        self.settings = QSettings()
        self.canvas=canvas
        self.nbPoints = 0
        self.rb = None
        self.rb_arcs = None
        self.x_p1, self.y_p1, self.x_p2, self.y_p2, self.currx, self.curry, self.x_p3, self.y_p3 = None, None, None, None, None, None, None, None
        self.circ_center, self.circ_rayon = None, -1
        self.mCtrl = None
        self.setval = False
        #our own fancy cursor
        self.cursor = QCursor(QPixmap(["16 16 3 1",
                                      "      c None",
                                      ".     c #FF0000",
                                      "+     c #1210f3",
                                      "                ",
                                      "       +.+      ",
                                      "      ++.++     ",
                                      "     +.....+    ",
                                      "    +.     .+   ",
                                      "   +.   .   .+  ",
                                      "  +.    .    .+ ",
                                      " ++.    .    .++",
                                      " ... ...+... ...",
                                      " ++.    .    .++",
                                      "  +.    .    .+ ",
                                      "   +.   .   .+  ",
                                      "   ++.     .+   ",
                                      "    ++.....+    ",
                                      "      ++.++     ",
                                      "       +.+      "]))
        self.initGui()

    def setAngleValue(self):
        self.angle = radians(self.dialog.SpinBox_Angle.value())
        
        if self.circ_rayon != None and self.circ_rayon > 0:
        
            
            segments = self.settings.value("/CADDigitize/arc/segments",36,type=int)
            clock = self.settings.value("/CADDigitize/arc/direction",  "ClockWise")
            method = self.settings.value("/CADDigitize/arc/method",  "pitch")
            
            if clock == "ClockWise":
                self.currx = self.x_p1 + cos(self.a1 - self.angle) * self.circ_rayon
                self.curry = self.y_p1 + sin(self.a1 - self.angle) * self.circ_rayon
                self.rb_arcs.setToGeometry(QgsGeometry.fromPolyline([QgsPoint(self.x_p2, self.y_p2), QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.currx, self.curry)]), None)
            
                geom = CircularArc.getArcByCenterPointAngle(QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.x_p2, self.y_p2), self.a1 - self.angle, method, segments, clock)
            elif clock == "CounterClockWise":
                self.currx = self.x_p1 + cos(self.angle + self.a1) * self.circ_rayon
                self.curry = self.y_p1 + sin(self.angle + self.a1) * self.circ_rayon
                self.rb_arcs.setToGeometry(QgsGeometry.fromPolyline([QgsPoint(self.x_p2, self.y_p2), QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.currx, self.curry)]), None)
            
                geom = CircularArc.getArcByCenterPointAngle(QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.x_p2, self.y_p2), self.angle + self.a1, method, segments, clock)
            
    	    self.rb.setToGeometry(geom, None)

    def finishedAngle(self):
        segments = self.settings.value("/CADDigitize/arc/segments",36,type=int)
        clock = self.settings.value("/CADDigitize/arc/direction",  "ClockWise")
        method = self.settings.value("/CADDigitize/arc/method",  "pitch")
        if clock == "ClockWise":
            self.currx = self.x_p1 + cos(self.a1 - self.angle) * self.circ_rayon
            self.curry = self.y_p1 + sin(self.a1 - self.angle) * self.circ_rayon
            self.rb_arcs.setToGeometry(QgsGeometry.fromPolyline([QgsPoint(self.x_p2, self.y_p2), QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.currx, self.curry)]), None)
            
            geom = CircularArc.getArcByCenterPointAngle(QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.x_p2, self.y_p2), self.a1 - self.angle, method, segments, clock)
        elif clock == "CounterClockWise":
            self.currx = self.x_p1 + cos(self.angle + self.a1) * self.circ_rayon
            self.curry = self.y_p1 + sin(self.angle + self.a1) * self.circ_rayon
            self.rb_arcs.setToGeometry(QgsGeometry.fromPolyline([QgsPoint(self.x_p2, self.y_p2), QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.currx, self.curry)]), None)
            
            geom = CircularArc.getArcByCenterPointAngle(QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.x_p2, self.y_p2), self.angle + self.a1, method, segments, clock)

        self.nbPoints = 0
        self.emit(SIGNAL("rbFinished(PyQt_PyObject)"), geom)
        self.x_p1, self.y_p1, self.x_p2, self.y_p2, self.currx, self.curry, self.x_p3, self.y_p3 = None, None, None, None, None, None, None, None
        self.angle, self.circ_rayon = None, -1
        self.setval = True
        self.rb.reset(True)
        self.rb_arcs.reset(True)
        self.rb=None
        self.rb_arcs=None

        self.canvas.refresh()
        self.dialog.SpinBox_Angle.setValue(0)

        return

    def initGui(self):
        self.dialog = Ui_CADDigitizeDialogAngle()
        self.dialog.SpinBox_Angle.valueChanged.connect(self.setAngleValue)
        self.dialog.buttonBox.accepted.connect(self.finishedAngle)

    def keyPressEvent(self,  event):
        if event.key() == Qt.Key_Control:
            self.mCtrl = True
            
    def keyReleaseEvent(self,  event):
        if event.key() == Qt.Key_Control:
            self.mCtrl = False
        if event.key() == Qt.Key_Escape:
            self.dialog.close()

            self.nbPoints = 0
            self.x_p1, self.y_p1, self.x_p2, self.y_p2, self.currx, self.curry, self.x_p3, self.y_p3 = None, None, None, None, None, None, None, None
            self.angle, self.circ_rayon = None, -1
            self.setval = True
            self.rb.reset(True)
            self.rb_arcs.reset(True)
            self.rb=None
            self.rb_arcs=None

            self.canvas.refresh()
            return

    def canvasPressEvent(self,event):
        layer = self.canvas.currentLayer()
        if self.nbPoints == 0:
            self.setval = False
            color = QColor(255,0,0)
            self.rb = QgsRubberBand(self.canvas, True)
            self.rb_arcs = QgsRubberBand(self.canvas, True)
            self.rb.setColor(color)
            self.rb_arcs.setColor(QColor(0,0,255))
            self.rb.setWidth(1)
            self.rb_arcs.setWidth(1)
        elif self.nbPoints == 2:
            self.rb.reset(True)
            self.rb_arcs.reset(True)
            self.rb=None
            self.rb_arcs=None

            self.canvas.refresh()


        x = event.pos().x()
        y = event.pos().y()
        if self.mCtrl:
            startingPoint = QPoint(x,y)
            snapper = QgsMapCanvasSnapper(self.canvas)
            (retval,result) = snapper.snapToCurrentLayer (startingPoint, QgsSnapper.SnapToVertex)
            if result <> []:
                point = result[0].snappedVertex
            else:
                (retval,result) = snapper.snapToBackgroundLayers(startingPoint)
                if result <> []:
                    point = result[0].snappedVertex
                else:
                    point = self.toLayerCoordinates(layer,event.pos())
        else:
            point = self.toLayerCoordinates(layer,event.pos())
        pointMap = self.toMapCoordinates(layer, point)

        if self.nbPoints == 0:
            self.x_p1 = pointMap.x()
            self.y_p1 = pointMap.y()
        elif self.nbPoints == 1:
            self.dialog.show()
            self.x_p2 = pointMap.x()
            self.y_p2 = pointMap.y()
            self.a1 = math.atan2( self.y_p2 - self.y_p1, self.x_p2 - self.x_p1 )
            self.angle = radians(self.dialog.SpinBox_Angle.value())
            self.circ_rayon = QgsDistanceArea().measureLine(QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.x_p2, self.y_p2))
            
            segments = self.settings.value("/CADDigitize/arc/segments",36,type=int)
            clock = self.settings.value("/CADDigitize/arc/direction",  "ClockWise")
            method = self.settings.value("/CADDigitize/arc/method",  "pitch")
            
            if clock == "ClockWise":
                self.currx = self.x_p1 + cos(self.a1 - self.angle) * self.circ_rayon
                self.curry = self.y_p1 + sin(self.a1 - self.angle) * self.circ_rayon
                self.rb_arcs.setToGeometry(QgsGeometry.fromPolyline([QgsPoint(self.x_p2, self.y_p2), QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.currx, self.curry)]), None)
            
                geom = CircularArc.getArcByCenterPointAngle(QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.x_p2, self.y_p2), self.a1 - self.angle, method, segments, clock)
            elif clock == "CounterClockWise":
                self.currx = self.x_p1 + cos(self.angle + self.a1) * self.circ_rayon
                self.curry = self.y_p1 + sin(self.angle + self.a1) * self.circ_rayon
                self.rb_arcs.setToGeometry(QgsGeometry.fromPolyline([QgsPoint(self.x_p2, self.y_p2), QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.currx, self.curry)]), None)
            
                geom = CircularArc.getArcByCenterPointAngle(QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.x_p2, self.y_p2), self.angle + self.a1, method, segments, clock)
                
            self.rb_arcs.setToGeometry(QgsGeometry.fromPolyline([QgsPoint(self.x_p2, self.y_p2), QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.currx, self.curry)]), None)
            
    	    self.rb.setToGeometry(geom, None)
        else:
            self.x_p3 = pointMap.x()
            self.y_p3 = pointMap.y()

        self.nbPoints += 1

        if self.nbPoints == 3:
            self.dialog.close()
            segments = self.settings.value("/CADDigitize/arc/segments",36,type=int)
            clock = self.settings.value("/CADDigitize/arc/direction",  "ClockWise")
            method = self.settings.value("/CADDigitize/arc/method",  "pitch")
            
            if clock == "ClockWise":
            
                geom = CircularArc.getArcByCenterPointAngle(QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.x_p2, self.y_p2), self.a1 - self.angle, method, segments, clock)
            elif clock == "CounterClockWise":
            
                geom = CircularArc.getArcByCenterPointAngle(QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.x_p2, self.y_p2), self.angle + self.a1, method, segments, clock)

            self.nbPoints = 0
            center = QgsPoint(self.x_p1, self.y_p1)
            self.x_p1, self.y_p1, self.x_p2, self.y_p2, self.currx, self.curry, self.x_p3, self.y_p3 = None, None, None, None, None, None, None, None

            self.emit(SIGNAL("rbFinished(PyQt_PyObject)"), [geom, center])


        if self.rb:return


    def canvasMoveEvent(self,event):
        
        if not self.rb:return
        currpoint = self.toMapCoordinates(event.pos())
        self.currx = currpoint.x()
        self.curry = currpoint.y()

        if self.nbPoints == 1:
            self.rb_arcs.setToGeometry(QgsGeometry.fromPolyline([QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.currx, self.curry)]), None)

        if self.nbPoints >= 2 and calc_isCollinear(QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.x_p2, self.y_p2), QgsPoint(self.currx, self.curry)) != 0:
        
            segments = self.settings.value("/CADDigitize/arc/segments",36,type=int)
            clock = self.settings.value("/CADDigitize/arc/direction",  "ClockWise")
            method = self.settings.value("/CADDigitize/arc/method",  "pitch")
            self.rb_arcs.setToGeometry(QgsGeometry.fromPolyline([QgsPoint(self.x_p2, self.y_p2), QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.currx, self.curry)]), None)
            
            
            self.a2 = math.atan2( self.curry - self.y_p1, self.currx - self.x_p1 )
            self.angle = self.a2 - self.a1
            if self.angle < 0:
                self.angle += 2*math.pi


                
            if clock == "ClockWise":
                self.angle = 2*math.pi - self.angle            
                geom = CircularArc.getArcByCenterPointAngle(QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.x_p2, self.y_p2), self.a1 - self.angle, method, segments, clock)

            elif clock == "CounterClockWise":
            
                geom = CircularArc.getArcByCenterPointAngle(QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.x_p2, self.y_p2), self.angle + self.a1, method, segments, clock)
            
            if self.setval == False:
                self.dialog.SpinBox_Angle.setValue(degrees(self.angle))
                
            self.rb.setToGeometry(geom, None)
            
    def showSettingsWarning(self):
        pass

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def deactivate(self):
        self.dialog.close()

        self.nbPoints = 0
        self.x_p1, self.y_p1, self.x_p2, self.y_p2, self.currx, self.curry, self.x_p3, self.y_p3 = None, None, None, None, None, None, None, None
        self.angle, self.circ_rayon = None, -1
        self.setval = True
        if self.rb:
            self.rb.reset(True)
        if self.rb_arcs:
            self.rb_arcs.reset(True)
        self.rb=None
        self.rb_arcs=None

        self.canvas.refresh()

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True

