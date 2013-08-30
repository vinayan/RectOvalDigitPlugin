# -*- coding: utf-8 -*-

# List comprehensions in canvasMoveEvent functions are 
# adapted from Benjamin Bohard`s part of rectovaldiams plugin.

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import math

# Tool class
class OvalFromCenterTool(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self,canvas)
        self.canvas=canvas
        self.rb = None
        self.xc = None
        self.yc = None
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
    
    def canvasPressEvent(self,event):
		layer = self.canvas.currentLayer()
		color = QColor(255,0,0)
		self.rb = QgsRubberBand(self.canvas, True)
		self.rb.setColor(color)
		self.rb.setWidth(1)
		x = event.pos().x()
		y = event.pos().y()
		if self.mCtrl:
			startingPoint = QPoint(x,y)
			snapper = QgsMapCanvasSnapper(self.canvas)
			(retval,result) = snapper.snapToCurrentLayer (startingPoint, QgsSnapper.SnapToVertex)
			if result <> []:
				point = result[0].snappedVertex
			else:
				(retval,result) = snapper.snapToBackgroundLayers(startingPoint)
				if result <> []:
					point = result[0].snappedVertex
				else:
					point = self.toLayerCoordinates(layer,event.pos())
		else:
			point = self.toLayerCoordinates(layer,event.pos())
		pointMap = self.toMapCoordinates(layer, point)
		self.xc = pointMap.x()
		self.yc = pointMap.y()
		if self.rb:return
		    
    def canvasMoveEvent(self,event):
        settings = QSettings()
        if not self.rb:return
        currpoint = self.toMapCoordinates(event.pos())
        currx = currpoint.x()
        curry = currpoint.y()
        xOffset = abs( currx - self.xc)
        yOffset = abs( curry - self.yc)
        self.rb.reset(True)
        segments = settings.value("/RectOvalDigit/segments",36,type=int)
        points = []
        for t in [(2*math.pi)/segments*i for i in range(segments)]:
            points.append((xOffset*math.cos(t), yOffset*math.sin(t)))
        polygon = [QgsPoint(i[0]+self.xc,i[1]+self.yc) for i in points]
        #delete [self.rb.addPoint( point ) for point in polygon]
	self.rb.setToGeometry(QgsGeometry.fromPolygon([polygon]), None)
        
    def canvasReleaseEvent(self,event):
        if not self.rb:return		
        if self.rb.numberOfVertices() > 2:
            geom = self.rb.asGeometry()
            self.emit(SIGNAL("rbFinished(PyQt_PyObject)"), geom)
            
        self.rb.reset(True)
        self.rb=None
        
        self.canvas.refresh()

    def showSettingsWarning(self):
        pass
    
    def activate(self):
        self.canvas.setCursor(self.cursor)
        
    def deactivate(self):
        pass

    def isZoomTool(self):
        return False
  
    def isTransient(self):
        return False
    
    def isEditTool(self):
        return True

# Tool class
class OvalByExtentTool(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self,canvas)
        self.canvas=canvas
        self.rb = None
        self.x0 = None
        self.y0 = None
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
                                  
 


    def canvasPressEvent(self,event):
		layer = self.canvas.currentLayer()
		color = QColor(255,0,0)
		self.rb = QgsRubberBand(self.canvas, True)
		self.rb.setColor(color)
		self.rb.setWidth(1)
		point = self.toLayerCoordinates(layer,event.pos())
		pointMap = self.toMapCoordinates(layer, point)
		self.x0 = pointMap.x()
		self.y0 = pointMap.y()		
		if self.rb:return

		    
    def canvasMoveEvent(self,event):
        settings = QSettings()
        if not self.rb:return
        currpoint = self.toMapCoordinates(event.pos())
        currx = currpoint.x()
        curry = currpoint.y()
        xc = self.x0 + ((currx - self.x0) / 2)
        yc = self.y0 + ((curry - self.y0) / 2) 
        xOffset = (abs( currx - self.x0))/2
        yOffset = (abs( curry - self.y0))/2
        self.rb.reset(True)
        segments = settings.value("/RectOvalDigit/segments",36,type=int)
        points = []
        for t in [(2*math.pi)/segments*i for i in range(segments)]:
            points.append((xOffset*math.cos(t), yOffset*math.sin(t)))
        polygon = [QgsPoint(i[0]+xc,i[1]+yc) for i in points]
        #delete [self.rb.addPoint( point ) for point in polygon]
	self.rb.setToGeometry(QgsGeometry.fromPolygon([polygon]), None)
	
        
    def canvasReleaseEvent(self,event):
        if not self.rb:return		
        if self.rb.numberOfVertices() > 2:
            geom = self.rb.asGeometry()
            self.emit(SIGNAL("rbFinished(PyQt_PyObject)"), geom)
            
        self.rb.reset(True)
        self.rb=None
        
        self.canvas.refresh()

    def showSettingsWarning(self):
        pass
    
    def activate(self):
        self.canvas.setCursor(self.cursor)
        
    def deactivate(self):
        pass

    def isZoomTool(self):
        return False
  
    def isTransient(self):
        return False
    
    def isEditTool(self):
        return True

