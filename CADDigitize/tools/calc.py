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


def GetAngleOfLineBetweenTwoPoints(p1, p2, angle_unit="degrees"):
    xDiff = p2.x() - p1.x()
    yDiff = p2.y() - p1.y()

    if angle_unit == "radians":
        return atan2(yDiff, xDiff)
    else:
        return degrees(atan2(yDiff, xDiff))

def calcPente(p1, p2):
    """
    Return the slope of the line represents by two points : p1 and p2

    :param p1: The first point
    :param p2: The second point
    :type p1: QgsPoint
    :type p2: QgsPoint
    :return: Return the slope (degre)
    :rtype: float
    """

    num = p1.x() - p2.x()
    denum = p1.y() - p2.y()

    # Avoid division by zero
    if num == 0:
        # Return a negative value if denum > 0
        if denum > 0:
            return -90
        else:
        # else return a positive value
            return 90
    # Same as above with denum
    elif denum == 0:
        if num > 0:
            return -90
        else:
            return 90
    else:
        return denum/num

def calcAngleExistant(p1, p2):
    """
    Return the angle of the line represents by two points : p1 and p2

    :param p1: The first point
    :param p2: The second point
    :type p1: QgsPoint
    :type p2: QgsPoint
    :return: Return the angle (degre)
    :rtype: float
    """

    a = calcPente(p1, p2) # The slope of the segment p1-p2
    length_p1p2 = QgsDistanceArea().measureLine(p1, p2) # Hypothenuse
    length_adjacent = fabs(p2.y() - p1.y()) # Adjacent
    if length_p1p2 == 0: # Normally you can't have a length of 0 but avoid division by zero
        angle_CAB = 0
    else:
        angle_CAB = acos(length_adjacent/length_p1p2) #

    # Correction of angle_CAB
    if a<0:
        angle_CAB = angle_CAB - pi/2
    elif a>0:
        angle_CAB = pi/2 - angle_CAB

    return angle_CAB


# Tool class
# Test if point pCherche is on left/on/right of the line [p0p1]
# 1 left
# 0 collinear
# -1 right
def calc_isCollinear(p0, p1, pCherche):
    sens =  (   ( pCherche.x() - p0.x() ) * (p1.y() - p0.y() ) - \
                ( pCherche.y() - p0.y() ) * (p1.x() - p0.x() ) )

    if sens > 0:
        return 1
    elif sens < 0:
        return -1
    else:
        return 0

def calc_milieuLine(p1, p2):
    return QgsPoint((p1.x()+p2.x())/2.0, (p1.y()+p2.y())/2.0)


#https://stackoverflow.com/questions/3252194/numpy-and-line-intersections
#Stolen directly from http://www.cs.mun.ca/~rod/2500/notes/numpy-arrays/numpy-arrays.html
#
# line segment intersection using vectors
# see Computer Graphics by F.S. Hill
#
from numpy import *
def perp( a ) :
    b = empty_like(a)
    b[0] = -a[1]
    b[1] = a[0]
    return b

# line segment a given by endpoints a1, a2
# line segment b given by endpoints b1, b2
# return
def seg_intersect(a1,a2, b1,b2) :
    da = a2-a1
    db = b2-b1
    dp = a1-b1
    dap = perp(da)
    denom = dot( dap, db)
    num = dot( dap, dp )
    # Modification: test if a1b1 // a2b2
    if denom != 0.0:
        return (num / denom)*db + b1
    else:
        return None

def qgsPolyline_NParray(line):
    return array( [line.asPolyline()[0][0], line.asPolyline()[0][1]] ), array( [line.asPolyline()[1][0], line.asPolyline()[1][1]] )

def qgsPoint_NParray(point):
    return array( [point[0], point[1]] )

def npArray_qgsPoint(array):
    return QgsPoint( array[0], array[1] )


