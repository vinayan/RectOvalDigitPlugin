#   Menu avec les cercles, rectangles, ellipses, arc, etc.
#
#   Cercles :
#       - Cercle avec centre, rayon
#       - Cercle avec centre et point sur le cercle
#       - Cercle avec deux points sur le cercle
#       - Cercle avec trois points sur le cercle
#       - Cercle inscrit
#       - Cercle circonscrit
#
#   Rectangles :
#       - Rectangle par 3 points
#       - (voir autre outil)
#
#   Ellipses :
#       - Ellipses avec centre et deux points
#       - (voir autre outil + librecad)
#
#   Arc :
#       - Centre, point, angle
#       - Arc avec trois points
#-*- coding:utf-8 -*-

def distance(p1, p2):
    return sqrt( pow(p2.x() - p1.x(), 2.0) + pow(p2.y() - p1.y(), 2.0) )

def circleByCenterRayon(p1, rayon):
    return (p1, rayon)

def circleByCenterPoint(pc, p1):
    return (pc, distance(pc, p1))

def circleBy2Points(p1, p2):
    center = QgsPoint( (p1.x() + p2.x()) / 2.0, (p1.y() + p2.y()) / 2.0 )
    rayon = distance(p1, center)
    return (center, rayon)

def circleBy3Points(p1, p2, p3):
    # longueur A = p1p2, B = p2p3, C = p3p1
    A, B, C = distance(p1, p2), distance(p2, p3), distance(p3, p1)
    rayon = (A * B * C) / sqrt( (A + B + C) * (-A + B + C) * (A - B + C) * (A + B - C) )
    D = 2 * (p1.x() * (p2.y()-p3.y()) + p2.x() * (p3.y()-p1.y())+p3.x()*(p1.y()-p2.y()))
    center = QgsPoint()
    center.setX( ((pow(p1.x(), 2.0) + pow(p1.y(), 2.0))*(p2.y() - p3.y()) + (pow(p2.x(), 2.0) + pow(p2.y(), 2.0))*(p3.y()-p1.y()) + (pow(p3.x(), 2.0) + pow(p3.y(), 2.0))*(p1.y()-p2.y()))/D )
    center.setY(((pow(p1.x(), 2.0) + pow(p1.y(), 2.0))*(p3.x() - p2.x()) + (pow(p2.x(), 2.0) + pow(p2.y(), 2.0))*(p1.x()-p3.x()) + (pow(p3.x(), 2.0) + pow(p3.y(), 2.0))*(p2.x()-p1.x()))/D )
    return (center, rayon)



if __name__ == "__main__":
    from PyQgis.gui import *
    from PyQgis.core import *
    p1 = QgsPoint(1981089, 5190558.61)
    p2 = QgsPoint(1981135.44, 5190575.26)
    p3 = QgsPoint(1981127.65, 5190512.55)


# TEST
class cercle:
    centre = 0
    rayon = 0

p1 = QgsPoint(1981089, 5190558.61)
p2 = QgsPoint(1981135.44, 5190575.26)
p3 = QgsPoint(1981127.65, 5190512.55)
cercle.centre, cercle.rayon = circleBy3Points(p1,p2,p3)

cLayer = qgis.utils.iface.mapCanvas().currentLayer()
pr = cLayer.dataProvider()

fet = QgsFeature()
fet.setGeometry(QgsGeometry.fromPoint(cercle.centre).buffer(cercle.rayon, 360))

pr.addFeatures([fet])

cLayer.commitChanges()
cLayer.updateExtents()
