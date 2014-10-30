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

import math


    
#CirculArc from CadTools
#
#CadTools provides some tools to perform CAD like functions in QGIS.
#There is some code adopted from the Numerical Vertex Edit plugin (Cédric Möri), fTools (Carson Farmer) and the Python console. Thank you!
#And thanks to Giuseppe Sucameli for solving the lost icons issue.
#Ported to QGIS 2.0 API version by Angelos Tzotsos (gcpp.kalxas@gmail.com) and Matthias Uden (matthias.uden@gmail.com)
#LICENSING INFORMATION:
#CadTools is copyright (C) 2009-2011 Stefan Ziegler
#stefan.ziegler@bd.so.ch
#Licensed under the terms of GNU GPL 2
#This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
#This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#
# Modified by Loïc Bartoletti (l.bartoletti@free.fr) 2014


class CircularArc:
    
    def getArcBy3Points(ptStart,  ptArc, ptEnd,  method="angle",  interValue=1):
        
        coords = []
        coords.append(ptStart)
        
        center = CircularArc.getArcCenter(ptStart,  ptArc, ptEnd)
        
        if center == None:
            coords.append(ptEnd)
            g = QgsGeometry.fromPolyline(coords)
            return g
        
        cx = center.x()
        cy = center.y()
        
        px = ptArc.x() 
        py = ptArc.y()
        r = ( ( cx-px ) * ( cx-px ) + ( cy-py ) * ( cy-py ) ) ** 0.5

        ## If the method is "pitch" (=Pfeilhöhe) then
        ## we need to calculate the corresponding
        ## angle.
        if method == "pitch":
            myAlpha = 2.0 * math.acos( 1.0 - ( interValue / 1000.0 ) / r )
            arcIncr = myAlpha
#            print "myAlpha: " + str(myAlpha)
        else:
            arcIncr = interValue * math.pi / 180
#            print "arcIncr:  " + str(arcIncr)

        a1 = math.atan2( ptStart.y() - center.y(), ptStart.x() - center.x() )
        a2 = math.atan2( ptArc.y() - center.y(), ptArc.x() - center.x() )
        a3 = math.atan2( ptEnd.y() - center.y(), ptEnd.x() - center.x() )

        # Clockwise
        if a1 > a2 and a2 > a3:
            sweep = a3 - a1;

        # Counter-clockwise
        elif a1 < a2 and a2 < a3: 
            sweep = a3 - a1

        # Clockwise, wrap
        elif (a1 < a2 and a1 > a3) or (a2 < a3 and a1 > a3):
            sweep = a3 - a1 + 2*math.pi

        # Counter-clockwise, wrap
        elif (a1 > a2 and a1 < a3) or (a2 > a3 and a1 < a3):
            sweep = a3 - a1 - 2*math.pi

        else:
            sweep = 0.0;

        ptcount = int(math.ceil( math.fabs ( sweep / arcIncr ) ))

        if sweep < 0: 
            arcIncr *= -1.0;

        angle = a1;

        for i in range(0,  ptcount-1):
            angle += arcIncr;

            if arcIncr > 0.0 and angle > math.pi:
                angle -= 2*math.pi
                
            if arcIncr < 0.0 and angle < -1*math.pi:
                angle -= 2*math.pi

            x = cx + r * math.cos(angle);
            y = cy + r * math.sin(angle);

            point = QgsPoint(x,  y)
            coords.append(point)
#            print str(point.toString())
            
            if angle < a2 and (angle +arcIncr) > a2:
                coords.append(ptArc)

            if angle > a2 and (angle + arcIncr) < a2:
                coords.append(ptArc)

        coords.append(ptEnd)
        g = QgsGeometry.fromPolyline(coords)
        return g


    def getArcCenter(ptStart,  ptArc,  ptEnd):
        
#        print str(ptStart.toString)
#        print str(ptArc.toString())
#        print str(ptEnd.toString())
        
        bx = ptStart.x()
        by = ptStart.y()
        cx = ptArc.x()
        cy = ptArc.y()
        dx = ptEnd.x()
        dy = ptEnd.y()
        
        temp = cx * cx + cy * cy
        bc = (bx * bx + by * by - temp) / 2.0
        cd = (temp - dx * dx - dy * dy) / 2.0
        det = (bx - cx) * (cy - dy) - (cx - dx) * (by - cy)

        try:
            det = 1 / det
            x = (bc * (cy - dy) - cd * (by - cy)) * det
            y = ((bx - cx) * cd - (cx - dx) * bc) * det

            return QgsPoint(x, y);             
            
        except ZeroDivisionError:
            return None
            
    def getArcByCenter2Points(ptCenter, ptStart, ptEnd, method="angle", interValue=1, clockwise="ClockWise"):

        coords = []
        coords.append(ptStart)
        
        center = ptCenter
        
        cx = center.x()
        cy = center.y()
        r =QgsDistanceArea().measureLine(ptStart, ptCenter)
        

        ## If the method is "pitch" (=Pfeilhöhe) then
        ## we need to calculate the corresponding
        ## angle.
        if method == "pitch":
            myAlpha = 2.0 * math.acos( 1.0 - ( interValue / 1000.0 ) / r )
            arcIncr = myAlpha
