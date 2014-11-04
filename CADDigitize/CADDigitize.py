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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
from qgis.core import *
from qgis.gui import *
# Initialize Qt resources from file resources.py
import resources_rc
import os.path


#Import own classes and tools
from CADDigitize_tools_circle import *
from CADDigitize_tools_rect import *
from CADDigitize_tools_ellipse import *
from CADDigitize_tools_arc import *
from CADDigitize_tools_regularpolygon import *
from CADDigitize_dialog import Ui_CADDigitizeSettings

class CADDigitize:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'CADDigitize_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

    def initGui(self):
        
        settings = QSettings()
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        # Add toolbar 
        self.menu = QMenu()
        self.menu.setTitle( QCoreApplication.translate( "CADDigitize","&CADDigitize" ) )
        self.caddigitize_help = QAction( QCoreApplication.translate("CADDigitize", "Help" ), self.iface.mainWindow() )
        self.caddigitize_settings = QAction( QCoreApplication.translate("CADDigitize", "Settings" ), self.iface.mainWindow() )
  
        self.menu.addActions( [self.caddigitize_help, self.caddigitize_settings] )

        menu_bar = self.iface.mainWindow().menuBar()
        actions = menu_bar.actions()
        lastAction = actions[ len( actions ) - 1 ]
        menu_bar.insertMenu( lastAction, self.menu )

        self.caddigitize_help.triggered.connect(self.doHelp)
        self.caddigitize_settings.triggered.connect(self.doSettings)

        # Add button
        self.toolBar = self.iface.addToolBar("CADDigitize")
        self.toolBar.setObjectName("CADDigitize")
        
        self.optionsToolBar = self.iface.addToolBar("CADDigitize Options")
        self.optionsToolBar.setObjectName("CADDigitize Options")
        
        self.circleToolButton = QToolButton(self.toolBar)
        self.rectToolButton = QToolButton(self.toolBar)
        self.ellipseToolButton = QToolButton(self.toolBar)
        self.arcToolButton = QToolButton(self.toolBar)
        self.rpolygonToolButton = QToolButton(self.toolBar)
        self.circleToolButton.setPopupMode(QToolButton.MenuButtonPopup)
        self.rectToolButton.setPopupMode(QToolButton.MenuButtonPopup)
        self.ellipseToolButton.setPopupMode(QToolButton.MenuButtonPopup)
        self.arcToolButton.setPopupMode(QToolButton.MenuButtonPopup)
        self.rpolygonToolButton.setPopupMode(QToolButton.MenuButtonPopup)



        ###
        # Circles
        ###

        # Add actions
        self.circleBy2Points = QAction(QIcon(":/plugins/CADDigitize/icons/circleBy2Points.png"),  "Circle by 2 points",  self.iface.mainWindow())
        self.circleBy3Points = QAction(QIcon(":/plugins/CADDigitize/icons/circleBy3Points.png"),  "Circle by 3 points",  self.iface.mainWindow())
        self.circleByCenterRadius = QAction(QIcon(":/plugins/CADDigitize/icons/circleByCenterRadius.png"),  "Circle by center and radius",  self.iface.mainWindow())
        self.circleByCenterPoint = QAction(QIcon(":/plugins/CADDigitize/icons/circleByCenterPoint.png"),  "Circle by center and a point",  self.iface.mainWindow())

        self.circleToolButton.addActions( [ self.circleBy2Points, self.circleBy3Points, self.circleByCenterRadius, self.circleByCenterPoint ] )
        self.circleToolButton.setDefaultAction(self.circleBy2Points)
        self.toolBar.addWidget( self.circleToolButton )


        self.circleBy2Points.setCheckable(True)
        self.circleBy2Points.setEnabled(False)
        self.circleBy3Points.setCheckable(True)
        self.circleBy3Points.setEnabled(False)
        self.circleByCenterRadius.setCheckable(True)
        self.circleByCenterRadius.setEnabled(False)
        self.circleByCenterPoint.setCheckable(True)
        self.circleByCenterPoint.setEnabled(False)

        self.toolBar.addSeparator()

        ###
        # Rectangles
        ###

        self.rectBy3Points = QAction(QIcon(":/plugins/CADDigitize/icons/rectBy3Points.png"), "Rectangle by 3 points", self.iface.mainWindow())
        self.rectByExtent = QAction(QIcon(":/plugins/CADDigitize/icons/rectByExtent.png"), "Rectangle by extent", self.iface.mainWindow())
        self.rectFromCenter = QAction(QIcon(":/plugins/CADDigitize/icons/rectFromCenter.png"), "Rectangle from center", self.iface.mainWindow())
        self.squareFromCenter = QAction(QIcon(":/plugins/CADDigitize/icons/squareFromCenter.png"), "Square from center", self.iface.mainWindow())
        self.rectToolButton.addActions( [self.rectBy3Points, self.rectByExtent, self.rectFromCenter, self.squareFromCenter] )
        self.rectToolButton.setDefaultAction(self.rectBy3Points)
        self.toolBar.addWidget( self.rectToolButton )

        self.rectBy3Points.setEnabled(False)
        self.rectBy3Points.setCheckable(True)
        self.rectByExtent.setEnabled(False)
        self.rectByExtent.setCheckable(True)
        self.rectFromCenter.setEnabled(False)
        self.rectFromCenter.setCheckable(True)
        self.squareFromCenter.setEnabled(False)
        self.squareFromCenter.setCheckable(True)

        self.toolBar.addSeparator()

        ###
        # Ellipses
        ###


        # Add actions
        self.ellipseByCenter2Points = QAction(QIcon(":/plugins/CADDigitize/icons/ellipseByCenter2Points.png"),  "Ellipse by center and 2 points",  self.iface.mainWindow())
        self.ellipseByCenter3Points = QAction(QIcon(":/plugins/CADDigitize/icons/ellipseByCenter3Points.png"),  "Ellipse by center and 3 points",  self.iface.mainWindow())
        self.ellipseBy4Points= QAction(QIcon(":/plugins/CADDigitize/icons/ellipseBy4Points.png"),  "Ellipse by 4 points",  self.iface.mainWindow())
        self.ellipseByFociPoint = QAction(QIcon(":/plugins/CADDigitize/icons/ellipseByFociPoint.png"),  "Ellipse by foci and a point",  self.iface.mainWindow())
        self.ellipseFromCenter = QAction(QIcon(":/plugins/CADDigitize/icons/ellipseFromCenter.png"),  "Ellipse from center",  self.iface.mainWindow())
        self.ellipseByExtent = QAction(QIcon(":/plugins/CADDigitize/icons/ellipseByExtent.png"),  "Ellipse by extent",  self.iface.mainWindow())

        self.ellipseToolButton.addActions( [ self.ellipseByCenter2Points, self.ellipseByFociPoint, self.ellipseFromCenter, self.ellipseByExtent ] )
        self.ellipseToolButton.setDefaultAction(self.ellipseByCenter2Points)
        self.toolBar.addWidget( self.ellipseToolButton )


        self.ellipseByCenter2Points.setCheckable(True)
        self.ellipseByCenter2Points.setEnabled(False)
        self.ellipseByCenter3Points.setCheckable(True)
        self.ellipseByCenter3Points.setEnabled(False)
        self.ellipseBy4Points.setCheckable(True)
        self.ellipseBy4Points.setEnabled(False)
        self.ellipseByFociPoint.setCheckable(True)
        self.ellipseByFociPoint.setEnabled(False)
        self.ellipseFromCenter.setCheckable(True)
        self.ellipseFromCenter.setEnabled(False)
        self.ellipseByExtent.setCheckable(True)
        self.ellipseByExtent.setEnabled(False)

        self.toolBar.addSeparator()

        ###
        # Arcs
        ###

        # Add actions
        self.arcByCenter2Points = QAction(QIcon(":/plugins/CADDigitize/icons/arcByCenter2Points.png"),  "Arc by center and 2 points",  self.iface.mainWindow())
        self.arcBy3Points = QAction(QIcon(":/plugins/CADDigitize/icons/arcBy3Points.png"),  "Arc by 3 points",  self.iface.mainWindow())
        self.arcByCenterPointAngle = QAction(QIcon(":/plugins/CADDigitize/icons/arcByCenterPointAngle.png"),  "Arc by center, point and angle",  self.iface.mainWindow())

        self.arcToolButton.addActions( [ self.arcByCenter2Points, self.arcBy3Points, self.arcByCenterPointAngle ] )
        self.arcToolButton.setDefaultAction(self.arcByCenter2Points)
        self.toolBar.addWidget( self.arcToolButton )


        self.arcByCenter2Points.setCheckable(True)
        self.arcByCenter2Points.setEnabled(False)
        self.arcBy3Points.setCheckable(True)
        self.arcBy3Points.setEnabled(False)
        self.arcByCenterPointAngle.setCheckable(True)
        self.arcByCenterPointAngle.setEnabled(False)

        self.toolBar.addSeparator()
        
        
        ###
        # Regular Polygon
        ###

        self.rpolygonByCenterPoint = QAction(QIcon(":/plugins/CADDigitize/icons/rpolygonByCenterPoint.png"),  "Regular polygon by center and point",  self.iface.mainWindow())
        self.rpolygonBy2Corners = QAction(QIcon(":/plugins/CADDigitize/icons/rpolygonBy2Corners.png"),  "Regular polygon by 2 corners",  self.iface.mainWindow())
        
        self.rpolygonToolButton.addActions( [ self.rpolygonByCenterPoint, self.rpolygonBy2Corners ] )
        self.rpolygonToolButton.setDefaultAction(self.rpolygonByCenterPoint)
        self.toolBar.addWidget( self.rpolygonToolButton )

        self.rpolygonByCenterPoint.setCheckable(True)
        self.rpolygonByCenterPoint.setEnabled(False)
        self.rpolygonBy2Corners.setCheckable(True)
        self.rpolygonBy2Corners.setEnabled(False)

        self.toolBar.addSeparator()
        
        
        ### Conect

        QObject.connect(self.circleBy2Points,  SIGNAL("activated()"), self.circleBy2PointsDigit)
        QObject.connect(self.circleBy3Points,  SIGNAL("activated()"), self.circleBy3PointsDigit)
        QObject.connect(self.circleByCenterRadius,  SIGNAL("activated()"),  self.circleByCenterRadiusDigit)
        QObject.connect(self.circleByCenterPoint,  SIGNAL("activated()"),  self.circleByCenterPointDigit)
        QObject.connect(self.rectBy3Points,  SIGNAL("activated()"),  self.rectBy3PointsDigit)
        QObject.connect(self.rectByExtent,  SIGNAL("activated()"),  self.rectByExtentDigit)
        QObject.connect(self.rectFromCenter,  SIGNAL("activated()"),  self.rectFromCenterDigit)
        QObject.connect(self.squareFromCenter,  SIGNAL("activated()"),  self.squareFromCenterDigit)
        QObject.connect(self.ellipseByCenter2Points,  SIGNAL("activated()"), self.ellipseByCenter2PointsDigit)
        QObject.connect(self.ellipseByCenter3Points,  SIGNAL("activated()"), self.ellipseByCenter3PointsDigit)
        QObject.connect(self.ellipseBy4Points,  SIGNAL("activated()"),  self.ellipseBy4PointsDigit)
        QObject.connect(self.ellipseByFociPoint,  SIGNAL("activated()"),  self.ellipseByFociPointDigit)
        QObject.connect(self.ellipseFromCenter,  SIGNAL("activated()"),  self.ellipseFromCenterDigit)
        QObject.connect(self.ellipseByExtent,  SIGNAL("activated()"),  self.ellipseByExtentDigit)
        QObject.connect(self.arcByCenter2Points,  SIGNAL("activated()"), self.arcByCenter2PointsDigit)
        QObject.connect(self.arcBy3Points,  SIGNAL("activated()"), self.arcBy3PointsDigit)
        QObject.connect(self.arcByCenterPointAngle,  SIGNAL("activated()"), self.arcByCenterPointAngleDigit)
        QObject.connect(self.rpolygonByCenterPoint,  SIGNAL("activated()"), self.rpolygonByCenterPointDigit)
        QObject.connect(self.rpolygonBy2Corners,  SIGNAL("activated()"), self.rpolygonBy2CornersDigit)

        QObject.connect(self.iface, SIGNAL("currentLayerChanged(QgsMapLayer*)"), self.toggle)
        QObject.connect(self.canvas, SIGNAL("mapToolSet(QgsMapTool*)"), self.deactivate)


        
        # Get the tools
        self.circleBy2Points_tool = CircleBy2PointsTool( self.canvas )
        self.circleBy3Points_tool = CircleBy3PointsTool( self.canvas )
        self.circleByCenterRadius_tool = CircleByCenterRadiusTool( self.canvas )
        self.circleByCenterPoint_tool = CircleByCenterPointTool( self.canvas )
        self.rectBy3Points_tool = RectBy3PointsTool( self.canvas )
        self.rectByExtent_tool = RectByExtentTool( self.canvas )
        self.rectFromCenter_tool = RectFromCenterTool( self.canvas )
        self.squareFromCenter_tool = SquareFromCenterTool( self.canvas )
        self.ellipseByCenter2Points_tool = EllipseByCenter2PointsTool( self.canvas )
        self.ellipseByCenter3Points_tool = EllipseByCenter3PointsTool( self.canvas )
        self.ellipseBy4Points_tool= EllipseBy4PointsTool( self.canvas )
        self.ellipseByFociPoint_tool = EllipseByFociPointTool( self.canvas )
        self.ellipseByExtent_tool = EllipseByExtentTool( self.canvas )
        self.ellipseFromCenter_tool = EllipseFromCenterTool( self.canvas )
        self.arcByCenter2Points_tool = ArcByCenter2PointsTool( self.canvas )
        self.arcBy3Points_tool = ArcBy3PointsTool( self.canvas )
        self.arcByCenterPointAngle_tool = ArcByCenterPointAngleTool( self.canvas )
        self.rpolygonByCenterPoint_tool = RPolygonByCenterPointTool( self.canvas )
        self.rpolygonBy2Corners_tool = RPolygon2CornersTool( self.canvas )


