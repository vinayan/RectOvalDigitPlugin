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

class Circle:
    def getCircleBy2Points(p1, p2, segments=36):
        center = QgsPoint( (p1.x() + p2.x()) / 2.0, (p1.y() + p2.y()) / 2.0 )
        rayon = QgsDistanceArea().measureLine(p1, center)
    
    
        return QgsGeometry.fromPoint(center).buffer(rayon, segments)

    def getCircleBy3Points(p1, p2, p3, segments=36):
    # Paul Bourke's algorithm
        m_Center = QgsPoint()
        m_dRadius = -1
        yDelta_a = p2.y() - p1.y()
        xDelta_a = p2.x() - p1.x()
        yDelta_b = p3.y() - p2.y()
        xDelta_b = p3.x() - p2.x()
        try:
            aSlope=yDelta_a/xDelta_a
        except ZeroDivisionError:
            return None
        try:
            bSlope=yDelta_b/xDelta_b
        except ZeroDivisionError:
            return None
    
        if (fabs(xDelta_a) <= 0.000000001 and fabs(yDelta_b) <= 0.000000001):
            m_Center.setX(0.5*(p2.x() + p3.x()))
            m_Center.setY(0.5*(p1.y() + p2.y()))
            m_dRadius = QgsDistanceArea().measureLine(m_Center,p1)
    
            return QgsGeometry.fromPoint(m_Center).buffer(m_dRadius, segments)
    
	    # IsPerpendicular() assure that xDelta(s) are not zero
    
	    if fabs(aSlope-bSlope) <= 0.000000001:	# checking whether the given points are colinear.
	    	return None
    
    
	    # calc center
        m_Center.setX( (aSlope*bSlope*(p1.y() - p3.y()) + bSlope*(p1.x() + p2.x()) - aSlope*(p2.x()+p3.x()) )/(2.0* (bSlope-aSlope) ) )
        m_Center.setY( -1.0*(m_Center.x() - (p1.x()+p2.x())/2.0)/aSlope +  (p1.y()+p2.y())/2.0 )
    
        m_dRadius = QgsDistanceArea().measureLine(m_Center,p1)
    
        return QgsGeometry.fromPoint(m_Center).buffer(m_dRadius, segments)

        # longueur A = p1p2, B = p2p3, C = p3p1
        #    A, B, C =QgsDistanceArea().measureLine(p1, p2),QgsDistanceArea().measureLine(p2, p3),QgsDistanceArea().measureLine(p3, p1)
        #    rayon = (A * B * C) / sqrt( (A + B + C) * (-A + B + C) * (A - B + C) * (A + B - C) )
        #    D = 2 * (p1.x() * (p2.y()-p3.y()) + p2.x() * (p3.y()-p1.y())+p3.x()*(p1.y()-p2.y()))
        #    center = QgsPoint()
        #    center.setX( ((pow(p1.x(), 2.0) + pow(p1.y(), 2.0))*(p2.y() - p3.y()) + (pow(p2.x(), 2.0) + pow(p2.y(), 2.0))*(p3.y()-p1.y()) + (pow(p3.x(), 2.0) + pow(p3.y(), 2.0))*(p1.y()-p2.y()))/D )
        #    center.setY(((pow(p1.x(), 2.0) + pow(p1.y(), 2.0))*(p3.x() - p2.x()) + (pow(p2.x(), 2.0) + pow(p2.y(), 2.0))*(p1.x()-p3.x()) + (pow(p3.x(), 2.0) + pow(p3.y(), 2.0))*(p2.x()-p1.x()))/D )
        #    return (center, rayon)
        
    def getCircleByCenterRadius(pc, radius, segments=36):
        return QgsGeometry.fromPoint(pc).buffer(radius, segments)

    def getCircleByCenterPoint(pc, p1, segments=36):
        return QgsGeometry.fromPoint(pc).buffer(QgsDistanceArea().measureLine(pc, p1), segments)


    getCircleBy2Points = staticmethod(getCircleBy2Points)
    getCircleBy3Points = staticmethod(getCircleBy3Points)
    getCircleByCenterRadius = staticmethod(getCircleByCenterRadius)
    getCircleByCenterPoint = staticmethod(getCircleByCenterPoint)
    