# Tool class
class CircleFromCenterTool(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self,canvas)
        self.canvas=canvas
        self.rb = None
        self.xc = None
        self.yc = None
        self.mCtrl = None
        #our own fancy cursor
        self.cursor = QCursor(QPixmap(["16 16 3 1",
                                       "      c None",
                                       ".     c #FF0000",
                                       "+     c #800080",
                                       "                ",
                                       "       +.+      ",
                                       "      ++.++     ",
                                       "     +.....+    ",
                                       "    +.  .  .+   ",
                                       "   +.   .   .+  ",
                                       "  +.    .    .+ ",
                                       " ++.    .    .++",
                                       " ... ...+... ...",
                                       " ++.    .    .++",
                                       "  +.    .    .+ ",
                                       "   +.   .   .+  ",
                                       "   ++.  .  .+   ",
                                       "    ++.....+    ",
                                       "      ++.++     ",
                                       "       +.+      "]))
                                  
 
    def keyPressEvent(self,  event):
        if event.key() == Qt.Key_Control:
            self.mCtrl = True


    def keyReleaseEvent(self,  event):
        if event.key() == Qt.Key_Control:
            self.mCtrl = False
    
    def canvasPressEvent(self,event):
		layer = self.canvas.currentLayer()
		color = QColor(255,0,0)
		self.rb = QgsRubberBand(self.canvas, True)
		self.rb.setColor(color)
		self.rb.setWidth(1)
		x = event.pos().x()
		y = event.pos().y()
		if self.mCtrl:
			startingPoint = QPoint(x,y)
			snapper = QgsMapCanvasSnapper(self.canvas)
			(retval,result) = snapper.snapToCurrentLayer (startingPoint, QgsSnapper.SnapToVertex)
			if result <> []:
				point = result[0].snappedVertex
			else:
				(retval,result) = snapper.snapToBackgroundLayers(startingPoint)
				if result <> []:
					point = result[0].snappedVertex
				else:
					point = self.toLayerCoordinates(layer,event.pos())
		else:
			point = self.toLayerCoordinates(layer,event.pos())	
		pointMap = self.toMapCoordinates(layer, point)
		self.xc = pointMap.x()
		self.yc = pointMap.y()
		if self.rb:return
		    
    def canvasMoveEvent(self,event):
        settings = QSettings()
        if not self.rb:return
        currpoint = self.toMapCoordinates(event.pos())
        currx = currpoint.x()
        curry = currpoint.y()
        r = math.sqrt(pow(abs( currx - self.xc),2) + pow(abs( curry - self.yc),2))
        self.rb.reset(True)
        segments = settings.value("/RectOvalDigit/segments",36,type=int)
        points = []
        for t in [(2*math.pi)/segments*i for i in range(segments)]:
            points.append((r*math.cos(t), r*math.sin(t)))
        polygon = [QgsPoint(i[0]+self.xc,i[1]+self.yc) for i in points]
        #delete [self.rb.addPoint( point ) for point in polygon]
	self.rb.setToGeometry(QgsGeometry.fromPolygon([polygon]), None)
        
    def canvasReleaseEvent(self,event):
        if not self.rb:return		
        if self.rb.numberOfVertices() > 2:
            geom = self.rb.asGeometry()
            self.emit(SIGNAL("rbFinished(PyQt_PyObject)"), geom)
            
        self.rb.reset(True)
        self.rb=None
        
        self.canvas.refresh()

    def showSettingsWarning(self):
        pass
    
    def activate(self):
        self.canvas.setCursor(self.cursor)
        
    def deactivate(self):
        pass

    def isZoomTool(self):
        return False
  
    def isTransient(self):
        return False
    
    def isEditTool(self):
        return True