#####################################################################################################
#                                                                                                   #
#                                                                                                   #
#                                       TOOLBAR OPTIONS                                             #
#                                                                                                   #
#                                                                                                   #
#####################################################################################################

    #####################
    #       Arcs        #
    #####################
    def arcOptions(self):
        settings = QSettings()
        self.optionsToolBar.clear()
        
        
        self.arc_featurePitch = settings.value("/CADDigitize/arc/pitch", 2,type=float)
        self.arc_featureAngle = settings.value("/CADDigitize/arc/angle", 1,type=int)
        self.arc_method = settings.value("/CADDigitize/arc/method",  "pitch")
        self.arc_angleDirection = settings.value("/CADDigitize/arc/direction",  "ClockWise")
        
        mc = self.canvas
        layer = mc.currentLayer()
        if layer.geometryType() == 2:
            self.arc_polygonCreation = settings.value("/CADDigitize/arc/polygon",  "pie")
            self.ArcPolygonCombo = QComboBox(self.iface.mainWindow())
            self.ArcPolygonCombo.addItems(["pie", "chord"])
            self.ArcPolygonComboAction = self.optionsToolBar.addWidget(self.ArcPolygonCombo)
            if self.arc_polygonCreation == "pie":
                self.ArcPolygonCombo.setCurrentIndex(0)
            else:
                self.ArcPolygonCombo.setCurrentIndex(1) 
                
            QObject.connect(self.ArcPolygonCombo, SIGNAL("currentIndexChanged(int)"), self.polygonArc)  
            
        self.ArcFeatureSpin = QDoubleSpinBox(self.iface.mainWindow())
        self.ArcAngleDirectionCombo = QComboBox(self.iface.mainWindow())
        self.ArcAngleDirectionCombo.addItems(["ClockWise", "CounterClockWise"])
        self.ArcAngleDirectionComboAction = self.optionsToolBar.addWidget(self.ArcAngleDirectionCombo)
        self.ArcFeatureCombo = QComboBox(self.iface.mainWindow())
        self.ArcFeatureCombo.addItems(["pitch", "angle"])
        self.ArcFeatureComboAction = self.optionsToolBar.addWidget(self.ArcFeatureCombo)
        

        if self.arc_method == "pitch":
            self.ArcFeatureCombo.setCurrentIndex(0)
            self.ArcFeatureSpin.setMinimum(1)
            self.ArcFeatureSpin.setMaximum(1000)
            self.ArcFeatureSpin.setDecimals(1)
            self.ArcFeatureSpin.setValue(self.arc_featurePitch)
            self.ArcFeatureSpinAction = self.optionsToolBar.addWidget(self.ArcFeatureSpin)
            self.ArcFeatureSpin.setToolTip("Pitch")
            self.ArcFeatureSpinAction.setEnabled(True)
        else:
            self.ArcFeatureCombo.setCurrentIndex(1)
            self.ArcFeatureSpin.setMinimum(1)
            self.ArcFeatureSpin.setMaximum(3600)
            self.ArcFeatureSpin.setDecimals(0)
            self.ArcFeatureSpin.setValue(self.arc_featureAngle)
            self.ArcFeatureSpinAction = self.optionsToolBar.addWidget(self.ArcFeatureSpin)
            self.ArcFeatureSpin.setToolTip("Angle")
            self.ArcFeatureSpinAction.setEnabled(True)            

        
        if self.arc_angleDirection == "ClockWise":
            self.ArcAngleDirectionCombo.setCurrentIndex(0)
        else:
            self.ArcAngleDirectionCombo.setCurrentIndex(1)
            
        
      
            
        
        QObject.connect(self.ArcFeatureSpin, SIGNAL("valueChanged(double)"), self.segmentsettingsArc)
        QObject.connect(self.ArcFeatureCombo, SIGNAL("currentIndexChanged(int)"), self.featureArc)
        QObject.connect(self.ArcAngleDirectionCombo, SIGNAL("currentIndexChanged(int)"), self.angleDirectionArc) 


    def polygonArc(self):
        settings = QSettings()
        if self.ArcPolygonCombo.currentText() == "pie":
            settings.setValue("/CADDigitize/arc/polygon", "pie")
        else:
            settings.setValue("/CADDigitize/arc/polygon", "chord")  

              
    def angleDirectionArc(self):
        settings = QSettings()
        if self.ArcAngleDirectionCombo.currentText() == "ClockWise":
            settings.setValue("/CADDigitize/arc/direction",  "ClockWise")
        else:
            settings.setValue("/CADDigitize/arc/direction",  "CounterClockWise")     
                
    def segmentsettingsArc(self):
        settings = QSettings()
        if self.arc_method == "pitch":
            settings.setValue("/CADDigitize/arc/segments", self.ArcFeatureSpin.value())
            settings.setValue("/CADDigitize/arc/pitch", self.ArcFeatureSpin.value())
        else:
            settings.setValue("/CADDigitize/arc/segments", int(self.ArcFeatureSpin.value()))
            settings.setValue("/CADDigitize/arc/angle", int(self.ArcFeatureSpin.value()))        
        
    def featureArc(self):
        settings = QSettings()
    
        if self.ArcFeatureCombo.currentText() == "pitch":
            self.ArcFeatureSpin.setMinimum(1)
            self.ArcFeatureSpin.setMaximum(1000)
            self.ArcFeatureSpin.setDecimals(1)
            self.ArcFeatureSpin.setValue(settings.value("/CADDigitize/arc/pitch", 2,type=float))
            self.ArcFeatureSpinAction = self.optionsToolBar.addWidget(self.ArcFeatureSpin)
            self.ArcFeatureSpin.setToolTip("Pitch")
            self.ArcFeatureSpinAction.setEnabled(True)
            self.arc_method = "pitch"
            settings.setValue("/CADDigitize/arc/method",  "pitch")
        else:
            self.ArcFeatureSpin.setMinimum(1)
            self.ArcFeatureSpin.setMaximum(3600)
            self.ArcFeatureSpin.setDecimals(0)
            self.ArcFeatureSpin.setValue(settings.value("/CADDigitize/arc/angle", 1,type=int))
            self.ArcFeatureSpinAction = self.optionsToolBar.addWidget(self.ArcFeatureSpin)
            self.ArcFeatureSpin.setToolTip("Angle")
            self.ArcFeatureSpinAction.setEnabled(True)
            self.arc_method = "angle"   
            settings.setValue("/CADDigitize/arc/method",  "angle")        
        
        
        
    #####################
    #     RPolygon      #
    #####################
   
    def segmentsettingsRPolygon(self):
        settings = QSettings()
        settings.setValue("/CADDigitize/rpolygon/nbedges", self.spinBox.value())    
        
    def rpolygonOptions(self):
        settings = QSettings()
        self.optionsToolBar.clear()
        ###
        # Options
        ###
        # Add spinbox circle
        self.spinBox = QSpinBox(self.iface.mainWindow())
        self.spinBox.setMinimum(3)
        self.spinBox.setMaximum(9999)
        segvalue = settings.value("/CADDigitize/rpolygon/nbedges",36,type=int)
        if not segvalue:
            settings.setValue("/CADDigitize/rpolygon/nbedges", 36)
        self.spinBox.setValue(segvalue)
        self.spinBox.setSingleStep(1)
        self.spinBoxAction = self.optionsToolBar.addWidget(self.spinBox)
        self.spinBox.setToolTip("Number of edges")
        self.spinBoxAction.setEnabled(True)
        
        
        QObject.connect(self.spinBox, SIGNAL("valueChanged(int)"), self.segmentsettingsRPolygon)

    #####################
    #      Circle       #
    #####################      
      
    def segmentsettingsCircle(self):
        settings = QSettings()
        settings.setValue("/CADDigitize/circle/segments", self.spinBox.value())

    def circleOptions(self):
        settings = QSettings()
        self.optionsToolBar.clear()
        ###
        # Options
        ###
        # Add spinbox circle
        self.spinBox = QSpinBox(self.iface.mainWindow())
        self.spinBox.setMinimum(3)
        self.spinBox.setMaximum(3600)
        segvalue = settings.value("/CADDigitize/circle/segments",36,type=int)
        if not segvalue:
            settings.setValue("/CADDigitize/circle/segments", 36)
        self.spinBox.setValue(segvalue)
        self.spinBox.setSingleStep(1)
        self.spinBoxAction = self.optionsToolBar.addWidget(self.spinBox)
        self.spinBox.setToolTip("Number of quadrant segments")
        self.spinBoxAction.setEnabled(True)
        
        
        QObject.connect(self.spinBox, SIGNAL("valueChanged(int)"), self.segmentsettingsCircle)

    #####################
    #      Ellipse      #
    #####################

    def segmentsettingsEllipse(self):
        settings = QSettings()
        settings.setValue("/CADDigitize/ellipse/segments", self.spinBox.value()) 
        
    def ellipseOptions(self):
        settings = QSettings()
        self.optionsToolBar.clear()
        ###
        # Options
        ###
        # Add spinbox circle
        self.spinBox = QSpinBox(self.iface.mainWindow())
        self.spinBox.setMinimum(4)
        self.spinBox.setMaximum(3600)
        segvalue = settings.value("/CADDigitize/ellipse/segments",36,type=int)
        if not segvalue:
            settings.setValue("/CADDigitize/ellipse/segments", 36)
        self.spinBox.setValue(segvalue)
        self.spinBox.setSingleStep(1)
        self.spinBoxAction = self.optionsToolBar.addWidget(self.spinBox)
        self.spinBox.setToolTip("Number of points")
        self.spinBoxAction.setEnabled(True)
        
        
        QObject.connect(self.spinBox, SIGNAL("valueChanged(int)"), self.segmentsettingsEllipse)

    #####################
    #       Rect        #
    #####################  
                  
    def rectOptions(self):
        self.optionsToolBar.clear()        



