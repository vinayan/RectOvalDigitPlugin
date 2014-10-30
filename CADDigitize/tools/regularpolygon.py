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
import math
from calc import *


class RegularPolygon:
    def getRPolygon2Corners(p1, p2, nbEdges):
        length = QgsDistanceArea().measureLine(p1, p2)
        angle_start = math.atan2( p2.y() - p1.y(), p2.x() - p1.x() )

        angle = angle_start
        
        c1 = p2
        n = 1
        points = []
        while(n <= nbEdges):
        
            angle = angle_start + (2*math.pi)/nbEdges*n;
            if angle > math.pi:
                angle -= 2*math.pi
            
                
            c2 = QgsPoint(c1.x() + length * math.cos(angle), c1.y() + length * math.sin(angle))
            c1 = c2
            
            points.append(c2)
            
            n += 1
            
        geom = QgsGeometry.fromPolygon([points])
        return geom     
          
    def getRPolygonCenterCorner(p1, p2, nbEdges):
        n = 1
        center = p1
        corner = p2
        
        r = QgsDistanceArea().measureLine(center, corner)
        
        points = []
        angle_add = 2*math.pi / nbEdges
        
        angle_start = math.atan2( corner.y() - center.y(), corner.x() - center.x() )
        
        angle = angle_start
        
        while(n <= nbEdges):
        
            angle += angle_add
            if angle_add > 0.0 and angle > math.pi:
                angle -= 2*math.pi
            
                
            c2 = QgsPoint(center.x() + r * math.cos(angle), center.y() + r * math.sin(angle))
            
            points.append(c2)
            
            n += 1
            
        geom = QgsGeometry.fromPolygon([points])
        return geom     
    
    
    getRPolygon2Corners = staticmethod(getRPolygon2Corners)
    getRPolygonCenterCorner = staticmethod(getRPolygonCenterCorner)