# Tool class
class RectByExtentTool(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self,canvas)
        self.canvas=canvas
        self.rb=None
        self.x0 = None
        self.y0 = None
        #our own fancy cursor
        self.cursor = QCursor(QPixmap(["16 16 3 1",
                                       "      c None",
                                       ".     c #FF0000",
                                       "+     c #17a51a",
                                       "                ",
                                       "       +.+      ",
                                       "      ++.++     ",
                                       "     +.....+    ",
                                       "    +.  .  .+   ",
                                       "   +.   .   .+  ",
                                       "  +.    .    .+ ",
                                       " ++.    .    .++",
                                       " ... ...+... ...",
                                       " ++.    .    .++",
                                       "  +.    .    .+ ",
                                       "   +.   .   .+  ",
                                       "   ++.  .  .+   ",
                                       "    ++.....+    ",
                                       "      ++.++     ",
                                       "       +.+      "]))
                                  
 
    def canvasPressEvent(self,event):
		layer = self.canvas.currentLayer()
		color = QColor(255,0,0)
		self.rb = QgsRubberBand(self.canvas, True)
		self.rb.setColor(color)
		self.rb.setWidth(1)
		x = event.pos().x()
		y = event.pos().y()
		point = self.toLayerCoordinates(layer,event.pos())		
		pointMap = self.toMapCoordinates(layer, point)
		self.x0 = pointMap.x()
		self.y0 = pointMap.y()		
		if self.rb:return
		    
    def canvasMoveEvent(self,event):
        if not self.rb:return
        currpoint = self.toMapCoordinates(event.pos())
        currx = currpoint.x()
        curry = currpoint.y()
        self.rb.reset(True)
        pt1 = (self.x0, self.y0)
        pt2 = (self.x0, curry)
        pt3 = (currx, curry)
        pt4 = (currx, self.y0)
        points = [pt1, pt2, pt3, pt4]
        polygon = [QgsPoint(i[0],i[1]) for i in points]
	self.rb.setToGeometry(QgsGeometry.fromPolygon([polygon]), None)
        #delete [self.rb.addPoint( point ) for point in polygon]                
        
    def canvasReleaseEvent(self,event):
        if not self.rb:return		
        if self.rb.numberOfVertices() > 2:
            geom = self.rb.asGeometry()
            self.emit(SIGNAL("rbFinished(PyQt_PyObject)"), geom)
            
        self.rb.reset(True)
        self.rb=None
        self.canvas.refresh()

    def showSettingsWarning(self):
        pass
    
    def activate(self):
        self.canvas.setCursor(self.cursor)
        
    def deactivate(self):
        pass

    def isZoomTool(self):
        return False
  
    def isTransient(self):
        return False
    
    def isEditTool(self):
        return True