#####################################################################################################
#                                                                                                   #
#                                                                                                   #
#                                         FUNCTIONS                                                 #
#                                                                                                   #
#                                                                                                   #
#####################################################################################################
    
    def circleBy2PointsDigit(self):
        self.circleOptions()
        self.circleToolButton.setDefaultAction(self.circleBy2Points)
        self.canvas.setMapTool(self.circleBy2Points_tool)
        self.circleBy2Points.setChecked(True)
        QObject.connect(self.circleBy2Points_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def circleBy3PointsDigit(self):
        self.circleOptions()
        self.circleToolButton.setDefaultAction(self.circleBy3Points)
        self.canvas.setMapTool(self.circleBy3Points_tool)
        self.circleBy3Points.setChecked(True)
        QObject.connect(self.circleBy3Points_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def circleByCenterRadiusDigit(self):
        self.circleOptions()
        self.circleToolButton.setDefaultAction(self.circleByCenterRadius)
        self.canvas.setMapTool(self.circleByCenterRadius_tool)
        self.circleByCenterRadius.setChecked(True)
        QObject.connect(self.circleByCenterRadius_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def circleByCenterPointDigit(self):
        self.circleOptions()
        self.circleToolButton.setDefaultAction(self.circleByCenterPoint)
        self.canvas.setMapTool(self.circleByCenterPoint_tool)
        self.circleByCenterPoint.setChecked(True)
        QObject.connect(self.circleByCenterPoint_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def rectBy3PointsDigit(self):
        self.rectOptions()
        self.rectToolButton.setDefaultAction(self.rectBy3Points)
        self.canvas.setMapTool(self.rectBy3Points_tool)
        self.rectBy3Points.setChecked(True)
        QObject.connect(self.rectBy3Points_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def rectByExtentDigit(self):
        self.rectOptions()
        self.rectToolButton.setDefaultAction(self.rectByExtent)
        self.canvas.setMapTool(self.rectByExtent_tool)
        self.rectByExtent.setChecked(True)
        QObject.connect(self.rectByExtent_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def rectFromCenterDigit(self):
        self.rectOptions()
        self.rectToolButton.setDefaultAction(self.rectFromCenter)
        self.canvas.setMapTool(self.rectFromCenter_tool)
        self.rectFromCenter.setChecked(True)
        QObject.connect(self.rectFromCenter_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def squareFromCenterDigit(self):
        self.rectOptions()
        self.rectToolButton.setDefaultAction(self.squareFromCenter)
        self.canvas.setMapTool(self.squareFromCenter_tool)
        self.squareFromCenter.setChecked(True)
        QObject.connect(self.squareFromCenter_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def ellipseByCenter2PointsDigit(self):
        self.ellipseOptions()
        self.ellipseToolButton.setDefaultAction(self.ellipseByCenter2Points)
        self.canvas.setMapTool(self.ellipseByCenter2Points_tool)
        self.ellipseByCenter2Points.setChecked(True)
        QObject.connect(self.ellipseByCenter2Points_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def ellipseByCenter3PointsDigit(self):
        self.ellipseOptions()
        self.ellipseToolButton.setDefaultAction(self.ellipseByCenter3Points)
        self.canvas.setMapTool(self.ellipseByCenter3Points_tool)
        self.ellipseByCenter3Points.setChecked(True)
        QObject.connect(self.ellipseByCenter3Points_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def ellipseBy4PointsDigit(self):
        self.ellipseOptions()
        self.ellipseToolButton.setDefaultAction(self.ellipseBy4Points)
        self.canvas.setMapTool(self.ellipseBy4Points_tool)
        self.ellipseBy4Points.setChecked(True)
        QObject.connect(self.ellipseBy4Points_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def ellipseByFociPointDigit(self):
        self.ellipseOptions()
        self.ellipseToolButton.setDefaultAction(self.ellipseByFociPoint)
        self.canvas.setMapTool(self.ellipseByFociPoint_tool)
        self.ellipseByFociPoint.setChecked(True)
        QObject.connect(self.ellipseByFociPoint_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def ellipseFromCenterDigit(self):
        self.ellipseOptions()
        self.ellipseToolButton.setDefaultAction(self.ellipseFromCenter)
        self.canvas.setMapTool(self.ellipseFromCenter_tool)
        self.ellipseFromCenter.setChecked(True)
        QObject.connect(self.ellipseFromCenter_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def ellipseByExtentDigit(self):
        self.ellipseOptions()
        self.ellipseToolButton.setDefaultAction(self.ellipseByExtent)
        self.canvas.setMapTool(self.ellipseByExtent_tool)
        self.ellipseByExtent.setChecked(True)
        QObject.connect(self.ellipseByExtent_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)

    def arcByCenter2PointsDigit(self):
        self.arcOptions()
        self.arcToolButton.setDefaultAction(self.arcByCenter2Points)
        self.canvas.setMapTool(self.arcByCenter2Points_tool)
        self.arcByCenter2Points.setChecked(True)
        QObject.connect(self.arcByCenter2Points_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.arcFeature)
        
    def arcBy3PointsDigit(self):
        self.arcOptions()
        self.arcToolButton.setDefaultAction(self.arcBy3Points)
        self.canvas.setMapTool(self.arcBy3Points_tool)
        self.arcBy3Points.setChecked(True)
        QObject.connect(self.arcBy3Points_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.arcFeature)

    def arcByCenterPointAngleDigit(self):
        self.arcOptions()
        self.arcToolButton.setDefaultAction(self.arcByCenterPointAngle)
        self.canvas.setMapTool(self.arcByCenterPointAngle_tool)
        self.arcByCenterPointAngle.setChecked(True)
        QObject.connect(self.arcByCenterPointAngle_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.arcFeature)


    def rpolygonByCenterPointDigit(self):
        self.rpolygonOptions()
        self.rpolygonToolButton.setDefaultAction(self.rpolygonByCenterPoint)
        self.canvas.setMapTool(self.rpolygonByCenterPoint_tool)
        self.rpolygonByCenterPoint.setChecked(True)
        QObject.connect(self.rpolygonByCenterPoint_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        
    def rpolygonBy2CornersDigit(self):
        self.rpolygonOptions()
        self.rpolygonToolButton.setDefaultAction(self.rpolygonBy2Corners)
        self.canvas.setMapTool(self.rpolygonBy2Corners_tool)
        self.rpolygonBy2Corners.setChecked(True)
        QObject.connect(self.rpolygonBy2Corners_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)        
        
    def doHelp(self):
        help_file = "file:///"+ self.plugin_dir + "/help/index.html"
        QDesktopServices.openUrl(QUrl(help_file))
        
    def doSettings(self):
        self.optionsToolBar.clear()
        self.settings = Ui_CADDigitizeSettings()
        self.settings.show()

    def toggle(self):
        self.optionsToolBar.clear()
        mc = self.canvas
        layer = mc.currentLayer()
        #Decide whether the plugin button/menu is enabled or disabled
        if layer <> None:
            if (layer.isEditable() and (layer.geometryType() == 2 or layer.geometryType() == 1)):
                self.circleBy2Points.setEnabled(True)
                self.circleBy3Points.setEnabled(True)
                self.circleByCenterRadius.setEnabled(True)
                self.circleByCenterPoint.setEnabled(True)
                self.rectBy3Points.setEnabled(True)
                self.rectByExtent.setEnabled(True)
                self.rectFromCenter.setEnabled(True)
                self.squareFromCenter.setEnabled(True)
                self.ellipseByCenter2Points.setEnabled(True)
                self.ellipseByCenter3Points.setEnabled(True)
                self.ellipseBy4Points.setEnabled(True)
                self.ellipseByFociPoint.setEnabled(True)
                self.ellipseFromCenter.setEnabled(True)
                self.ellipseByExtent.setEnabled(True)
                self.arcByCenter2Points.setEnabled(True)
                self.arcBy3Points.setEnabled(True)
                self.arcByCenterPointAngle.setEnabled(True)
                self.rpolygonByCenterPoint.setEnabled(True)
                self.rpolygonBy2Corners.setEnabled(True)
                
                QObject.connect(layer,SIGNAL("editingStopped()"),self.toggle)
                QObject.disconnect(layer,SIGNAL("editingStarted()"),self.toggle)
            else:
                self.circleBy2Points.setEnabled(False)
                self.circleBy3Points.setEnabled(False)
                self.circleByCenterRadius.setEnabled(False)
                self.circleByCenterPoint.setEnabled(False)
                self.rectBy3Points.setEnabled(False)
                self.rectByExtent.setEnabled(False)
                self.rectFromCenter.setEnabled(False)
                self.squareFromCenter.setEnabled(False)
                self.ellipseByCenter2Points.setEnabled(False)
                self.ellipseByCenter3Points.setEnabled(False)
                self.ellipseBy4Points.setEnabled(False)
                self.ellipseByFociPoint.setEnabled(False)
                self.ellipseFromCenter.setEnabled(False)
                self.ellipseByExtent.setEnabled(False)
                self.arcByCenter2Points.setEnabled(False)
                self.arcBy3Points.setEnabled(False)
                self.arcByCenterPointAngle.setEnabled(False)
                self.rpolygonByCenterPoint.setEnabled(False)
                self.rpolygonBy2Corners.setEnabled(False)

                QObject.connect(layer,SIGNAL("editingStarted()"),self.toggle)
                QObject.disconnect(layer,SIGNAL("editingStopped()"),self.toggle)



    def deactivate(self):
        self.circleBy2Points.setChecked(False)
        self.circleBy3Points.setChecked(False)
        self.circleByCenterRadius.setChecked(False)
        self.circleByCenterPoint.setChecked(False)
        self.rectBy3Points.setChecked(False)
        self.rectByExtent.setChecked(False)
        self.rectFromCenter.setChecked(False)
        self.squareFromCenter.setChecked(False)
        self.ellipseByCenter2Points.setChecked(False)
        self.ellipseByCenter3Points.setChecked(False)
        self.ellipseBy4Points.setChecked(False)
        self.ellipseByFociPoint.setChecked(False)
        self.ellipseFromCenter.setChecked(False)
        self.ellipseByExtent.setChecked(False)
        self.arcByCenter2Points.setChecked(False)
        self.arcBy3Points.setChecked(False)
        self.arcByCenterPointAngle.setChecked(False)
        self.rpolygonByCenterPoint.setChecked(False)
        self.rpolygonBy2Corners.setChecked(False)
        
        QObject.disconnect(self.circleBy2Points_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.circleBy2Points_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.circleByCenterRadius_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.circleByCenterPoint_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.rectBy3Points_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.rectByExtent_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.rectFromCenter_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.squareFromCenter_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.ellipseByCenter2Points_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.ellipseByCenter3Points_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.ellipseBy4Points_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.ellipseByFociPoint_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.ellipseFromCenter_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.ellipseByExtent_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.arcByCenter2Points_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.arcFeature)
        QObject.disconnect(self.arcBy3Points_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.arcFeature)
        QObject.disconnect(self.arcByCenterPointAngle_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.arcFeature)
        QObject.disconnect(self.rpolygonByCenterPoint_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.rpolygonBy2Corners_tool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)


    def arcFeature(self, arc):
        geom = arc[0]
        center = arc[1]
        mc = self.canvas
        layer = mc.currentLayer()
        if layer.geometryType() == 2:
            arcPolygonSettings = QSettings()
            
            if arcPolygonSettings.value("/CADDigitize/arc/polygon","chord") == "pie":
                geom.insertVertex(center.x(), center.y(),0)
                
            geom = geom.convertToType(2, False)
        
        self.createFeature(geom)
            
    def createFeature(self, geom):
        settings = QSettings()
        mc = self.canvas
        layer = mc.currentLayer()
        renderer = mc.mapSettings()
        layerCRSSrsid = layer.crs().srsid()
        projectCRSSrsid = renderer.destinationCrs().srsid()
        provider = layer.dataProvider()
        f = QgsFeature()


        #On the Fly reprojection.
        if layerCRSSrsid != projectCRSSrsid:
            geom.transform(QgsCoordinateTransform(projectCRSSrsid, layerCRSSrsid))

        # Line or Polygon
        if layer.geometryType() == 2:
            f.setGeometry(geom)
        else:
            f.setGeometry(geom.convertToType(1, False))

        # add attribute fields to feature
        fields = layer.pendingFields()
        
        # vector api change update
        f.initAttributes(fields.count())
        for i in range(fields.count()):
            f.setAttribute(i,provider.defaultValue(i))
            
        disable_attributes = settings.value( "/qgis/digitizing/disable_enter_attribute_values_dialog", False, type=bool)

        if disable_attributes:
            cancel = 1
        else:
            dlg = QgsAttributeDialog(layer, f, False)
            dlg.setIsAddDialog(True)
            if not dlg.dialog().exec_():
                cancel = 0
            else:
                layer.destroyEditCommand()
                cancel = 1

        if cancel == 1:
            layer.addFeature(f)
            layer.endEditCommand()
            
        mc.refresh()
        
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
        self.circleToolButton.removeAction(self.circleBy2Points)
        self.circleToolButton.removeAction(self.circleBy3Points)
        self.circleToolButton.removeAction(self.circleByCenterRadius)
        self.circleToolButton.removeAction(self.circleByCenterPoint)
        self.rectToolButton.removeAction(self.rectBy3Points)
        self.rectToolButton.removeAction(self.rectByExtent)
        self.rectToolButton.removeAction(self.rectFromCenter)
        self.rectToolButton.removeAction(self.squareFromCenter)
        self.ellipseToolButton.removeAction(self.ellipseByCenter2Points)
        self.ellipseToolButton.removeAction(self.ellipseByCenter3Points)
        self.ellipseToolButton.removeAction(self.ellipseBy4Points)
        self.ellipseToolButton.removeAction(self.ellipseByFociPoint)
        self.ellipseToolButton.removeAction(self.ellipseFromCenter)
        self.ellipseToolButton.removeAction(self.ellipseByExtent)
        self.arcToolButton.removeAction(self.arcByCenter2Points)
        self.arcToolButton.removeAction(self.arcBy3Points)
        self.arcToolButton.removeAction(self.arcByCenterPointAngle)
        self.rpolygonToolButton.removeAction(self.rpolygonByCenterPoint)
        self.rpolygonToolButton.removeAction(self.rpolygonBy2Corners)
        self.optionsToolBar.clear()
                
        del self.circleToolButton
        del self.rectToolButton
        del self.ellipseToolButton
        del self.arcToolButton
        del self.rpolygonToolButton
        del self.toolBar
        del self.optionsToolBar
        del self.menu


