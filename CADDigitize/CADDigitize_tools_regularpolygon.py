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
from qgis.utils import iface
from math import *
from tools.calc import *
from tools.regularpolygon import *

#####################
#     RPolygon      #
#####################
class ToolBar:
    def __init__(self):
        self.optionsToolBar = iface.mainWindow().findChild(
                QToolBar, u"CADDigitize Options")
        self.clear()
        self.rpolygonOptions()

    def segmentsettingsRPolygon(self):
        settings = QSettings()
        settings.setValue("/CADDigitize/rpolygon/nbedges", self.spinBox.value())

    def rpolygonOptions(self):
        settings = QSettings()
        ###
        # Options
        ###
        # Add spinbox circle
        self.spinBox = QSpinBox(iface.mainWindow())
        self.spinBox.setMinimum(3)
        self.spinBox.setMaximum(9999)
        segvalue = settings.value("/CADDigitize/rpolygon/nbedges",36,type=int)
        if not segvalue:
            settings.setValue("/CADDigitize/rpolygon/nbedges", 36)
        self.spinBox.setValue(segvalue)
        self.spinBox.setSingleStep(1)
        self.spinBoxAction = self.optionsToolBar.addWidget(self.spinBox)
        self.spinBox.setToolTip( QCoreApplication.translate( "CADDigitize","Number of edges", None, QApplication.UnicodeUTF8))
        self.spinBoxAction.setEnabled(True)

        QObject.connect(self.spinBox, SIGNAL("valueChanged(int)"), self.segmentsettingsRPolygon)

    def clear(self):
        self.optionsToolBar.clear()


class RPolygonByCenterPointTool(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self,canvas)
        self.settings = QSettings()
        self.canvas=canvas
        self.nbPoints = 0
        self.rb = None
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
    def changegeomSRID(self, geom):
        layer = self.canvas.currentLayer()
        renderer = self.canvas.mapRenderer()
        layerCRSSrsid = layer.crs().srsid()
        projectCRSSrsid = renderer.destinationCrs().srsid()
        if layerCRSSrsid != projectCRSSrsid:
            g = QgsGeometry.fromPoint(geom)
            g.transform(QgsCoordinateTransform(projectCRSSrsid, layerCRSSrsid))
            retPoint = g.asPoint()
        else:
            retPoint = geom

        return retPoint


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
            (layerid, enabled, snapType, tolUnits, tol, avoidInt) = QgsProject.instance().snapSettingsForLayer(layer.id())
            startingPoint = QPoint(x,y)
            snapper = QgsMapCanvasSnapper(self.canvas)
            (retval,result) = snapper.snapToCurrentLayer (startingPoint, snapType, tol)
            if result <> [] and enabled == True:
                point = self.changegeomSRID(result[0].snappedVertex)
            else:
                (retval,result) = snapper.snapToBackgroundLayers(startingPoint)
                print result
                if result <> []:
                    point = self.changegeomSRID(result[0].snappedVertex)
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
            segments = self.settings.value("/CADDigitize/rpolygon/nbedges",5,type=int)
            geom = RegularPolygon.getRPolygonCenterCorner(QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.x_p2, self.y_p2), segments)

            self.nbPoints = 0
            self.x_p1, self.y_p1, self.x_p2, self.y_p2 = None, None, None, None

            self.emit(SIGNAL("rbFinished(PyQt_PyObject)"), geom)

        if self.rb:return


    def canvasMoveEvent(self,event):
        segments = self.settings.value("/CADDigitize/rpolygon/nbedges",5,type=int)
        if not self.rb:return
        currpoint = self.toMapCoordinates(event.pos())
        currx = currpoint.x()
        curry = currpoint.y()
    	self.rb.setToGeometry(RegularPolygon.getRPolygonCenterCorner(QgsPoint(self.x_p1, self.y_p1), QgsPoint(currx, curry), segments), None)

    def showSettingsWarning(self):
        pass

    def activate(self):
        self.canvas.setCursor(self.cursor)
        self.optionsToolbar = ToolBar()

    def deactivate(self):
        self.nbPoints = 0
        self.x_p1, self.y_p1, self.x_p2, self.y_p2 = None, None, None, None
        if self.rb:
            self.rb.reset(True)
        self.rb=None

        self.optionsToolbar.clear()

        self.canvas.refresh()

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True


class RPolygon2CornersTool(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self,canvas)
        self.settings = QSettings()
        self.canvas=canvas
        self.nbPoints = 0
        self.rb = None
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
    def changegeomSRID(self, geom):
        layer = self.canvas.currentLayer()
        renderer = self.canvas.mapRenderer()
        layerCRSSrsid = layer.crs().srsid()
        projectCRSSrsid = renderer.destinationCrs().srsid()
        if layerCRSSrsid != projectCRSSrsid:
            g = QgsGeometry.fromPoint(geom)
            g.transform(QgsCoordinateTransform(projectCRSSrsid, layerCRSSrsid))
            retPoint = g.asPoint()
        else:
            retPoint = geom

        return retPoint


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
            (layerid, enabled, snapType, tolUnits, tol, avoidInt) = QgsProject.instance().snapSettingsForLayer(layer.id())
            startingPoint = QPoint(x,y)
            snapper = QgsMapCanvasSnapper(self.canvas)
            (retval,result) = snapper.snapToCurrentLayer (startingPoint, snapType, tol)
            if result <> [] and enabled == True:
                point = self.changegeomSRID(result[0].snappedVertex)
            else:
                (retval,result) = snapper.snapToBackgroundLayers(startingPoint)
                print result
                if result <> []:
                    point = self.changegeomSRID(result[0].snappedVertex)
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
            segments = self.settings.value("/CADDigitize/rpolygon/nbedges",5,type=int)
            geom = RegularPolygon.getRPolygon2Corners(QgsPoint(self.x_p1, self.y_p1), QgsPoint(self.x_p2, self.y_p2), segments)

            self.nbPoints = 0
            self.x_p1, self.y_p1, self.x_p2, self.y_p2 = None, None, None, None

            self.emit(SIGNAL("rbFinished(PyQt_PyObject)"), geom)

        if self.rb:return


    def canvasMoveEvent(self,event):
        segments = self.settings.value("/CADDigitize/rpolygon/nbedges",5,type=int)
        if not self.rb:return
        currpoint = self.toMapCoordinates(event.pos())
        currx = currpoint.x()
        curry = currpoint.y()
    	self.rb.setToGeometry(RegularPolygon.getRPolygon2Corners(QgsPoint(self.x_p1, self.y_p1), QgsPoint(currx, curry), segments), None)

    def showSettingsWarning(self):
        pass

    def activate(self):
        self.canvas.setCursor(self.cursor)
        self.optionsToolbar = ToolBar()

    def deactivate(self):
        self.nbPoints = 0
        self.x_p1, self.y_p1, self.x_p2, self.y_p2 = None, None, None, None
        if self.rb:
            self.rb.reset(True)
        self.rb=None

        self.optionsToolbar.clear()

        self.canvas.refresh()

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True


