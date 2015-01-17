#-*- coding:utf-8 -*-

from PyQt4.QtCore import QSettings,QCoreApplication
from PyQt4.QtGui import QApplication

from qgis.core import *
import qgis.utils

from tools.calc import *

from math import *

from tools.circle import *
from tools.rectangle import *
from tools.circulararc import *
from tools.ellipse import *
from tools.regularpolygon import *

def arc_setting(self):
    arc_method = QSettings().value("/CADDigitize/arc/method",  "pitch")
    if arc_method == "pitch":
        interValue = QSettings().value("/CADDigitize/arc/pitch", 2,type=float)
    else:
        interValue = QSettings().value("/CADDigitize/arc/angle", 1,type=int)
    arc_clock = QSettings().value("/CADDigitize/arc/direction",  "ClockWise")

    return arc_method, interValue, arc_clock

def arc_polygon(self, arc):
    iface = qgis.utils.iface

    geom = arc[0]
    center = arc[1]
    mc = iface.mapCanvas()
    layer = mc.currentLayer()
    if layer.geometryType() == 2:
        arcPolygonSettings = QSettings()

        if arcPolygonSettings.value("/CADDigitize/arc/polygon","chord") == "pie":
            geom.insertVertex(center.x(), center.y(),0)

        geom = geom.convertToType(2, False)

    return geom


def listToPoint(pList):
    if len(pList) != 2:
        return None
    else:
        return QgsPoint(pList[0], pList[1])

P = listToPoint

class ND_functions:


    @staticmethod
    def f_getCircleBy2Points(list_args):

        return Circle.getCircleBy2Points( P(list_args[0]), P(list_args[1]), QSettings().value("/CADDigitize/circle/segments",36,type=int) )

    @staticmethod
    def f_getCircleBy3Points(list_args):

        return Circle.getCircleBy3Points( P(list_args[0]), P(list_args[1]), P(list_args[2]), QSettings().value("/CADDigitize/circle/segments",36,type=int) )

    @staticmethod
    def f_getCircleByCenterRadius(list_args):

        return Circle.getCircleByCenterRadius( P(list_args[0]), list_args[1], QSettings().value("/CADDigitize/circle/segments",36,type=int) )

    @staticmethod
    def f_getCircleByCenterPoint(list_args):

        return Circle.getCircleByCenterPoint( P(list_args[0]), P(list_args[1]), QSettings().value("/CADDigitize/circle/segments",36,type=int) )


    @staticmethod
    def f_getSquareFromCenter(list_args):

        return Rectangle.getSquareFromCenter( P(list_args[0]), P(list_args[1]) )

    @staticmethod
    def f_getRectFromCenter(list_args):

        return Rectangle.getRectFromCenter( P(list_args[0]), P(list_args[1]) )

    @staticmethod
    def f_getRectByExtent(list_args):

        return Rectangle.getRectByExtent( P(list_args[0]), P(list_args[1]) )

    @staticmethod
    def f_getRectBy3Points(list_args):

        return Rectangle.getRectBy3Points( P(list_args[0]), P(list_args[1]), P(list_args[2]) )


    @staticmethod
    def f_getEllipseByCenterAnd2Points(list_args):
        pc, p1 = P(list_args[0]), P(list_args[1])
        angle_exist = calcAngleExistant(pc, p1)
        axis_a = QgsDistanceArea().measureLine( pc, p1)
        length = QgsDistanceArea().measureLine(pc, P(list_args[2]) )

        p2 = [ pc[0] + length * cos(radians(90) + angle_exist), pc[1] + length * sin(radians(90) + angle_exist)]
        axis_b = QgsDistanceArea().measureLine(pc, p2)

        return Ellipse.getEllipse(pc, axis_a, axis_b, angle_exist, QSettings().value("/CADDigitize/ellipse/segments",36,type=int) )


    @staticmethod
    def f_getEllipseFromCenter(list_args):
        pc = P(list_args[0])
        p1 = P(list_args[1])
        xOffset = abs( p1[0] - pc[0])
        yOffset = abs( p1[1] - pc[1])

        return Ellipse.getEllipse(pc, xOffset, yOffset, QSettings().value("/CADDigitize/ellipse/segments",36,type=int))

    @staticmethod
    def f_getEllipseByExtent(list_args):
        p1 = P(list_args[0])
        p2 = P(list_args[1])
        xc = p1[0] + ((p2[0] - p1[0]) / 2)
        yc = p1[1] + ((p2[1] - p1[1]) / 2)
        xOffset = (abs( p2[0] - p1[0]))/2
        yOffset = (abs( p2[1] - p1[1]))/2

        return Ellipse.getEllipse(QgsPoint(xc, yc), xOffset, yOffset, QSettings().value("/CADDigitize/ellipse/segments",36,type=int))

    @staticmethod
    def f_getEllipseFromFoci(list_args):

        return Ellipse.getEllipseFromFoci( P(list_args[0]), P(list_args[1]), P(list_args[2]), QSettings().value("/CADDigitize/ellipse/segments",36,type=int) )


    @staticmethod
    def f_getArcBy3Points(list_args):
        arc_method, interValue, arc_clock = arc_setting()
        geom = CircularArc.getArcBy3Points(P(list_args[0]), P(list_args[1]), P(list_args[2]),  arc_method,  interValue)
        print geom.exportToWKT()
        g = self.arc_polygon(geom)
        print g.exportToWKT()
        return g

    @staticmethod
    def f_getArcByCenter2Points(list_args):
        arc_method, interValue, arc_clock = arc_setting()
        geom = CircularArcgetArcByCenter2Points(P(list_args[0]), P(list_args[1]), P(list_args[2]), arc_method, interValue, arc_clock)
        return self.arc_polygon(geom)

    @staticmethod
    def f_getArcByCenterPointAngle(list_args):
        arc_method, interValue, arc_clock = arc_setting()
        geom = CircularArc.getArcByCenterPointAngle(P(list_args[0]), P(list_args[1]),  list_args[2], arc_method, interValue, arc_clock)
        return self.arc_polygon(geom)


    @staticmethod
    def f_getRPolygon2Corners(list_args):
        return RegularPolygon.getRPolygon2Corners( P(list_args[0]), P(list_args[1]), QSettings().value("/CADDigitize/rpolygon/nbedges", 5,type=int))

    @staticmethod
    def f_getRPolygonCenterCorner(list_args):
        return RegularPolygon.getRPolygonCenterCorner( P(list_args[0]), P(list_args[1]), QSettings().value("/CADDigitize/rpolygon/nbedges", 5,type=int) )


