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
from tools.circle import *

# Arrondi
# Rayon
# Oui ou non on supprime l'angle si accolé
# possibilité prolongation ou non
class ModifyFilletTool(QgsMapTool):
    pass

# Chanfrein
# Découpe 1
# Découpe 2
# Oui ou non on supprime l'angle si accolé
# possibilité prolongation ou non
class ModifyBevelTool(QgsMapTool):
    pass

# Parallèle
class ModifyOffsetTool(QgsMapTool):
    """
        Offset can be on a segment or a feature.

    """

    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.layer = None
        self.setval = False # flag for setting a value
        self.rb1, self.rb2 = None, None # Ruberbands rb1: for selected segment/Feature rb2: for the result
        self.nbPoints = 0
        self.side = 0
        self.geom = None # Final geometry
        # our own fancy cursor
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


    def keyReleaseEvent(self,  event):
        if event.key() == Qt.Key_Escape:    # if escape, clear all
            self.clear()
        return

    def canvasPressEvent(self, event):


        x = event.pos().x()
        y = event.pos().y()

        flag = False

        point1, point2 = None, None # Points for segment
        feat, layerSnapped = None, None # Feature and layer snapped

        # Well know routine for snap segments.
        (layerid, enabled, snapType, tolUnits, tol,
         avoidInt) = QgsProject.instance().snapSettingsForLayer(self.layer.id())
        startingPoint = QPoint(x, y)
        snapper = QgsMapCanvasSnapper(self.canvas)
        (retval, self.result) = snapper.snapToCurrentLayer(
            startingPoint, snapType, tol)
        if self.result <> []:
            if self.segmentChoice.isChecked():
                point1 = self.result[0].beforeVertex
                point2 = self.result[0].afterVertex
            elif self.featureChoice.isChecked():
                feat = self.result[0].snappedAtGeometry
                layerSnapped = self.result[0].layer
            flag = True
        else:
            (retval, self.result) = snapper.snapToBackgroundLayers(
                startingPoint)
            if self.result <> []:
                if self.segmentChoice.isChecked():
                    point1 = self.result[0].beforeVertex
                    point2 = self.result[0].afterVertex
                elif self.featureChoice.isChecked():
                    layerSnapped = self.result[0].layer
                    feat = self.result[0].snappedAtGeometry
                flag = True



        if self.nbPoints == 1:
            self.nbPoints += 1

        if flag == True:
            # Options for offset. Using QGis defaults
            self.of_join = QSettings().value("Qgis/digitizing/offset_join_style",0,type=int)
            self.of_quad = QSettings().value("Qgis/digitizing/offset_quad_seg",8,type=int)
            self.of_miter = QSettings().value("Qgis/digitizing/offset_miter_limit",5,type=int)
            self.nbPoints = 1 # One point is clicked

        if self.nbPoints == 1:
            # define rb1
            self.rb1 = QgsRubberBand(self.canvas, True)
            self.rb1.setColor(QColor(0, 0, 255))
            self.rb1.setWidth(3)

            # define rb2
            self.rb2 = QgsRubberBand(self.canvas, True)
            self.rb2.setColor(QColor(0, 0, 255))
            self.rb2.setWidth(3)


            # create geom. Segment or Feature
            # TODO: MultiLineString
            if self.segmentChoice.isChecked():
                self.geom = QgsGeometry.fromPolyline([point1, point2])
            elif self.featureChoice.isChecked():
                self.geom = [l.geometry() for l in layerSnapped.getFeatures(QgsFeatureRequest(feat))][0] # get the geometry of the first iterator
                # convert to Polyline for offset tools
                if self.geom.type() == QGis.Polygon:
                    self.geom = self.geom.convertToType(QGis.Line, False)

            print self.geom.exportToWkt()
            self.rb1.setToGeometry(self.geom, None)


            self.canvas.refresh()
            return

        if self.nbPoints == 2:
            # Conversion to
            if self.layer.geometryType() == QGis.Polygon:
                self.geom = self.geom.offsetCurve(self.distanceValue.value() * -self.side, self.of_quad, self.of_join, self.of_miter ).convertToType(QGis.Polygon, False)
            else:
                self.geom = self.geom.offsetCurve(self.distanceValue.value() * -self.side, self.of_quad, self.of_join, self.of_miter )

            self.emit(SIGNAL("rbFinished(PyQt_PyObject)"), self.geom)

            self.clear()

            return


    def canvasMoveEvent(self,event):

        if not self.rb1:return
        currpoint = self.toMapCoordinates(event.pos())
        currx = currpoint.x()
        curry = currpoint.y()

        if self.nbPoints == 1:
                (distance, nearPoint, ptAfterVertex) = self.geom.closestSegmentWithContext(currpoint)
                self.side = calc_isCollinear(self.geom.vertexAt(ptAfterVertex-1), self.geom.vertexAt(ptAfterVertex), currpoint)
                self.rb2.setToGeometry(self.geom.offsetCurve(self.distanceValue.value() * -self.side, self.of_quad, self.of_join, self.of_miter ), None)

    def clear(self):
        self.setVal = False
        self.geom = None
        self.nbPoints = 0
        self.side = 0
        if self.rb1:
            self.rb1.reset(True)
        if self.rb2:
            self.rb2.reset(True)
        self.rb1, self.rb2 = None, None

        self.canvas.refresh()

    def toggle(self):
        self.layer = self.canvas.currentLayer()
        if self.layer <> None:
            if self.layer.isEditable():
                if self.layer.geometryType() == QGis.Polygon:
                    self.segmentChoice.setChecked(Qt.Unchecked)
                    self.featureChoice.setChecked(Qt.Checked)
                    self.segmentChoice.setEnabled(False)
                    self.featureChoice.setEnabled(False)
                elif self.layer.geometryType() == QGis.Line:
                    self.segmentChoice.setEnabled(True)
                    self.featureChoice.setEnabled(True)


    def activate(self):
        self.layer = self.canvas.currentLayer()
        QObject.connect(iface, SIGNAL("currentLayerChanged(QgsMapLayer*)"), self.toggle)

        self.canvas.setCursor(self.cursor)
        self.optionsToolBar = iface.mainWindow().findChild(
            QToolBar, u"CADDigitize Options")
        self.segmentChoice = QRadioButton(QCoreApplication.translate(
            "CADDigitize", "Segment", None, QApplication.UnicodeUTF8))
        self.segmentChoice.setChecked(Qt.Checked)
        self.featureChoice = QRadioButton(QCoreApplication.translate(
            "CADDigitize", "Feature", None, QApplication.UnicodeUTF8))
        self.segmentChoiceAction = self.optionsToolBar.addWidget(self.segmentChoice)
        self.featureChoiceAction = self.optionsToolBar.addWidget(self.featureChoice)

        if self.layer.geometryType() == QGis.Polygon:
            self.segmentChoice.setChecked(Qt.Unchecked)
            self.featureChoice.setChecked(Qt.Checked)
            self.segmentChoice.setEnabled(False)
            self.featureChoice.setEnabled(False)
        elif self.layer.geometryType() == QGis.Line:
            self.segmentChoice.setEnabled(True)
            self.featureChoice.setEnabled(True)


        self.optionsToolBar.addSeparator()

        self.distanceValue = QDoubleSpinBox()
        self.distanceValue.setMaximum(999999999.0)
        self.distanceValue.setMinimum(0.0)
        self.distanceValue.setDecimals(6)
        self.distanceValueAction = self.optionsToolBar.addWidget(self.distanceValue)


    def deactivate(self):
        self.optionsToolBar.clear()
        self.clear()
        QObject.disconnect(iface, SIGNAL("currentLayerChanged(QgsMapLayer*)"), self.toggle)


    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True

