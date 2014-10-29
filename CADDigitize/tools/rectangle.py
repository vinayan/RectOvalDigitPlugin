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
from qgis.core import *
from math import *
from calc import *


class Rectangle:
    def getSquareFromCenter(p1, p2):
        distance= sqrt(p2.sqrDist( p1))
        offset = distance/sqrt(2)
        pt1 = (-offset, -offset)
        pt2 = (-offset, offset)
        pt3 = (offset, offset)
        pt4 = (offset, -offset)
        points = [pt1, pt2, pt3, pt4]
        polygon = [QgsPoint(p1.x() + i[0], p1.y() + i[1]) for i in points]
        geom = QgsGeometry.fromPolygon([polygon])
        
        return geom

    def getRectFromCenter(p1, p2):
        xOffset = abs( p2.x() - p1.x())
        yOffset = abs( p2.y() - p1.y())
        pt1 = QgsPoint(-xOffset, -yOffset)
        pt2 = QgsPoint(-xOffset, yOffset)
        pt3 = QgsPoint(xOffset, yOffset)
        pt4 = QgsPoint(xOffset, -yOffset)
        points = [pt1, pt2, pt3, pt4]
        polygon = [QgsPoint(p1.x() + i[0], p1.y() + i[1]) for i in points]
        geom = QgsGeometry.fromPolygon([polygon])
        
        return geom
        
    def getRectByExtent(p1, p2):
    
        pt1 = (p1.x(), p1.y())
        pt2 = (p1.x(), p2.y())
        pt3 = (p2.x(), p2.y())
        pt4 = (p2.x(), p1.y())
        points = [pt1, pt2, pt3, pt4]
        polygon = [QgsPoint(i[0],i[1]) for i in points]
        geom = QgsGeometry.fromPolygon([polygon])
        
        return geom
        
    def getRectBy3Points(p1, p2, p3):
        angle_exist = calcAngleExistant(p1, p2)
    
        side = calc_isCollinear(p1, p2, p3) # check if x_p2 > x_p1 and inverse side
        if p1.x() < p2.x():
            side *= -1
        length = QgsDistanceArea().measureLine(p2, p3) * side
        p3 = QgsPoint(p2.x() + length * cos(radians(90) + angle_exist), p2.y() + length * sin(radians(90) + angle_exist))
        p4 = QgsPoint(p1.x() + length * cos(radians(90) + angle_exist), p1.y() + length * sin(radians(90) + angle_exist))
        geom = QgsGeometry.fromPolygon([[p1, p2, p3, p4]])
        
        return geom


    getSquareFromCenter = staticmethod(getSquareFromCenter)
    getRectFromCenter = staticmethod(getRectFromCenter)
    getRectByExtent = staticmethod(getRectByExtent)
    getRectBy3Points = staticmethod(getRectBy3Points)