# Tool class
class RectFromCenterTool(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self,canvas)
        self.canvas=canvas
        self.rb=None
        self.xc = None
        self.yc = None
        self.mCtrl = None
        #our own fancy cursor
        self.cursor = QCursor(QPixmap(["16 16 3 1",
                                       "      c None",
                                       ".     c #FF0000",
                                       "+     c #17a51a",
                                       "                ",
                                       "       +.+      ",
                                       "      ++.++     ",
                                       "     +.....+    ",
                                       "    +.  .  .+   ",
                                       "   +.   .   .+  ",
                                       "  +.    .    .+ ",
                                       " ++.    .    .++",
                                       " ... ...+... ...",
                                       " ++.    .    .++",
                                       "  +.    .    .+ ",
                                       "   +.   .   .+  ",
                                       "   ++.  .  .+   ",
                                       "    ++.....+    ",
                                       "      ++.++     ",
                                       "       +.+      "]))
                 
    def keyPressEvent(self,  event):
        if event.key() == Qt.Key_Control:
            self.mCtrl = True


    def keyReleaseEvent(self,  event):
        if event.key() == Qt.Key_Control:
            self.mCtrl = False
    
    def canvasPressEvent(self,event):
		layer = self.canvas.currentLayer()
		color = QColor(255,0,0)
		self.rb = QgsRubberBand(self.canvas, True)
		self.rb.setColor(color)
		self.rb.setWidth(1)
		x = event.pos().x()
		y = event.pos().y()
		if self.mCtrl:
			startingPoint = QPoint(x,y)
			snapper = QgsMapCanvasSnapper(self.canvas)
			(retval,result) = snapper.snapToCurrentLayer (startingPoint, QgsSnapper.SnapToVertex)
			if result <> []:
				point = result[0].snappedVertex
			else:
				(retval,result) = snapper.snapToBackgroundLayers(startingPoint)
				if result <> []:
					point = result[0].snappedVertex
				else:
					point = self.toLayerCoordinates(layer,event.pos())
		else:
			point = self.toLayerCoordinates(layer,event.pos())		
		pointMap = self.toMapCoordinates(layer, point)
		self.xc = pointMap.x()
		self.yc = pointMap.y()
		if self.rb:return
		    
    def canvasMoveEvent(self,event):
        if not self.rb:return
        currpoint = self.toMapCoordinates(event.pos())
        currx = currpoint.x()
        curry = currpoint.y()
        xOffset = abs( currx - self.xc)
        yOffset = abs( curry - self.yc)      
        self.rb.reset(True)
        pt1 = QgsPoint(-xOffset, -yOffset)
        pt2 = QgsPoint(-xOffset, yOffset)
        pt3 = QgsPoint(xOffset, yOffset)
        pt4 = QgsPoint(xOffset, -yOffset)
        points = [pt1, pt2, pt3, pt4]
        polygon = [QgsPoint(i[0]+self.xc,i[1]+self.yc) for i in points]
	#delete [self.rb.addPoint( point ) for point in polygon]
	self.rb.setToGeometry(QgsGeometry.fromPolygon([polygon]), None)

        
    def canvasReleaseEvent(self,event):
        if not self.rb:return		
        if self.rb.numberOfVertices() > 2:
            geom = self.rb.asGeometry()
            self.emit(SIGNAL("rbFinished(PyQt_PyObject)"), geom)
            
        self.rb.reset(True)
        self.rb=None
        self.canvas.refresh()

    def showSettingsWarning(self):
        pass
    
    def activate(self):
        self.canvas.setCursor(self.cursor)
        
    def deactivate(self):
        pass

    def isZoomTool(self):
        return False
  
    def isTransient(self):
        return False
    
    def isEditTool(self):
        return True

# Tool class
class SquareFromCenterTool(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self,canvas)
        self.canvas=canvas
        self.rb = None
        self.xc = None
        self.yc = None
        self.mCtrl = None
        #our own fancy cursor
        self.cursor = QCursor(QPixmap(["16 16 3 1",
                                       "      c None",
                                       ".     c #FF0000",
                                       "+     c #800080",
                                       "                ",
                                       "       +.+      ",
                                       "      ++.++     ",
                                       "     +.....+    ",
                                       "    +.  .  .+   ",
                                       "   +.   .   .+  ",
                                       "  +.    .    .+ ",
                                       " ++.    .    .++",
                                       " ... ...+... ...",
                                       " ++.    .    .++",
                                       "  +.    .    .+ ",
                                       "   +.   .   .+  ",
                                       "   ++.  .  .+   ",
                                       "    ++.....+    ",
                                       "      ++.++     ",
                                       "       +.+      "]))
                                  
 
    def keyPressEvent(self,  event):
        if event.key() == Qt.Key_Control:
            self.mCtrl = True


    def keyReleaseEvent(self,  event):
        if event.key() == Qt.Key_Control:
            self.mCtrl = False
    
    def canvasPressEvent(self,event):
		layer = self.canvas.currentLayer()
		color = QColor(255,0,0)
		self.rb = QgsRubberBand(self.canvas, True)
		self.rb.setColor(color)
		self.rb.setWidth(1)
		x = event.pos().x()
		y = event.pos().y()
		if self.mCtrl:
			startingPoint = QPoint(x,y)
			snapper = QgsMapCanvasSnapper(self.canvas)
			(retval,result) = snapper.snapToCurrentLayer (startingPoint, QgsSnapper.SnapToVertex)
			if result <> []:
				point = result[0].snappedVertex
			else:
				(retval,result) = snapper.snapToBackgroundLayers(startingPoint)
				if result <> []:
					point = result[0].snappedVertex
				else:
					point = self.toLayerCoordinates(layer,event.pos())
		else:
			point = self.toLayerCoordinates(layer,event.pos())		
		pointMap = self.toMapCoordinates(layer, point)
		self.xc = pointMap.x()
		self.yc = pointMap.y()
		if self.rb:return
		    
    def canvasMoveEvent(self,event):
        if not self.rb:return
        currpoint = self.toMapCoordinates(event.pos())
        distance= math.sqrt(currpoint.sqrDist( self.xc, self.yc ))
        offset = distance/math.sqrt(2)
        self.rb.reset(True)
        pt1 = (-offset, -offset)
        pt2 = (-offset, offset)
        pt3 = (offset, offset)
        pt4 = (offset, -offset)
        points = [pt1, pt2, pt3, pt4]
        polygon = [QgsPoint(i[0]+self.xc,i[1]+self.yc) for i in points]
        #delete [self.rb.addPoint( point ) for point in polygon]
	self.rb.setToGeometry(QgsGeometry.fromPolygon([polygon]), None)
        
    def canvasReleaseEvent(self,event):
        if not self.rb:return		
        if self.rb.numberOfVertices() > 2:
            geom = self.rb.asGeometry()
            self.emit(SIGNAL("rbFinished(PyQt_PyObject)"), geom)
            
        self.rb.reset(True)
        self.rb=None
        
        self.canvas.refresh()

    def showSettingsWarning(self):
        pass
    
    def activate(self):
        self.canvas.setCursor(self.cursor)
        
    def deactivate(self):
        pass

    def isZoomTool(self):
        return False
  
    def isTransient(self):
        return False
    
    def isEditTool(self):
        return True