# Rotation
class ModifyRotationTool(QgsMapTool):
    pass


class ModifyTrimExtendTool(QgsMapTool):

    """

        ModifyTrimExtendTool can shorten or lenghten geometry to touches the edges of an other geometry.
        First select the "limit", second select the feature to trim/extend.
        You can trim/extend the "limit" if you choose "two" options in this case, is like "Trim / Extend Two" of LibreCad.

        Options are: "New", "Modify"
        New: Create a new feature with the result of the trim/extend operation. For a Polygon, Two is automatically checked.
        Modify: Modify the feature.
        Both can be checked

        If two is checked:
        New: Create a new feature as an union of the two geom produce with Trim/Extend.
        Modify: If both are editable, both are trimed/extended, if not, only the second segment is modified.

    """

    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.nbPoints = 0   # Number of click. Max is 2
        self.rb1, self.rb2 = None, None  # Ruberband for two segments
        # Points before and after Snap vertex
        self.point1, self.point2 = None, None
        # p1 first segment ; p2 second segment. px1 for first point on segment
        # ; px2 for second point on segment
        self.p11, self.p12, self.p21, self.p22 = None, None, None, None
        # our own fancy cursor
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

    def keyReleaseEvent(self,  event):
        if event.key() == Qt.Key_Escape:    # if escape, clear all
            self.clear()
        return

    def trimextend(self):
        """
            Cases:
            1)
            p1----pi---p2 or p2----pi-----p1
            [p1pi] <= [p1p2] and [p1pi] <= [p1p2]

            2)
            p1----p2---pi or pi----p2----p1
            p1pi >= p2pi

            3)
            pi----p1----p2 or p2-----p1----pi
            p2pi > p1pi

        """
        # get intersection of the segments
        p_inter = seg_intersect(self.p11, self.p12, self.p21, self.p22)
        # convert numpy array to QgsPoint
        p1 = npArray_qgsPoint(self.p21)
        p2 = npArray_qgsPoint(self.p22)

        p3 = npArray_qgsPoint(self.p11)
        p4 = npArray_qgsPoint(self.p12)
        # You can get an intersection even if segmets are "quasi" parellel. Fix a tolerance for difference between slopes
        p = math.fabs(calcPente(p1, p2) - calcPente(p3, p4) )
        print DEFAULT_SEGMENT_EPSILON
        if p_inter == None or p < DEFAULT_SEGMENT_EPSILON:
            iface.messageBar().pushMessage(QCoreApplication.translate("CADDigitize", "Error", None, QApplication.UnicodeUTF8),
                                           QCoreApplication.translate("CADDigitize", "Segments are parallels", None, QApplication.UnicodeUTF8), level=QgsMessageBar.CRITICAL)
            return None



        inter = npArray_qgsPoint(p_inter)
        # Calc distances between points
        p1i = QgsDistanceArea().measureLine(p1, inter)
        p2i = QgsDistanceArea().measureLine(p2, inter)
        p1p2 = QgsDistanceArea().measureLine(p1, p2)

        p3i = QgsDistanceArea().measureLine(p3, inter)
        p4i = QgsDistanceArea().measureLine(p4, inter)
        p3p4 = QgsDistanceArea().measureLine(p3, p4)

        geom = None  # Return geom if new


        if self.twoFeature.isChecked():

            if self.newFeature.isChecked():
                inter1, inter2 = 0, 0
                # Second segment
                # Trim: inter is on p1p2. Case 1
                if p1i <= p1p2 and p2i <= p1p2:
                    inter2 = 1
                    # We have click near p1
                    if QgsDistanceArea().measureLine(p1, self.result2.snappedVertex) <= p1i:
                        geom = QgsGeometry.fromPolyline([p1, inter])
                    else:
                        geom = QgsGeometry.fromPolyline([p2, inter])
                elif p1i >= p2i:  # Case 2
                    geom = QgsGeometry.fromPolyline([p1, inter])
                else:  # Case 3
                    geom = QgsGeometry.fromPolyline([p2, inter])

                geom2 = geom  # magic geom

                # First segment
                # Trim: inter is on p3p4. Case 1
                if p3i <= p3p4 and p4i <= p3p4:
                    inter1 = 1
                    # We have click near p3
                    if QgsDistanceArea().measureLine(p3, self.result1.snappedVertex) <= p3i:
                        geom2 = QgsGeometry.fromPolyline([p3, inter])
                    else:
                        geom2 = QgsGeometry.fromPolyline([p4, inter])
                elif p3i >= p4i:  #  Case 2
                    geom2 = QgsGeometry.fromPolyline([p3, inter])
                else:  # Case 3
                    geom2 = QgsGeometry.fromPolyline([p4, inter])

                # Cases when trim/extend are at least on a segment
                if inter1 == 0 and inter2 == 1:
                    geom = geom2
                elif inter1 == 1 and inter2 == 0:
                    geom = geom
                # Else if trim/extend can produce a result for both segments
                else:
                    geom = geom.combine(geom2)

            if self.modifyFeature.isChecked():

                # check if one or both are intersected
                inter1, inter2 = 0, 0
                if p1i <= p1p2 and p2i <= p1p2:
                    inter2 = 1
                if p3i <= p3p4 and p4i <= p3p4:
                    inter1 = 1

                # if both put flag on 0
                if inter1 == 1 and inter2 == 1:
                    inter1, inter2 = 0, 0

                # Second segment
                # Trim: inter is on p1p2. Case 1
                if p1i <= p1p2 and p2i <= p1p2 and inter2 == 0:
                    # we have click near p1
                    if QgsDistanceArea().measureLine(p1, self.result2.snappedVertex) <= p1i:
                        self.result2.layer.moveVertex(
                            inter.x(), inter.y(), self.result2.snappedAtGeometry, self.result2.afterVertexNr)
                    else:
                        self.result2.layer.moveVertex(
                            inter.x(), inter.y(), self.result2.snappedAtGeometry, self.result2.beforeVertexNr)

                elif p1i >= p2i:  # case 2
                    self.result2.layer.moveVertex(
                        inter.x(), inter.y(), self.result2.snappedAtGeometry, self.result2.afterVertexNr)
                else:  # case 3
                    self.result2.layer.moveVertex(
                        inter.x(), inter.y(), self.result2.snappedAtGeometry, self.result2.beforeVertexNr)

                # First segment
                # Trim: inter is on p3p4. Case1
                if p3i <= p3p4 and p4i <= p3p4 and inter1 == 0:
                    # We have click near p3
                    if QgsDistanceArea().measureLine(p3, self.result1.snappedVertex) <= p3i:
                        self.result1.layer.moveVertex(
                            inter.x(), inter.y(), self.result1.snappedAtGeometry, self.result1.afterVertexNr)
                    else:
                        self.result1.layer.moveVertex(
                            inter.x(), inter.y(), self.result1.snappedAtGeometry, self.result1.beforeVertexNr)

                elif p3i >= p4i:  # Case 2
                    self.result1.layer.moveVertex(
                        inter.x(), inter.y(), self.result1.snappedAtGeometry, self.result1.afterVertexNr)
                else:  # Case 3
                    self.result1.layer.moveVertex(
                        inter.x(), inter.y(), self.result1.snappedAtGeometry, self.result1.beforeVertexNr)

        else:
            if self.newFeature.isChecked():
                # Trim: inter is on p1p2. Case 1
                if p1i <= p1p2 and p2i <= p1p2:
                    # We have click near p1
                    if QgsDistanceArea().measureLine(p1, self.result2.snappedVertex) <= p1i:
                        geom = QgsGeometry.fromPolyline([p1, inter])
                    else:
                        geom = QgsGeometry.fromPolyline([p2, inter])
                elif p1i >= p2i:  # Case 2
                    geom = QgsGeometry.fromPolyline([p1, inter])
                else:  #  Case 3
                    geom = QgsGeometry.fromPolyline([p2, inter])

            if self.modifyFeature.isChecked():
                # Trim: inter is on p1p2. Case 1
                if p1i <= p1p2 and p2i <= p1p2:
                    # We have click near p1
                    if QgsDistanceArea().measureLine(p1, self.result2.snappedVertex) <= p1i:
                        self.result2.layer.moveVertex(
                            inter.x(), inter.y(), self.result2.snappedAtGeometry, self.result2.afterVertexNr)
                    else:
                        self.result2.layer.moveVertex(
                            inter.x(), inter.y(), self.result2.snappedAtGeometry, self.result2.beforeVertexNr)

                elif p1i >= p2i:  #  Case 2
                    self.result2.layer.moveVertex(
                        inter.x(), inter.y(), self.result2.snappedAtGeometry, self.result2.afterVertexNr)
                else:  # Case 3
                    self.result2.layer.moveVertex(
                        inter.x(), inter.y(), self.result2.snappedAtGeometry, self.result2.beforeVertexNr)

        return geom

    def canvasPressEvent(self, event):
        layer = self.canvas.currentLayer()

        x = event.pos().x()
        y = event.pos().y()

        flag = False    # flag if when we click we don't find a segment

        # Max two segments like LibreCad. TODO: Take all limits and all trim
        # segments like AutoCad
        if self.nbPoints == 2:
            flag = True

        # Well know routine for snap segments.
        (layerid, enabled, snapType, tolUnits, tol,
         avoidInt) = QgsProject.instance().snapSettingsForLayer(layer.id())
        startingPoint = QPoint(x, y)
        snapper = QgsMapCanvasSnapper(self.canvas)
        (retval, self.result) = snapper.snapToCurrentLayer(
            startingPoint, snapType, tol)
        if self.result <> []:
            self.point1 = self.result[0].beforeVertex
            self.point2 = self.result[0].afterVertex
            flag = True
        else:
            (retval, self.result) = snapper.snapToBackgroundLayers(
                startingPoint)
            if self.result <> []:
                self.point1 = self.result[0].beforeVertex
                self.point2 = self.result[0].afterVertex
                flag = True

        # record first segment and draw it
        if self.nbPoints == 0 and flag:
            self.result1 = self.result[0]

            # convert points to numpy array
            self.p11 = qgsPoint_NParray(self.point1)
            self.p12 = qgsPoint_NParray(self.point2)

            self.rb1 = QgsRubberBand(self.canvas, True)
            self.rb1.setColor(QColor(0, 0, 255))
            self.rb1.setWidth(3)
            self.rb1.setToGeometry(
                QgsGeometry.fromPolyline([self.point1, self.point2]), None)

        # record second segment and draw it
        if self.nbPoints == 1 and flag:
            self.result2 = self.result[0]

            # convert points to numpy array
            self.p21 = qgsPoint_NParray(self.point1)
            self.p22 = qgsPoint_NParray(self.point2)

            self.rb2 = QgsRubberBand(self.canvas, True)
            self.rb2.setColor(QColor(0, 0, 255))
            self.rb2.setWidth(3)
            self.rb2.setToGeometry(
                QgsGeometry.fromPolyline([self.point1, self.point2]), None)

        # Increment nbPoints only if flag (a segment is snapped) is True and
        # obviously if nbPoints < 2
        if self.nbPoints < 2 and flag:
            self.nbPoints += 1

        if self.nbPoints == 2:
            # Need at least one option checked
            if self.newFeature.isChecked() == False and self.modifyFeature.isChecked() == False:
                iface.messageBar().pushMessage(QCoreApplication.translate("CADDigitize", "Error", None, QApplication.UnicodeUTF8), QCoreApplication.translate(
                    "CADDigitize", "Check at least one of the options New or Modify", None, QApplication.UnicodeUTF8), level=QgsMessageBar.WARNING)
            else:
                # For create a new feature with polyon you need to add the geom
                # of the first segment
                if layer.geometryType() == 2 and self.newFeature.isChecked():
                    self.twoFeature.setCheckState(Qt.Checked)

                geom = self.trimextend()

                if geom:
                    if layer.geometryType() == 2:
                        geom.insertVertex(
                            geom.asPolyline()[-1].x(), geom.asPolyline()[-1].y(), 0)
                        geom = geom.convertToType(2, False)
                    self.emit(SIGNAL("rbFinished(PyQt_PyObject)"), geom)

            self.clear()

            return

    def activate(self):
        self.canvas.setCursor(self.cursor)
        self.optionsToolBar = iface.mainWindow().findChild(
            QToolBar, u"CADDigitize Options")
        self.newFeature = QCheckBox(QCoreApplication.translate(
            "CADDigitize", "New", None, QApplication.UnicodeUTF8))
        self.modifyFeature = QCheckBox(QCoreApplication.translate(
            "CADDigitize", "Modify", None, QApplication.UnicodeUTF8))
        self.twoFeature = QCheckBox(QCoreApplication.translate(
            "CADDigitize", "Two", None, QApplication.UnicodeUTF8))
        self.modifyFeature.setCheckState(Qt.Checked)
        self.newFeatureAction = self.optionsToolBar.addWidget(self.newFeature)
        self.modifyFeatureAction = self.optionsToolBar.addWidget(
            self.modifyFeature)
        self.optionsToolBar.addSeparator()
        self.twoFeatureAction = self.optionsToolBar.addWidget(self.twoFeature)

    def clear(self):
        self.nbPoints = 0
        self.point1, self.point2 = None, None
        self.p11, self.p12, self.p21, self.p22 = None, None, None, None
        if self.rb1:
            self.rb1.reset(True)
        if self.rb2:
            self.rb2.reset(True)
        self.rb1, self.rb2 = None, None

        self.canvas.refresh()

    def deactivate(self):
        self.optionsToolBar.clear()
        self.clear()

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True