CADDigitize_functions = [
        # Circle
        [QCoreApplication.translate( "CADDigitize","Circle by 2 points", None, QApplication.UnicodeUTF8)                     ,   ND_functions.f_getCircleBy2Points],
        [QCoreApplication.translate( "CADDigitize","Circle by 3 points", None, QApplication.UnicodeUTF8)                     ,   ND_functions.f_getCircleBy3Points],
        [QCoreApplication.translate( "CADDigitize","Circle by center and a point", None, QApplication.UnicodeUTF8)           ,   ND_functions.f_getCircleByCenterPoint],
        [QCoreApplication.translate( "CADDigitize","Circle by center and radius", None, QApplication.UnicodeUTF8)            ,   ND_functions.f_getCircleByCenterRadius],
        # Rectangle
        [QCoreApplication.translate( "CADDigitize","Rectangle by 3 points", None, QApplication.UnicodeUTF8)                  ,   ND_functions.f_getRectBy3Points],
        [QCoreApplication.translate( "CADDigitize","Rectangle by extent", None, QApplication.UnicodeUTF8)                    ,   ND_functions.f_getRectByExtent],
        [QCoreApplication.translate( "CADDigitize","Rectangle from center", None, QApplication.UnicodeUTF8)                  ,   ND_functions.f_getRectFromCenter],
        [QCoreApplication.translate( "CADDigitize","Square from center", None, QApplication.UnicodeUTF8)                     ,   ND_functions.f_getSquareFromCenter],
        # Ellipse
        [QCoreApplication.translate( "CADDigitize","Ellipse by center and 2 points", None, QApplication.UnicodeUTF8)         ,   ND_functions.f_getEllipseByCenterAnd2Points],
        [QCoreApplication.translate( "CADDigitize","Ellipse by extent", None, QApplication.UnicodeUTF8)                      ,   ND_functions.f_getEllipseByExtent],
        [QCoreApplication.translate( "CADDigitize","Ellipse by foci and a point", None, QApplication.UnicodeUTF8)            ,   ND_functions.f_getEllipseFromFoci],
        [QCoreApplication.translate( "CADDigitize","Ellipse from center", None, QApplication.UnicodeUTF8)                    ,   ND_functions.f_getEllipseFromCenter],
        # Arc
        [QCoreApplication.translate( "CADDigitize","Arc by 3 points", None, QApplication.UnicodeUTF8)                        ,   ND_functions.f_getArcBy3Points],
        [QCoreApplication.translate( "CADDigitize","Arc by center and 2 points", None, QApplication.UnicodeUTF8)             ,   ND_functions.f_getArcByCenter2Points],
        [QCoreApplication.translate( "CADDigitize","Arc by center, point and angle", None, QApplication.UnicodeUTF8)         ,   ND_functions.f_getArcByCenterPointAngle],
        # Regular polygon
        [QCoreApplication.translate( "CADDigitize","Regular polygon by 2 corners", None, QApplication.UnicodeUTF8)           ,   ND_functions.f_getRPolygon2Corners],
        [QCoreApplication.translate( "CADDigitize","Regular polygon by center and point", None, QApplication.UnicodeUTF8)    ,   ND_functions.f_getRPolygonCenterCorner]
        ]


CADDigitize_functions_points = [
        #[Point, Point, Point, "Option"]
        # Circle
        [True, True, False, False],
        [True, True, True, False],
        [True, True, False, False],
        [True, False, False, "double"],
        # Rectangle
        [True, True, True, False],
        [True, True, False, False],
        [True, True, False, False],
        [True, True, False, False],
        # Ellipse
        [True, True, True, False],
        [True, True, False, False],
        [True, True, True, False],
        [True, True, False, False],
        # Arc
        [True, True, True, False],
        [True, True, True, False],
        [True, True, False, "angle"],
        # Regular polygon
        [True, True, False, False],
        [True, True, False, False]
        ]
