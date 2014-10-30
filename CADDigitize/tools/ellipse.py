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
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from calc import *

import math



class Ellipse:
    def getEllipse(center, axis_a, axis_b, angle_exist=0, segments=36):
            
        points = []
        for t in [(2*math.pi)/segments*i for i in range(segments)]:
            points.append((center.x() + axis_a*math.cos(t)*math.cos(angle_exist) - axis_b*math.sin(t)*math.sin(angle_exist), center.y() + axis_a*math.cos(t)*math.sin(angle_exist) + axis_b*math.sin(t)*math.cos(angle_exist)))
        
        polygon = [QgsPoint(i[0],i[1]) for i in points]
        geom = QgsGeometry.fromPolygon([polygon])
        
        return geom
        
    def getEllipseFromFoci(f1, f2, f3, segments=36):
        dist_f1f2 = QgsDistanceArea().measureLine(f1, f2)
        dist_tot = QgsDistanceArea().measureLine(f1, f3) + QgsDistanceArea().measureLine(f2, f3)
        angle_exist = calcAngleExistant(f1, f2)
        center_f1f2 = calc_milieuLine(f1, f2)

        axis_a = dist_tot / 2.0
        axis_b = sqrt((dist_tot/2.0)**2.0 - (dist_f1f2/2.0)**2.0)

        if axis_a < axis_b:
            axis_a,axis_b = axis_b, axis_a

        return Ellipse.getEllipse(center_f1f2, axis_a, axis_b, angle_exist, segments)
        

        
    getEllipse = staticmethod(getEllipse)
    getEllipseFromFoci = staticmethod(getEllipseFromFoci)
