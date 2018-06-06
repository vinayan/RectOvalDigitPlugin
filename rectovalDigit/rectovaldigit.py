# -*- coding: utf-8 -*-
#-----------------------------------------------------------
# 
# Rectangles Ovals Digitizing
# Copyright (C) 2011 - 2012 Pavol Kapusta
# pavol.kapusta@gmail.com
# bug fix in version 1.1.3 added by Thomas Baumann rdbath.regiodata@gmail.com
# Code adopted/adapted from:
#
# 'SelectPlus Menu Plugin', Copyright (C) Barry Rowlingson
# 'CadTools Plugin', Copyright (C) Stefan Ziegler
# 'Numerical Vertex Edit Plugin' and 'traceDigitize' plugin, Copyright (C) Cédric Möri
#
#-----------------------------------------------------------
# 
# licensed under the terms of GNU GPL 2
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
# 
#---------------------------------------------------------------------


# Import the PyQt and the QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

#Import own classes and tools
from rectovaldigittools import RectByExtentTool, RectFromCenterTool, SquareFromCenterTool, CircleFromCenterTool, OvalByExtentTool, OvalFromCenterTool, RotateTool

# initialize Qt resources from file resources.py
import resources

# Our main class for the plugin
class RectOvalDigit:

    def __init__(self, iface):
    # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()


    def initGui(self):
        settings = QSettings()
        # Add button
        self.toolBar = self.iface.addToolBar("Rectangles, ovals digitizing tools")
        self.toolBar.setObjectName("RectOvalDigit")
        # Add actions
        self.rectbyextent = QAction(QIcon(":/plugins/rectovalDigit/icons/rectbyextent.png"),  "Rectangle by extent",  self.iface.mainWindow())
        self.rectfromcenter = QAction(QIcon(":/plugins/rectovalDigit/icons/rectfromcenter.png"),  "Rectangle from center",  self.iface.mainWindow())
        self.squarefromcenter = QAction(QIcon(":/plugins/rectovalDigit/icons/squarefromcenter.png"),  "Square from center",  self.iface.mainWindow())
        self.circlefromcenter = QAction(QIcon(":/plugins/rectovalDigit/icons/circlefromcenter.png"),  "Circle from center",  self.iface.mainWindow())
        self.ovalbyextent = QAction(QIcon(":/plugins/rectovalDigit/icons/ovalbyextent.png"),  "Ellipse by extent",  self.iface.mainWindow())
        self.ovalfromcenter = QAction(QIcon(":/plugins/rectovalDigit/icons/ovalfromcenter.png"),  "Ellipse from center",  self.iface.mainWindow())
        
        self.toolBar.addActions( [ self.rectbyextent, self.rectfromcenter, self.squarefromcenter, self.circlefromcenter, self.ovalbyextent, self.ovalfromcenter ] )

        self.rectbyextent.setCheckable(True)
        self.rectbyextent.setEnabled(False)
        self.rectfromcenter.setCheckable(True)
        self.rectfromcenter.setEnabled(False)
        self.squarefromcenter.setCheckable(True)
        self.squarefromcenter.setEnabled(False)
        self.circlefromcenter.setCheckable(True)
        self.circlefromcenter.setEnabled(False)
        self.ovalbyextent.setCheckable(True)
        self.ovalbyextent.setEnabled(False)
        self.ovalfromcenter.setCheckable(True)
        self.ovalfromcenter.setEnabled(False)

        self.toolBar.addSeparator()
        
        # Add rotate 
        self.rotaterectoval =  QAction(QIcon(":/plugins/rectovalDigit/icons/rotate.png"),  "Rotate rectangle or oval",  self.iface.mainWindow())
        self.rotaterectoval.setEnabled(False)
        self.rotaterectoval.setCheckable(True)
        self.toolBar.addAction(self.rotaterectoval)
        self.toolBar.addSeparator()
               
        # Add spinbox
        self.spinBox = QSpinBox(self.iface.mainWindow())        
        self.spinBox.setMinimum(3)
        self.spinBox.setMaximum(72)
        segvalue = settings.value("/RectOvalDigit/segments",36,type=int)
        if not segvalue:
            settings.setValue("/RectOvalDigit/segments", 36)
        self.spinBox.setValue(segvalue)
        self.spinBox.setSingleStep(1)
        self.spinBoxAction = self.toolBar.addWidget(self.spinBox)
        self.spinBox.setToolTip("Number of segments for ovals")
        self.spinBoxAction.setEnabled(False)
        
        # Connect to signals for button behaviour
        QObject.connect(self.rectbyextent,  SIGNAL("activated()"),  self.rectbyextentdigit)
        QObject.connect(self.rectfromcenter,  SIGNAL("activated()"),  self.rectfromcenterdigit)
        QObject.connect(self.squarefromcenter,  SIGNAL("activated()"),  self.squarefromcenterdigit)
        QObject.connect(self.circlefromcenter,  SIGNAL("activated()"),  self.circlefromcenterdigit)
        QObject.connect(self.ovalbyextent,  SIGNAL("activated()"),  self.ovalbyextentdigit)
        QObject.connect(self.ovalfromcenter,  SIGNAL("activated()"),  self.ovalfromcenterdigit)
        QObject.connect(self.rotaterectoval,  SIGNAL("activated()"),  self.rotatedigit)
        QObject.connect(self.spinBox,  SIGNAL("valueChanged(int)"),  self.segmentsettings)
        
        self.iface.legendInterface().currentLayerChanged.connect(self.toggle)
        
        QObject.connect(self.canvas, SIGNAL("mapToolSet(QgsMapTool*)"), self.deactivate)
    
        # Get the tools
        self.rectbyextenttool = RectByExtentTool( self.canvas )
        self.rectfromcentertool = RectFromCenterTool( self.canvas )
        self.squarefromcentertool = SquareFromCenterTool( self.canvas )
        self.circlefromcentertool = CircleFromCenterTool( self.canvas )
        self.ovalbyextenttool = OvalByExtentTool( self.canvas )
        self.ovalfromcentertool = OvalFromCenterTool( self.canvas )
        self.rotatetool = RotateTool( self.canvas )
    
    def rectbyextentdigit(self):          
        self.canvas.setMapTool(self.rectbyextenttool)
        self.rectbyextent.setChecked(True)
        QObject.connect(self.rectbyextenttool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)      
    
    def rectfromcenterdigit(self):
        self.canvas.setMapTool(self.rectfromcentertool)
        self.rectfromcenter.setChecked(True)
        QObject.connect(self.rectfromcentertool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature) 
        
    def squarefromcenterdigit(self):
        self.canvas.setMapTool(self.squarefromcentertool)
        self.squarefromcenter.setChecked(True)
        QObject.connect(self.squarefromcentertool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature) 
        
    def circlefromcenterdigit(self):
        self.canvas.setMapTool(self.circlefromcentertool)
        self.circlefromcenter.setChecked(True)
        QObject.connect(self.circlefromcentertool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature) 
        
    def ovalbyextentdigit(self):
        self.canvas.setMapTool(self.ovalbyextenttool)
        self.ovalbyextent.setChecked(True)
        QObject.connect(self.ovalbyextenttool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature) 
        
    def ovalfromcenterdigit(self):
        self.canvas.setMapTool(self.ovalfromcentertool)
        self.ovalfromcenter.setChecked(True)
        QObject.connect(self.ovalfromcentertool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature) 
        
   
    def rotatedigit(self):
        mc = self.canvas
        layer = mc.currentLayer() 
        if layer.selectedFeatureCount() != 1:
            QMessageBox.information(None,  "Selection information",  "Please select exactly one rectangle or oval.")
            self.rotaterectoval.setChecked(False)
        else:
            self.canvas.setMapTool(self.rotatetool)
            self.rotaterectoval.setChecked(True)
            QObject.connect(layer,SIGNAL("selectionChanged()"),self.selectionchanged)  
            QObject.connect(self.rotatetool, SIGNAL("rbFinished(PyQt_PyObject)"), self.changegeom)
            			  
	
    def selectionchanged(self):
        mc = self.canvas
        layer = mc.currentLayer() 
        if layer.selectedFeatureCount() != 1:
            self.rotaterectoval.setChecked(False)
    
    def segmentsettings(self):
		settings = QSettings()
		settings.setValue("/RectOvalDigit/segments", self.spinBox.value())
    
            


	
        
    def toggle(self):
        #print "toggle"
        mc = self.canvas
        layer = mc.currentLayer()
        #Decide whether the plugin button/menu is enabled or disabled
        if layer is not None:
            if layer.type() == QgsMapLayer.VectorLayer:
                try:
                    layer.editingStarted.disconnect(self.toggle)
                except:
                    pass
                try:
                    layer.editingStopped.disconnect(self.toggle)
                except:
                    pass
                
                if layer.geometryType() == 2:
                    try:
                        layer.editingStarted.connect(self.toggle, Qt.UniqueConnection)
                        layer.editingStopped.connect(self.toggle, Qt.UniqueConnection)
                    except TypeError:
                        pass

                if (layer.isEditable() and (layer.geometryType() == QGis.Polygon)):
                    self.rectbyextent.setEnabled(True)
                    self.rectfromcenter.setEnabled(True)
                    self.squarefromcenter.setEnabled(True)
                    self.circlefromcenter.setEnabled(True)
                    self.ovalbyextent.setEnabled(True)
                    self.ovalfromcenter.setEnabled(True)
                    self.rotaterectoval.setEnabled(True)
                    self.spinBoxAction.setEnabled(True)
                
                elif(not layer.isEditable() and layer.geometryType() == 2):
                    self.rectbyextent.setEnabled(False)
                    self.rectfromcenter.setEnabled(False)
                    self.squarefromcenter.setEnabled(False)
                    self.circlefromcenter.setEnabled(False)
                    self.ovalbyextent.setEnabled(False)
                    self.ovalfromcenter.setEnabled(False)
                    self.rotaterectoval.setEnabled(False)
                    self.spinBoxAction.setEnabled(False)
                    
                else:
                    self.rectbyextent.setEnabled(False)
                    self.rectfromcenter.setEnabled(False)
                    self.squarefromcenter.setEnabled(False)
                    self.circlefromcenter.setEnabled(False)
                    self.ovalbyextent.setEnabled(False)
                    self.ovalfromcenter.setEnabled(False)
                    self.rotaterectoval.setEnabled(False)
                    self.spinBoxAction.setEnabled(False)
            
    def deactivate(self):
        self.rectbyextent.setChecked(False)
        self.rectfromcenter.setChecked(False)
        self.squarefromcenter.setChecked(False)
        self.circlefromcenter.setChecked(False)
        self.ovalbyextent.setChecked(False)
        self.ovalfromcenter.setChecked(False)
        self.rotaterectoval.setChecked(False)
        QObject.disconnect(self.rectbyextenttool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.rectfromcentertool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.squarefromcentertool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.circlefromcentertool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.ovalbyextenttool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.ovalfromcentertool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.rotatetool, SIGNAL("rbFinished(PyQt_PyObject)"), self.changegeom)
        

    def createFeature(self, geom):
        settings = QSettings()
        mc = self.canvas
        layer = mc.currentLayer()
        renderer = mc.mapRenderer()
        layerCRSSrsid = layer.crs().srsid()
        projectCRSSrsid = renderer.destinationCrs().srsid()
        provider = layer.dataProvider()
        f = QgsFeature()
        
        
        #On the Fly reprojection.
        if layerCRSSrsid != projectCRSSrsid:
            geom.transform(QgsCoordinateTransform(projectCRSSrsid, layerCRSSrsid))
                                    
        f.setGeometry(geom)
        
        # add attribute fields to feature
        fields = layer.pendingFields()

        # vector api change update

        f.initAttributes(fields.count())
        for i in range(fields.count()):
            f.setAttribute(i,provider.defaultValue(i))

        if not (settings.value("/qgis/digitizing/disable_enter_attribute_values_dialog")):
            self.iface.openFeatureForm( layer, f, False)
        
        layer.beginEditCommand("Feature added")       
        layer.addFeature(f)
        layer.endEditCommand()


    def changegeom(self, result):
        mc = self.canvas
        layer = mc.currentLayer()
        renderer = mc.mapRenderer()
        layerCRSSrsid = layer.crs().srsid()
        projectCRSSrsid = renderer.destinationCrs().srsid()
        geom = result[0]
        fid = result[1]
        if layerCRSSrsid != projectCRSSrsid:
            geom.transform(QgsCoordinateTransform(projectCRSSrsid, layerCRSSrsid))
        layer.beginEditCommand("Feature rotated")
        layer.changeGeometry( fid, geom )
        layer.endEditCommand()
        
    def unload(self):
		self.toolBar.removeAction(self.rectbyextent)
		self.toolBar.removeAction(self.rectfromcenter)
		self.toolBar.removeAction(self.squarefromcenter)
		self.toolBar.removeAction(self.circlefromcenter)
		self.toolBar.removeAction(self.ovalbyextent)
		self.toolBar.removeAction(self.ovalfromcenter)
		self.toolBar.removeAction(self.rotaterectoval)
		self.toolBar.removeAction(self.spinBoxAction)
		del self.toolBar
   
 
