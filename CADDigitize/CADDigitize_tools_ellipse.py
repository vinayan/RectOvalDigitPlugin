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
from tools.ellipse import *



class EllipseByCenter2PointsTool(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self,canvas)
        self.settings = QSettings()
        self.canvas = canvas
        self.nbPoints = 0
        self.angle_exist = 0
        self.rb = None
        self.rb_axis_a, self.rb_axis_b = None, None
        self.xc, self.yc, self.x_p1, self.y_p1, self.x_p2, self.y_p2 = None, None, None, None, None, None
        self.length = 0
        self.axis_a, self.axis_b = 0,0
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
            if self.rb:
                self.rb.reset(True)
            if self.rb_axis_a:
                self.rb_axis_a.reset(True)
            if self.rb_axis_b:
                self.rb_axis_b.reset(True)
            self.rb, self.rb_axis_a, self.rb_axis_b = None, None, None
            self.nbPoints = 0
            self.angle_exist = 0
            self.xc, self.yc, self.x_p1, self.y_p1, self.x_p2, self.y_p2 = None, None, None, None, None, None
            self.length = 0
            self.axis_a, self.axis_b = 0,0
        
            self.canvas.refresh()
            return

    def calcPoint(x,y):
        return p.x() + self.length * cos(radians(90) + self.angle_exist), self.p.y() + self.length * sin(radians(90) + self.angle_exist)

    def canvasPressEvent(self,event):
        layer = self.canvas.currentLayer()
        if self.nbPoints == 0:
            color = QColor(255,0,0)
            self.rb = QgsRubberBand(self.canvas, True)
            self.rb.setColor(color)
            self.rb.setWidth(1)

            self.rb_axis_a = QgsRubberBand(self.canvas, False)
            self.rb_axis_b = QgsRubberBand(self.canvas, False)
            self.rb_axis_a.setColor(QColor(0,0,255))
            self.rb_axis_b.setColor(QColor(0,0,255))
            self.rb_axis_a.setWidth(1)
            self.rb_axis_b.setWidth(1)
        elif self.nbPoints == 2:
            self.rb.reset(True)
            self.rb_axis_a.reset(True)
            self.rb_axis_b.reset(True)
            self.rb, self.rb_axis_a, self.rb_axis_b = None, None, None

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
            self.xc = pointMap.x()
            self.yc = pointMap.y()
        elif self.nbPoints == 1:
            self.x_p1 = pointMap.x()
            self.y_p1 = pointMap.y()
            self.angle_exist = calcAngleExistant(QgsPoint(self.xc, self.yc), QgsPoint(self.x_p1, self.y_p1))
            self.axis_a = QgsDistanceArea().measureLine(QgsPoint(self.xc, self.yc), QgsPoint(self.x_p1, self.y_p1))
            self.rb_axis_a.setToGeometry(QgsGeometry.fromPolyline([QgsPoint(self.xc, self.yc), QgsPoint(self.x_p1, self.y_p1)]), None)
        else:
            self.x_p2, self.y_p2 = self.xc + self.length * cos(radians(90) + self.angle_exist), self.yc + self.length * sin(radians(90) + self.angle_exist)
            self.axis_b = QgsDistanceArea().measureLine(QgsPoint(self.xc, self.yc), QgsPoint(self.x_p2, self.y_p2))


        self.nbPoints += 1

        if self.nbPoints == 3:
            segments = self.settings.value("/CADDigitize/ellipse/segments",36,type=int)
            geom = Ellipse.getEllipse(QgsPoint(self.xc, self.yc), self.axis_a, self.axis_b, self.angle_exist, segments)

            self.nbPoints = 0
            self.x_p1, self.y_p1, self.x_p2, self.y_p2, self.xc, self.yc = None, None, None, None, None, None

            self.emit(SIGNAL("rbFinished(PyQt_PyObject)"), geom)

        if self.rb:return

    def canvasMoveEvent(self,event):

        if not self.rb:return
        currpoint = self.toMapCoordinates(event.pos())
        currx = currpoint.x()
        curry = currpoint.y()
        if self.nbPoints == 1:
            self.rb_axis_a.setToGeometry(QgsGeometry.fromPolyline([QgsPoint(self.xc, self.yc), QgsPoint(currx, curry)]), None)
        if self.nbPoints >= 2:
            self.length = QgsDistanceArea().measureLine(QgsPoint(self.xc, self.yc), QgsPoint(currx, curry))
            self.x_p2, self.y_p2 = self.xc + self.length * cos(radians(90) + self.angle_exist), self.yc + self.length * sin(radians(90) + self.angle_exist)
            self.axis_b = QgsDistanceArea().measureLine(QgsPoint(self.xc, self.yc), QgsPoint(self.x_p2, self.y_p2))
            self.rb_axis_b.setToGeometry(QgsGeometry.fromPolyline([QgsPoint(self.xc, self.yc), QgsPoint(self.x_p2, self.y_p2)]), None)

            segments = self.settings.value("/CADDigitize/ellipse/segments",36,type=int)
            
            geom = Ellipse.getEllipse(QgsPoint(self.xc, self.yc), self.axis_a, self.axis_b, self.angle_exist, segments)
            
            self.rb.setToGeometry(geom, None)

    def showSettingsWarning(self):
        pass

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def deactivate(self):
        if self.rb:
            self.rb.reset(True)
        if self.rb_axis_a:
            self.rb_axis_a.reset(True)
        if self.rb_axis_b:
            self.rb_axis_b.reset(True)
        self.rb, self.rb_axis_a, self.rb_axis_b = None, None, None
        self.nbPoints = 0
        self.angle_exist = 0
        self.xc, self.yc, self.x_p1, self.y_p1, self.x_p2, self.y_p2 = None, None, None, None, None, None
        self.length = 0
        self.axis_a, self.axis_b = 0,0
        
        self.canvas.refresh()

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True

