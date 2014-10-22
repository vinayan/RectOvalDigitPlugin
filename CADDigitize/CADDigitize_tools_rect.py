# -*- coding: utf-8 -*-

# List comprehensions in canvasMoveEvent functions are
# adapted from Benjamin Bohard`s part of rectovaldiams plugin.

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from math import *
from tools.calc import *
from CADDigitize_dialog import Ui_CADDigitizeDialog

class RectBy3PointsTool(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self,canvas)
        self.canvas = canvas
        self.nbPoints = 0
        self.rb = None
        self.x_p1, self.y_p1, self.x_p2, self.y_p2, self.x_p3, self.y_p3, self.x_p4, self.y_p4 = None, None, None, None, None, None, None, None
        self.length = 0
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

    def calcPoint(x,y):
        return p.x() + self.length * cos(radians(90) + self.angle_exist), self.p.y() + self.length * sin(radians(90) + self.angle_exist)

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
            self.x_p3, self.y_p3 = self.x_p2 + self.length * cos(radians(90) + self.angle_exist), self.y_p2 + self.length * sin(radians(90) + self.angle_exist)
            self.x_p4, self.y_p4 = self.x_p1 + self.length * cos(radians(90) + self.angle_exist), self.y_p1 + self.length * sin(radians(90) + self.angle_exist)


        self.nbPoints += 1

        if self.nbPoints == 3:
            geom = QgsGeometry.fromPolygon([[QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.x_p2, self.y_p2), QgsPoint(self.x_p3, self.y_p3), QgsPoint(self.x_p4, self.y_p4)]])

            self.nbPoints = 0
            self.x_p1, self.y_p1, self.x_p2, self.y_p2, self.x_p3, self.y_p3, self.x_p4, self.y_p4 = None, None, None, None, None, None, None, None

            self.emit(SIGNAL("rbFinished(PyQt_PyObject)"), geom)

        if self.rb:return

    def canvasMoveEvent(self,event):

        if not self.rb:return
        currpoint = self.toMapCoordinates(event.pos())
        currx = currpoint.x()
        curry = currpoint.y()
        if self.nbPoints == 1:
            self.rb.setToGeometry(QgsGeometry.fromPolyline([QgsPoint(self.x_p1, self.y_p1), QgsPoint(currx, curry)]), None)
        if self.nbPoints >= 2:
            side = calc_isCollinear(QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.x_p2, self.y_p2), currpoint) # check if x_p2 > x_p1 and inverse side
            if self.x_p1 < self.x_p2:
                side *= -1
            self.length = QgsDistanceArea().measureLine(QgsPoint(self.x_p2, self.y_p2), QgsPoint(currx, curry)) * side
            self.x_p3, self.y_p3 = self.x_p2 + self.length * cos(radians(90) + self.angle_exist), self.y_p2 + self.length * sin(radians(90) + self.angle_exist)
            self.x_p4, self.y_p4 = self.x_p1 + self.length * cos(radians(90) + self.angle_exist), self.y_p1 + self.length * sin(radians(90) + self.angle_exist)
            geom = QgsGeometry.fromPolygon([[QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.x_p2, self.y_p2), QgsPoint(self.x_p3, self.y_p3), QgsPoint(self.x_p4, self.y_p4)]])
            self.rb.setToGeometry(geom, None)

    def showSettingsWarning(self):
        pass

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def deactivate(self):
        pass

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True