class RotateTool(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.rb = None
        self.cf = None
        self.fid = None
        self.layer = None
        self.cursor = QCursor(QPixmap(["16 16 3 1",
                                      "      c None",
                                      ".     c #FF0000",
                                      "+     c #2228b4",
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
                                      
 
    
 
    def canvasPressEvent(self, event):
        self.layer = self.canvas.currentLayer()
        color = QColor(255,0,0)
        self.rb = QgsRubberBand(self.canvas, True)
        self.rb.setColor(color)
        self.rb.setWidth(1)
        if self.layer.selectedFeatureCount() != 1:
            QMessageBox.information(None,  "Selection information",  "Please select exactly one rectangle or oval.")
            return
        else:
            self.cf = QgsFeature()
            self.fid = self.layer.selectedFeaturesIds()[0]
	    request = QgsFeatureRequest(self.fid)
	    fit = self.layer.getFeatures(request)
	    fit.nextFeature(self.cf)
            self.rb.setToGeometry( self.cf.geometry(), self.layer)    
        if self.rb:return                    

    def canvasMoveEvent(self,event):
        if not self.rb:return        
        currpoint = self.toLayerCoordinates(self.layer,event.pos())
        bounding = self.cf.geometry().boundingBox()
        center = bounding.center()
        angle = center.azimuth( currpoint )
        phi = -(angle*math.pi/180)
        self.rb.reset(True)        
        rotgeom = rotate(self.cf.geometry(), center, phi)
        self.rb.setToGeometry( rotgeom, self.layer )         
        
    def canvasReleaseEvent(self,event):
        if not self.rb:return		
        if self.rb.numberOfVertices() > 2:
            geom = self.rb.asGeometry()
            self.emit(SIGNAL("rbFinished(PyQt_PyObject)"), [geom, self.fid])
        
        self.cf = None
        self.fid = None
        self.rb.reset(True)
        self.rb=None
        self.canvas.refresh()

    def activate(self):
        self.canvas.setCursor(self.cursor)
  
    def deactivate(self):
        pass

    def isZoomTool(self):
        return False
  
    def isTransient(self):
        return False
    
    def isEditTool(self):
        return True

# Rotates a geometry.
# (c) Stefan Ziegler
def rotate(geom,  point,  angle):
    coords = []
    ring = []
    for i in geom.asPolygon():
        for k in i: 
            p1 = QgsPoint(k.x() - point.x(),  k.y() - point.y())
            p2 = rotatePoint(p1,  angle)
            p3 = QgsPoint(point.x() + p2.x(),  point.y() + p2.y())
            ring.append(p3)
        coords.append(ring)
        ring = []
    return QgsGeometry().fromPolygon(coords)
            
# Rotates a single point (centre 0/0).
# (c) Stefan Ziegler
def rotatePoint(point,  angle):
    x = math.cos(angle)*point.x() - math.sin(angle)*point.y()
    y = math.sin(angle)*point.x() + math.cos(angle)*point.y()
    return QgsPoint(x,  y)