class EllipseByFociPointTool(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self,canvas)
        self.settings = QSettings()
        self.canvas = canvas
        self.nbPoints = 0
        self.rb = None
        self.x_p1, self.y_p1, self.x_p2, self.y_p2, self.x_p3, self.y_p3 = None, None, None, None, None, None # P1 and P2 are foci
        self.distP1P3, self.distP2P3 = 0,0
        self.distTotal = 0
        self.angle_exist = 0
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
            self.x_p1, self.y_p1, self.x_p2, self.y_p2, self.x_p3, self.y_p3 = None, None, None, None, None, None # P1 and P2 are foci
            self.distP1P3, self.distP2P3 = 0,0
            self.distTotal = 0
            self.angle_exist = 0
            if self.rb:
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
            self.angle_exist = calcAngleExistant(QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.x_p2, self.y_p2))
        else:
            self.x_p3 = pointMap.x()
            self.y_p3 = pointMap.y()

        self.nbPoints += 1

        if self.nbPoints == 3:
        
            segments = self.settings.value("/CADDigitize/ellipse/segments",36,type=int)
            geom = Ellipse.getEllipseFromFoci(QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.x_p2, self.y_p2), QgsPoint(self.x_p3, self.y_p3), segments)
            self.nbPoints = 0
            self.x_p1, self.y_p1, self.x_p2, self.y_p2, self.x_p3, self.y_p3 = None, None, None, None, None, None
            
            self.emit(SIGNAL("rbFinished(PyQt_PyObject)"), geom)

        if self.rb:return


    def canvasMoveEvent(self,event):

        if not self.rb:return
        currpoint = self.toMapCoordinates(event.pos())
        currx = currpoint.x()
        curry = currpoint.y()
        if self.nbPoints == 1:
            self.rb.setToGeometry(QgsGeometry.fromPolyline([QgsPoint(self.x_p1, self.y_p1), QgsPoint(currx, curry)]), None)

        if self.nbPoints > 1:
            segments = self.settings.value("/CADDigitize/ellipse/segments",36,type=int)
            self.rb.setToGeometry(Ellipse.getEllipseFromFoci(QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.x_p2, self.y_p2), QgsPoint(currx, curry), segments), None)

    def showSettingsWarning(self):
        pass

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def deactivate(self):
        self.nbPoints = 0
        self.x_p1, self.y_p1, self.x_p2, self.y_p2, self.x_p3, self.y_p3 = None, None, None, None, None, None # P1 and P2 are foci
        self.distP1P3, self.distP2P3 = 0,0
        self.distTotal = 0
        self.angle_exist = 0
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