#            print "myAlpha: " + str(myAlpha)
        else:
            arcIncr = interValue * math.pi / 180
#            print "arcIncr:  " + str(arcIncr)

        a1 = math.atan2( ptStart.y() - center.y(), ptStart.x() - center.x() )
        a2 = math.atan2( ptEnd.y() - center.y(), ptEnd.x() - center.x() )

        ptcount = 0
        if clockwise == "ClockWise":
            if a2 < a1:
                sweep = a1 - a2
                arcIncr *= -1.0
            else:
                sweep = 2*math.pi - a2 +a1
                arcIncr *= -1.0


            ptcount = int(math.ceil( math.fabs ( sweep / arcIncr  )))
        
        
        if clockwise == "CounterClockWise":
            angle = a2 - a1
            if angle < 0:
                angle += 2*math.pi
            ptcount = int(math.ceil( math.fabs ( angle / arcIncr  )))


         
        angle = a1

        for i in range(0,  ptcount-1):
            angle += arcIncr

            if arcIncr > 0.0 and angle > math.pi:
                angle -= 2*math.pi
                
            if arcIncr < 0.0 and angle < -1*math.pi:
                angle -= 2*math.pi

                
            x = cx + r * math.cos(angle);
            y = cy + r * math.sin(angle);

            point = QgsPoint(x,  y)
            coords.append(point)
#            print str(point.toString())

        x = cx + r * math.cos(a2);
        y = cy + r * math.sin(a2);

        point = QgsPoint(x,  y)
        coords.append(point)
        
        g = QgsGeometry.fromPolyline(coords)
        return g
    

    def getArcByCenterPointAngle(ptCenter, ptStart, inAngle, method="angle", interValue=1, clockwise="ClockWise"):

        coords = []
        coords.append(ptStart)
        
        center = ptCenter
        
        cx = center.x()
        cy = center.y()
        r = QgsDistanceArea().measureLine(ptStart, ptCenter)
        
        ## If the method is "pitch" (=Pfeilhöhe) then
        ## we need to calculate the corresponding
        ## angle.
        if method == "pitch":
            myAlpha = 2.0 * math.acos( 1.0 - ( interValue / 1000.0 ) / r )
            arcIncr = myAlpha
#            print "myAlpha: " + str(myAlpha)
        else:
            arcIncr = interValue * math.pi / 180
#            print "arcIncr:  " + str(arcIncr)

        a1 = math.atan2( ptStart.y() - center.y(), ptStart.x() - center.x() )

        ptcount = int(math.ceil( math.fabs ( (a1-inAngle) / arcIncr  )))

        if clockwise == "ClockWise":
            if inAngle < a1:
                sweep = a1 - inAngle
                arcIncr *= -1.0
            else:
                sweep = 2*math.pi - inAngle +a1
                arcIncr *= -1.0


            ptcount = int(math.ceil( math.fabs ( sweep / arcIncr  )))
         
        angle = a1

        for i in range(0,  ptcount-1):
            angle += arcIncr
    
            if arcIncr > 0.0 and angle > math.pi:
                angle -= 2*math.pi
                    
            if arcIncr < 0.0 and angle < -1*math.pi:
                angle -= 2*math.pi

                                  
            x = cx + r * math.cos(angle);
            y = cy + r * math.sin(angle);

            point = QgsPoint(x,  y)
            coords.append(point)
#            print str(point.toString())

        x = cx + r * math.cos(inAngle);
        y = cy + r * math.sin(inAngle);

        point = QgsPoint(x,  y)
        coords.append(point)
        
        g = QgsGeometry.fromPolyline(coords)
        return g
    

        
    getArcBy3Points = staticmethod(getArcBy3Points)
    getArcCenter = staticmethod(getArcCenter)
    getArcByCenter2Points = staticmethod(getArcByCenter2Points)
    getArcByCenterPointAngle = staticmethod(getArcByCenterPointAngle)