class RectByExtentTool(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self,canvas)
        self.canvas=canvas
        self.nbPoints = 0
        self.rb=None
        self.mCtrl=None
        self.x_p1, self.y_p1, self.x_p2, self.y_p2 = None, None, None, None
        #our own fancy cursor
        self.cursor = QCursor(QPixmap(["16 16 3 1",
                                       "      c None",
                                       ".     c #FF0000",
                                       "+     c #17a51a",
                                       "                ",
                                       "       +.+      ",
                                       "      ++.++     ",
                                       "     +.....+    ",
                                       "    +.  .  .+   ",
                                       "   +.   .   .+  ",
                                       "  +.    .    .+ ",
                                       " ++.    .    .++",
                                       " ... ...+... ...",
                                       " ++.    .    .++",
                                       "  +.    .    .+ ",
                                       "   +.   .   .+  ",
                                       "   ++.  .  .+   ",
                                       "    ++.....+    ",
                                       "      ++.++     ",
                                       "       +.+      "]))



    def keyPressEvent(self,  event):
        if event.key() == Qt.Key_Control:
            self.mCtrl = True


    def keyReleaseEvent(self,  event):
        if event.key() == Qt.Key_Control:
            self.mCtrl = False

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
            pt1 = (self.x_p1, self.y_p1)
            pt2 = (self.x_p1, self.y_p2)
            pt3 = (self.x_p2, self.y_p2)
            pt4 = (self.x_p2, self.y_p1)
            points = [pt1, pt2, pt3, pt4]
            polygon = [QgsPoint(i[0],i[1]) for i in points]
            geom = QgsGeometry.fromPolygon([polygon])

            self.nbPoints = 0
            self.x_p1, self.y_p1, self.x_p2, self.y_p2 = None, None, None, None

            self.emit(SIGNAL("rbFinished(PyQt_PyObject)"), geom)

        if self.rb:return


    def canvasMoveEvent(self,event):
        if not self.rb:return
        currpoint = self.toMapCoordinates(event.pos())
        currx = currpoint.x()
        curry = currpoint.y()
        self.rb.reset(True)
        pt1 = (self.x_p1, self.y_p1)
        pt2 = (self.x_p1, curry)
        pt3 = (currx, curry)
        pt4 = (currx, self.y_p1)
        points = [pt1, pt2, pt3, pt4]
        polygon = [QgsPoint(i[0],i[1]) for i in points]
	self.rb.setToGeometry(QgsGeometry.fromPolygon([polygon]), None)
        #delete [self.rb.addPoint( point ) for point in polygon]

    def showSettingsWarning(self):
        pass

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def deactivate(self):
        pass

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True

# Tool class
class RectFromCenterTool(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self,canvas)
        self.canvas=canvas
        self.nbPoints = 0
        self.rb=None
        self.mCtrl=None
        self.xc, self.yc, self.x_p2, self.y_p2 = None, None, None, None
        #our own fancy cursor
        self.cursor = QCursor(QPixmap(["16 16 3 1",
                                       "      c None",
                                       ".     c #FF0000",
                                       "+     c #17a51a",
                                       "                ",
                                       "       +.+      ",
                                       "      ++.++     ",
                                       "     +.....+    ",
                                       "    +.  .  .+   ",
                                       "   +.   .   .+  ",
                                       "  +.    .    .+ ",
                                       " ++.    .    .++",
                                       " ... ...+... ...",
                                       " ++.    .    .++",
                                       "  +.    .    .+ ",
                                       "   +.   .   .+  ",
                                       "   ++.  .  .+   ",
                                       "    ++.....+    ",
                                       "      ++.++     ",
                                       "       +.+      "]))



    def keyPressEvent(self,  event):
        if event.key() == Qt.Key_Control:
            self.mCtrl = True


    def keyReleaseEvent(self,  event):
        if event.key() == Qt.Key_Control:
            self.mCtrl = False

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
            self.xc = pointMap.x()
            self.yc = pointMap.y()
        else:
            self.x_p2 = pointMap.x()
            self.y_p2 = pointMap.y()

        self.nbPoints += 1

        if self.nbPoints == 2:
            xOffset = abs( self.x_p2 - self.xc)
            yOffset = abs( self.y_p2 - self.yc)
            pt1 = QgsPoint(-xOffset, -yOffset)
            pt2 = QgsPoint(-xOffset, yOffset)
            pt3 = QgsPoint(xOffset, yOffset)
            pt4 = QgsPoint(xOffset, -yOffset)
            points = [pt1, pt2, pt3, pt4]
            polygon = [QgsPoint(self.xc + i[0], self.yc + i[1]) for i in points]
            geom = QgsGeometry.fromPolygon([polygon])

            self.nbPoints = 0
            self.xc, self.yc, self.x_p2, self.y_p2 = None, None, None, None

            self.emit(SIGNAL("rbFinished(PyQt_PyObject)"), geom)

        if self.rb:return

    def canvasMoveEvent(self,event):
        if not self.rb:return
        currpoint = self.toMapCoordinates(event.pos())
        currx = currpoint.x()
        curry = currpoint.y()
        xOffset = abs( currx - self.xc)
        yOffset = abs( curry - self.yc)
        self.rb.reset(True)
        pt1 = QgsPoint(-xOffset, -yOffset)
        pt2 = QgsPoint(-xOffset, yOffset)
        pt3 = QgsPoint(xOffset, yOffset)
        pt4 = QgsPoint(xOffset, -yOffset)
        points = [pt1, pt2, pt3, pt4]
        polygon = [QgsPoint(self.xc + i[0], self.yc + i[1]) for i in points]
	self.rb.setToGeometry(QgsGeometry.fromPolygon([polygon]), None)
        #delete [self.rb.addPoint( point ) for point in polygon]

    def showSettingsWarning(self):
        pass

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def deactivate(self):
        pass

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True