class EllipseFromCenterTool(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self,canvas)
        self.settings = QSettings()
        self.canvas=canvas
        self.rb = None
        self.nbPoints = 0
        self.x_p1, self.y_p1, self.x_p2, self.y_p2 = None, None, None, None
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
            self.x_p1, self.y_p1, self.x_p2, self.y_p2 = None, None, None, None
            if self.rb:
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
        else:
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
        else:
            self.x_p2 = pointMap.x()
            self.y_p2 = pointMap.y()

        self.nbPoints += 1

        if self.nbPoints == 2:
            xOffset = abs( self.x_p2 - self.x_p1)
            yOffset = abs( self.y_p2 - self.y_p1)
            segments = self.settings.value("/CADDigitize/ellipse/segments",36,type=int)
            
            geom = Ellipse.getEllipse(QgsPoint(self.x_p1, self.y_p1), xOffset, yOffset, segments=segments)

            self.nbPoints = 0
            self.x_p1, self.y_p1, self.x_p2, self.y_p2 = None, None, None, None
        
            self.emit(SIGNAL("rbFinished(PyQt_PyObject)"), geom)

        if self.rb:return


            
    def canvasMoveEvent(self,event):
        if not self.rb:return

        currpoint = self.toMapCoordinates(event.pos())
        currx = currpoint.x()
        curry = currpoint.y()
        xOffset = abs( currx - self.x_p1)
        yOffset = abs( curry - self.y_p1)
        segments = self.settings.value("/CADDigitize/ellipse/segments",36,type=int)

        self.rb.setToGeometry(Ellipse.getEllipse(QgsPoint(self.x_p1, self.y_p1), xOffset, yOffset, segments=segments), None)
  

    def showSettingsWarning(self):
        pass
    
    def activate(self):
        self.canvas.setCursor(self.cursor)
        
    def deactivate(self):
        self.nbPoints = 0
        self.x_p1, self.y_p1, self.x_p2, self.y_p2 = None, None, None, None
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
        
 
# Tool class
class EllipseByExtentTool(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self,canvas)
        self.settings = QSettings()
        self.canvas=canvas
        self.rb = None
        self.nbPoints = 0
        self.x_p1, self.y_p1, self.x_p2, self.y_p2 = None, None, None, None
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
            self.x_p1, self.y_p1, self.x_p2, self.y_p2 = None, None, None, None
            if self.rb:
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
        else:
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
        else:
            self.x_p2 = pointMap.x()
            self.y_p2 = pointMap.y()

        self.nbPoints += 1

        if self.nbPoints == 2:
            xc = self.x_p1 + ((self.x_p2 - self.x_p1) / 2)
            yc = self.y_p1 + ((self.y_p2 - self.y_p1) / 2) 
            xOffset = (abs( self.x_p2 - self.x_p1))/2
            yOffset = (abs( self.y_p2 - self.y_p1))/2
            segments = self.settings.value("/CADDigitize/ellipse/segments",36,type=int)
            
            geom = Ellipse.getEllipse(QgsPoint(xc, yc), xOffset, yOffset, segments=segments)

            self.nbPoints = 0
            self.x_p1, self.y_p1, self.x_p2, self.y_p2 = None, None, None, None
        
            self.emit(SIGNAL("rbFinished(PyQt_PyObject)"), geom)

        if self.rb:return


            
    def canvasMoveEvent(self,event):
        if not self.rb:return
        currpoint = self.toMapCoordinates(event.pos())
        currx = currpoint.x()
        curry = currpoint.y()
            
        xc = self.x_p1 + ((currx - self.x_p1) / 2)
        yc = self.y_p1 + ((curry - self.y_p1) / 2) 
        xOffset = (abs( currx - self.x_p1))/2
        yOffset = (abs( curry - self.y_p1))/2
        segments = self.settings.value("/CADDigitize/ellipse/segments",36,type=int)
            
        
        self.rb.setToGeometry(Ellipse.getEllipse(QgsPoint(xc, yc), xOffset, yOffset, segments=segments), None)
  

    def showSettingsWarning(self):
        pass
    
    def activate(self):
        self.canvas.setCursor(self.cursor)
        
    def deactivate(self):
        self.nbPoints = 0
        self.x_p1, self.y_p1, self.x_p2, self.y_p2 = None, None, None, None
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


class EllipseByCenter3PointsTool(QgsMapTool):
    pass

class EllipseBy4PointsTool(QgsMapTool):
    pass