# Tool class
class SquareFromCenterTool(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self,canvas)
        self.canvas=canvas
        self.nbPoints = 0
        self.rb=None
        self.mCtrl=None
        self.xc, self.yc, self.x_p2, self.y_p2 = None, None, None, None
        #our own fancy cursor
        self.cursor = QCursor(QPixmap(["16 16 3 1",
                                       "      c None",
                                       ".     c #FF0000",
                                       "+     c #17a51a",
                                       "                ",
                                       "       +.+      ",
                                       "      ++.++     ",
                                       "     +.....+    ",
                                       "    +.  .  .+   ",
                                       "   +.   .   .+  ",
                                       "  +.    .    .+ ",
                                       " ++.    .    .++",
                                       " ... ...+... ...",
                                       " ++.    .    .++",
                                       "  +.    .    .+ ",
                                       "   +.   .   .+  ",
                                       "   ++.  .  .+   ",
                                       "    ++.....+    ",
                                       "      ++.++     ",
                                       "       +.+      "]))



    def keyPressEvent(self,  event):
        if event.key() == Qt.Key_Control:
            self.mCtrl = True


    def keyReleaseEvent(self,  event):
        if event.key() == Qt.Key_Control:
            self.mCtrl = False

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
            self.xc = pointMap.x()
            self.yc = pointMap.y()
        else:
            self.x_p2 = pointMap.x()
            self.y_p2 = pointMap.y()

        self.nbPoints += 1

        if self.nbPoints == 2:
            currpoint = self.toMapCoordinates(event.pos())
            distance= sqrt(currpoint.sqrDist( self.xc, self.yc ))
            offset = distance/sqrt(2)
            pt1 = (-offset, -offset)
            pt2 = (-offset, offset)
            pt3 = (offset, offset)
            pt4 = (offset, -offset)
            points = [pt1, pt2, pt3, pt4]
            polygon = [QgsPoint(self.xc + i[0], self.yc + i[1]) for i in points]
            geom = QgsGeometry.fromPolygon([polygon])

            self.nbPoints = 0
            self.xc, self.yc, self.x_p2, self.y_p2 = None, None, None, None

            self.emit(SIGNAL("rbFinished(PyQt_PyObject)"), geom)

        if self.rb:return


    def canvasMoveEvent(self,event):
        if not self.rb:return
        currpoint = self.toMapCoordinates(event.pos())
        distance= sqrt(currpoint.sqrDist( self.xc, self.yc ))
        offset = distance/sqrt(2)
        self.rb.reset(True)
        pt1 = (-offset, -offset)
        pt2 = (-offset, offset)
        pt3 = (offset, offset)
        pt4 = (offset, -offset)
        points = [pt1, pt2, pt3, pt4]
        polygon = [QgsPoint(i[0]+self.xc,i[1]+self.yc) for i in points]
        #delete [self.rb.addPoint( point ) for point in polygon]
	self.rb.setToGeometry(QgsGeometry.fromPolygon([polygon]), None)

    def showSettingsWarning(self):
        pass

    def activate(self):
        self.canvas.setCursor(self.cursor)

    def deactivate(self):
        pass

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True


